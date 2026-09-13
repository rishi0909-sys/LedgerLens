export type CaseStatus = 
  | 'NEW' 
  | 'SCREENED' 
  | 'QUEUED' 
  | 'SELECTED' 
  | 'INVESTIGATING' 
  | 'EVIDENCE_REVIEW' 
  | 'CONFIRMED_FRAUD'
  | 'FALSE_POSITIVE'
  | 'ASSET_FROZEN'
  | 'CLOSED';

export interface InvestigationEvent {
  id: string;
  timestamp: string;
  type: 'STATUS_CHANGE' | 'NOTE_ADDED' | 'SYSTEM_ALERT' | 'COPILOT_SUGGESTION' | 'DOCUMENT_ANALYZED';
  actor: 'SYSTEM' | 'INVESTIGATOR' | 'COPILOT';
  description: string;
  metadata?: Record<string, any>;
}

export interface CaseNote {
  id: string;
  timestamp: string;
  author: string;
  content: string;
}

export interface DocumentAnalysisState {
  isAnalyzed: boolean;
  isAnalyzing: boolean;
  progress: {
    ocr: number;
    extraction: number;
    finbert: number;
    reconciliation: number;
  };
}

export interface CandidateCase {
  transaction_id: string;
  fused_score: number;
  cal_tx: number;
  cal_doc: number;
  cal_seq: number;
  cal_graph: number;
  conflict_tx_doc: number;
  conflict_tx_seq: number;
  tx_available: number;
  doc_available: number;
  seq_available: number;
  graph_available: number;
  investigated: boolean;
  
  // Phase 9 Additions
  status: CaseStatus;
  events: InvestigationEvent[];
  notes: CaseNote[];
  document_analysis: DocumentAnalysisState;
  rl_decision_summary?: string;
}

export interface CandidateQueueResponse {
  window_id: string;
  candidates: CandidateCase[];
}

export interface InvestigationRequest {
  candidates: CandidateCase[];
  remaining_budget: number;
  budget_limit: number;
  cumulative_discoveries: number;
}

export interface AgentRecommendation {
  transaction_id: string;
  index: number;
  confidence: number;
  reasoning: string;
}

export interface InvestigationResponse {
  recommendations: AgentRecommendation[];
  model_id: string;
  decision_summary?: string;
}

export type ProcessingState = 
  | 'idle'
  | 'loading'
  | 'transaction-analysis'
  | 'sequence-analysis'
  | 'graph-analysis'
  | 'document-analysis'
  | 'fusion-analysis'
  | 'rl-decision'
  | 'complete';
