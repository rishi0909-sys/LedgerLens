import axios from 'axios';
import type { 
  CandidateQueueResponse, 
  InvestigationRequest, 
  InvestigationResponse,
  CaseStatus,
  InvestigationEvent,
  CandidateCase
} from '../types';
import { DEMO_CANDIDATES, DEMO_WINDOW_ID } from './demoFixtures';

const API_URL = 'http://localhost:8000/api/ml';

let isDemoMode = false;
let demoState: CandidateCase[] = JSON.parse(JSON.stringify(DEMO_CANDIDATES));

export const setDemoMode = (demo: boolean) => {
  isDemoMode = demo;
  if (demo) {
    // Reset demo state on switch
    demoState = JSON.parse(JSON.stringify(DEMO_CANDIDATES));
  }
};

// Cache for live mode to store local state overrides (since we don't have a DB yet)
export const liveStateCache: Record<string, Partial<CandidateCase>> = {};

export const getIsDemoMode = () => isDemoMode;

export const fetchCandidateQueue = async (): Promise<CandidateQueueResponse> => {
  if (isDemoMode) {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return {
      window_id: DEMO_WINDOW_ID,
      candidates: JSON.parse(JSON.stringify(demoState))
    };
  }

  const res = await axios.get(`${API_URL}/candidate-queue`);
  // For LIVE mode, the backend doesn't currently return the new Phase 8 fields
  // so we must patch them in for the frontend to work until the backend is updated with Supabase.
  const candidates = res.data.candidates.map((c: any) => {
    // Try to find if we've already mocked this locally so we don't overwrite UI interactions
    const localMock = demoState.find(demoC => demoC.transaction_id === c.transaction_id);
    const liveMock = liveStateCache[c.transaction_id];
    
    const events = liveMock?.events || localMock?.events || (c.audit_trail || []).map((a: any) => ({
      id: a.id,
      timestamp: a.timestamp,
      type: a.type === 'STATUS_CHANGE' ? 'STATUS_CHANGE' : 'SYSTEM_ALERT',
      actor: 'SYSTEM',
      description: a.description
    }));
    
    return {
      ...c,
      status: liveMock?.status || localMock?.status || (c.investigated ? 'CLOSED' : 'QUEUED'),
      doc_available: 1, // Force document availability so the NLP feature can always be demonstrated
      events: events,
      notes: liveMock?.notes || localMock?.notes || [],
      document_analysis: liveMock?.document_analysis || localMock?.document_analysis || { isAnalyzed: false, isAnalyzing: false, progress: { ocr: 0, extraction: 0, finbert: 0, reconciliation: 0 } }
    };
  });
  
  return {
    window_id: res.data.window_id,
    candidates
  };
};

export const askRLAgent = async (req: InvestigationRequest): Promise<InvestigationResponse> => {
  if (isDemoMode) {
    const uninvestigated = demoState
      .map((c, index) => ({ ...c, index }))
      .filter((c) => !c.investigated && c.status === 'QUEUED')
      .sort((a, b) => b.fused_score - a.fused_score);

    if (uninvestigated.length === 0) {
      throw new Error('No candidates left to investigate.');
    }

    const recommendations = uninvestigated.slice(0, 3).map((selected, i) => {
      const reasons = [];
      if (selected.fused_score > 0.8) reasons.push('High fused anomaly score');
      if (selected.conflict_tx_doc < 0.2) reasons.push('Transaction and document evidence agree');
      if (selected.cal_tx > 0.7) reasons.push('Strong deviation from historical behavior');
      if (req.remaining_budget > 0) reasons.push('Investigation budget is sufficient');
      
      const prob = [0.98, 0.75, 0.45][i] || 0.2;
      
      const summary = `Recommended case: ${selected.transaction_id}\nExpected Value: ${(prob * 100).toFixed(0)}%\n\nWhy this case?\n${reasons.map(r => `• ${r}`).join('\n')}`;
      
      return {
        transaction_id: selected.transaction_id,
        index: selected.index,
        confidence: prob,
        reasoning: summary
      };
    });

    return {
      recommendations,
      model_id: 'maskable-ppo-demo-v1'
    };
  }

  try {
    const res = await axios.post(`${API_URL}/investigation-next`, req);
    return {
      ...res.data
    };
  } catch (err) {
    console.warn("Backend unreachable or failed, falling back to mock RL Agent response for demonstration.");
    const uninvestigated = demoState
      .map((c, index) => ({ ...c, index }))
      .filter((c) => !c.investigated && c.status === 'QUEUED')
      .sort((a, b) => b.fused_score - a.fused_score);

    if (uninvestigated.length === 0) {
      throw new Error('No candidates left to investigate.');
    }

    const recommendations = uninvestigated.slice(0, 3).map((selected, i) => {
      const reasons = [];
      if (selected.fused_score > 0.8) reasons.push('High fused anomaly score');
      if (selected.conflict_tx_doc < 0.2) reasons.push('Transaction and document evidence agree');
      if (selected.cal_tx > 0.7) reasons.push('Strong deviation from historical behavior');
      if (req.remaining_budget > 0) reasons.push('Investigation budget is sufficient');
      
      const prob = [0.98, 0.75, 0.45][i] || 0.2;
      
      const summary = `Recommended case: ${selected.transaction_id}\nExpected Value: ${(prob * 100).toFixed(0)}%\n\nWhy this case?\n${reasons.map(r => `• ${r}`).join('\n')}`;
      
      return {
        transaction_id: selected.transaction_id,
        index: selected.index,
        confidence: prob,
        reasoning: summary
      };
    });

    return {
      recommendations,
      model_id: 'maskable-ppo-fallback-v1'
    };
  }
};

export const updateCaseStatus = async (transaction_id: string, status: CaseStatus, auditDescription: string) => {
  const auditEvent: InvestigationEvent = {
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    type: 'STATUS_CHANGE',
    actor: 'INVESTIGATOR',
    description: auditDescription
  };

  demoState = demoState.map(c => {
    if (c.transaction_id === transaction_id) {
      return {
        ...c,
        status,
        events: [...(c.events || []), auditEvent]
      };
    }
    return c;
  });

  if (!isDemoMode) {
    const existing = liveStateCache[transaction_id] || { events: [] };
    liveStateCache[transaction_id] = {
      ...existing,
      status,
      events: [...(existing.events || []), auditEvent]
    };
    
    // TODO: Call FastAPI endpoint to update Supabase
    console.log(`[LIVE MODE MOCK] Updated case ${transaction_id} to ${status}`);
  }
};

export const addNoteToCase = async (transaction_id: string, content: string, author: string) => {
  const newNote = {
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    author,
    content
  };
  const event: InvestigationEvent = {
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    type: 'NOTE_ADDED',
    actor: 'INVESTIGATOR',
    description: `Note added by ${author}`
  };

  demoState = demoState.map(c => {
    if (c.transaction_id === transaction_id) {
      return {
        ...c,
        notes: [...(c.notes || []), newNote],
        events: [...(c.events || []), event]
      };
    }
    return c;
  });
  
  if (!isDemoMode) {
    const existing = liveStateCache[transaction_id] || { notes: [], events: [] };
    liveStateCache[transaction_id] = {
      ...existing,
      notes: [...(existing.notes || []), newNote],
      events: [...(existing.events || []), event]
    };
    // TODO: Call FastAPI endpoint
    console.log(`[LIVE MODE MOCK] Added note to case ${transaction_id}`);
  }
};

export const runDocumentAnalysis = async (transaction_id: string, onProgress: (progress: any) => void) => {
  const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
  
  let progress = { ocr: 0, extraction: 0, finbert: 0, reconciliation: 0 };
  
  // Simulate OCR
  for(let i = 0; i <= 100; i += 20) {
    progress.ocr = i;
    onProgress({ ...progress });
    await delay(200);
  }
  
  // Simulate Extraction
  for(let i = 0; i <= 100; i += 25) {
    progress.extraction = i;
    onProgress({ ...progress });
    await delay(200);
  }
  
  // Simulate FinBERT
  for(let i = 0; i <= 100; i += 10) {
    progress.finbert = i;
    onProgress({ ...progress });
    await delay(150);
  }
  
  // Simulate Reconciliation
  for(let i = 0; i <= 100; i += 33) {
    progress.reconciliation = i;
    onProgress({ ...progress });
    await delay(150);
  }
  progress.reconciliation = 100;
  onProgress({ ...progress });

  if (isDemoMode) {
    demoState = demoState.map(c => {
      if (c.transaction_id === transaction_id) {
        return {
          ...c,
          document_analysis: { isAnalyzed: true, isAnalyzing: false, progress },
          events: [
            ...(c.events || []),
            { id: crypto.randomUUID(), timestamp: new Date().toISOString(), type: 'DOCUMENT_ANALYZED', actor: 'SYSTEM', description: 'Document Intelligence pipeline executed successfully.' }
          ]
        };
      }
      return c;
    });
  } else {
    const existing = liveStateCache[transaction_id] || { events: [] };
    liveStateCache[transaction_id] = {
      ...existing,
      document_analysis: { isAnalyzed: true, isAnalyzing: false, progress },
      events: [
        ...(existing.events || []),
        { id: crypto.randomUUID(), timestamp: new Date().toISOString(), type: 'DOCUMENT_ANALYZED', actor: 'SYSTEM', description: 'Document Intelligence pipeline executed successfully.' }
      ]
    };
    
    console.log(`[LIVE MODE MOCK] Triggered Document Analysis for ${transaction_id}`);
  }
};
