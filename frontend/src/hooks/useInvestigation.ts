import { useReducer, useEffect } from 'react';
import type { CandidateCase, ProcessingState, CaseStatus } from '../types';
import { fetchCandidateQueue, askRLAgent, updateCaseStatus, runDocumentAnalysis, addNoteToCase, setDemoMode } from '../services/api';

interface State {
  candidates: CandidateCase[];
  windowId: string;
  selectedCandidate: CandidateCase | null;
  budget: number;
  discoveries: number;
  processingState: ProcessingState;
  isLoading: boolean;
  error: string | null;
  mode: 'LIVE' | 'DEMO';
  agentRecommendations: any[] | null;
  fundsProtected: number;
  chatHistory: Array<{id: string; sender: 'agent' | 'user'; text: string; timestamp: string}>;
  isTraining: boolean;
}

type Action =
  | { type: 'INIT_START' }
  | { type: 'INIT_SUCCESS'; payload: { candidates: CandidateCase[]; windowId: string } }
  | { type: 'INIT_ERROR'; payload: string }
  | { type: 'SELECT_CASE'; payload: CandidateCase }
  | { type: 'INVESTIGATE_COMPLETE' }
  | { type: 'SET_PROCESSING_STATE'; payload: ProcessingState }
  | { type: 'TOGGLE_MODE'; payload: 'LIVE' | 'DEMO' }
  | { type: 'SET_AGENT_RECOMMENDATIONS'; payload: any[] | null }
  | { type: 'CLEAR_RECOMMENDATIONS' }
  | { type: 'UPDATE_CASE_IN_STATE'; payload: CandidateCase }
  | { type: 'FREEZE_ASSET'; payload: number }
  | { type: 'ADD_CHAT_MESSAGE'; payload: {id: string; sender: 'agent' | 'user'; text: string; timestamp: string} }
  | { type: 'SET_TRAINING_STATE'; payload: boolean };

const initialState: State = {
  candidates: [],
  windowId: '',
  selectedCandidate: null,
  budget: 5,
  discoveries: 0,
  processingState: 'idle',
  isLoading: true,
  error: null,
  mode: 'LIVE',
  agentRecommendations: null,
  fundsProtected: 0,
  chatHistory: [],
  isTraining: false
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'INIT_START':
      return { ...state, isLoading: true, error: null };
    case 'INIT_SUCCESS':
      return { 
        ...state, 
        isLoading: false, 
        candidates: action.payload.candidates, 
        windowId: action.payload.windowId,
        agentRecommendations: null
      };
    case 'INIT_ERROR':
      return { ...state, isLoading: false, error: action.payload };
    case 'SELECT_CASE':
      return { ...state, selectedCandidate: action.payload };
    case 'SET_PROCESSING_STATE':
      return { ...state, processingState: action.payload };
    case 'TOGGLE_MODE':
      return { ...state, mode: action.payload };
    case 'SET_AGENT_RECOMMENDATIONS':
      return { ...state, agentRecommendations: action.payload };
    case 'CLEAR_RECOMMENDATIONS':
      return { ...state, agentRecommendations: null };
    case 'UPDATE_CASE_IN_STATE':
      return {
        ...state,
        candidates: state.candidates.map(c => c.transaction_id === action.payload.transaction_id ? action.payload : c),
        selectedCandidate: state.selectedCandidate?.transaction_id === action.payload.transaction_id ? action.payload : state.selectedCandidate
      };
    case 'FREEZE_ASSET':
      return {
        ...state,
        fundsProtected: state.fundsProtected + action.payload,
        budget: state.budget - 1, // Deduct budget when a case is successfully frozen
        discoveries: state.discoveries + 1
      };
    case 'INVESTIGATE_COMPLETE': {
      // Legacy, replaced by manual status updates + Freeze Asset
      return state;
    }
    case 'ADD_CHAT_MESSAGE':
      return { ...state, chatHistory: [...state.chatHistory, action.payload] };
    case 'SET_TRAINING_STATE':
      return { ...state, isTraining: action.payload };
    default:
      return state;
  }
}

export function useInvestigation() {
  const [state, dispatch] = useReducer(reducer, initialState as State);

  const loadQueue = async () => {
    dispatch({ type: 'INIT_START' });
    try {
      const data = await fetchCandidateQueue();
      dispatch({ type: 'INIT_SUCCESS', payload: { candidates: data.candidates, windowId: data.window_id } });
    } catch (err) {
      dispatch({ type: 'INIT_ERROR', payload: 'Failed to fetch candidate queue.' });
    }
  };

  useEffect(() => {
    loadQueue();
  }, [state.mode]);

  const selectCase = async (candidate: CandidateCase) => {
    dispatch({ type: 'SELECT_CASE', payload: candidate });
    if (candidate.status === 'QUEUED') {
      await updateCaseStatus(candidate.transaction_id, 'SELECTED', 'Investigator selected case from queue.');
      loadQueue(); // Refresh to get the audit trail update
    }
  };

  const completeInvestigation = async () => {
    // Legacy support
    dispatch({ type: 'INVESTIGATE_COMPLETE' });
  };

  const freezeAsset = async (amount: number) => {
    if (!state.selectedCandidate) return;
    await updateCaseStatusManual('ASSET_FROZEN', `Asset frozen. ₹${amount.toLocaleString()} recovered.`);
    dispatch({ type: 'FREEZE_ASSET', payload: amount });
    dispatch({ type: 'SELECT_CASE', payload: null as any }); // Clear selection to return to Command Center
  };

  const triggerDocumentAnalysis = async () => {
    if (!state.selectedCandidate) return;
    
    // Update local state to show analyzing
    const analyzingCase = { ...state.selectedCandidate, document_analysis: { ...state.selectedCandidate.document_analysis, isAnalyzing: true } };
    dispatch({ type: 'UPDATE_CASE_IN_STATE', payload: analyzingCase });
    
    await runDocumentAnalysis(state.selectedCandidate.transaction_id, (progress) => {
      // Intentionally not strictly dispatching every tick to avoid overwhelming React renders if needed, 
      // but for UX we can update the specific case in state
      dispatch({ 
        type: 'UPDATE_CASE_IN_STATE', 
        payload: { 
          ...analyzingCase, 
          document_analysis: { isAnalyzed: false, isAnalyzing: true, progress } 
        } 
      });
    });
    
    // Refresh to get full updated state from repo
    loadQueue();
    // Re-select to update the detail view
    const refreshed = await fetchCandidateQueue();
    const updated = refreshed.candidates.find(c => c.transaction_id === state.selectedCandidate?.transaction_id);
    if(updated) {
       dispatch({ type: 'SELECT_CASE', payload: updated });
       dispatch({ type: 'SET_AGENT_RECOMMENDATIONS', payload: state.agentRecommendations }); // Preserve summary
    }
  };

  const runRLProcessingStateMachine = async () => {
    if (state.budget <= 0) return;

    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'loading' });
    await delay(300);
    
    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'transaction-analysis' });
    await delay(400);

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'sequence-analysis' });
    await delay(400);

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'graph-analysis' });
    await delay(400);

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'document-analysis' });
    await delay(400);

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'fusion-analysis' });
    await delay(300);

    dispatch({ type: 'SET_PROCESSING_STATE', payload: 'rl-decision' });
    
    try {
      const response = await askRLAgent({
        candidates: state.candidates,
        remaining_budget: state.budget,
        budget_limit: 5,
        cumulative_discoveries: state.discoveries
      });
      
      await delay(400);
      
      const bestRecommendation = response.recommendations[0];
      const selected = state.candidates.find(c => c.transaction_id === bestRecommendation.transaction_id) || state.candidates[0];
      
      dispatch({ type: 'SET_PROCESSING_STATE', payload: 'complete' });
      dispatch({ type: 'SET_AGENT_RECOMMENDATIONS', payload: response.recommendations });
      dispatch({ type: 'SELECT_CASE', payload: selected });
      
      await updateCaseStatus(selected.transaction_id, 'INVESTIGATING', 'RL Agent prioritized and selected this case for investigation.');
      loadQueue();
      
      // Post agent explanation to chat
      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: {
        id: crypto.randomUUID(),
        sender: 'agent',
        text: `I prioritized case ${bestRecommendation.transaction_id}. ${bestRecommendation.reasoning.split('\n\n')[1]}`,
        timestamp: new Date().toISOString()
      }});

      await delay(300);
      dispatch({ type: 'SET_PROCESSING_STATE', payload: 'idle' });
      
    } catch (err) {
      console.error(err);
      dispatch({ type: 'SET_PROCESSING_STATE', payload: 'idle' });
    }
  };

  const updateCaseStatusManual = async (status: CaseStatus, description: string) => {
    if (!state.selectedCandidate) return;
    await updateCaseStatus(state.selectedCandidate.transaction_id, status, description);
    
    // Refresh to get full updated state from repo
    await loadQueue();
    // Re-select to update the detail view
    const refreshed = await fetchCandidateQueue();
    const updated = refreshed.candidates.find(c => c.transaction_id === state.selectedCandidate?.transaction_id);
    if (updated) {
       dispatch({ type: 'SELECT_CASE', payload: updated });
    }
  };

  const addNote = async (content: string) => {
    if (!state.selectedCandidate) return;
    await addNoteToCase(state.selectedCandidate.transaction_id, content, 'Investigator');
    
    await loadQueue();
    const refreshed = await fetchCandidateQueue();
    const updated = refreshed.candidates.find(c => c.transaction_id === state.selectedCandidate?.transaction_id);
    if (updated) {
       dispatch({ type: 'SELECT_CASE', payload: updated });
    }
  };

  const clearRecommendations = () => {
    dispatch({ type: 'CLEAR_RECOMMENDATIONS' });
  };

  const sendFeedback = async (text: string, isPositive: boolean) => {
    dispatch({ type: 'ADD_CHAT_MESSAGE', payload: {
      id: crypto.randomUUID(),
      sender: 'user',
      text: `${isPositive ? '👍' : '👎'} ${text}`,
      timestamp: new Date().toISOString()
    }});
    
    dispatch({ type: 'SET_TRAINING_STATE', payload: true });
    
    // Simulate backend storing structured offline dataset event
    await new Promise(res => setTimeout(res, 1500));
    
    dispatch({ type: 'ADD_CHAT_MESSAGE', payload: {
      id: crypto.randomUUID(),
      sender: 'agent',
      text: 'Thank you. I have structured this human-in-the-loop preference into the feedback repository for future offline PPO retraining.',
      timestamp: new Date().toISOString()
    }});
    
    dispatch({ type: 'SET_TRAINING_STATE', payload: false });
  };

  const toggleMode = () => {
    const newMode = state.mode === 'LIVE' ? 'DEMO' : 'LIVE';
    setDemoMode(newMode === 'DEMO');
    dispatch({ type: 'TOGGLE_MODE', payload: newMode });
  };

  return {
    state,
    selectCase,
    runRLProcessingStateMachine,
    completeInvestigation,
    updateCaseStatusManual,
    addNote,
    triggerDocumentAnalysis,
    loadQueue,
    clearRecommendations,
    toggleMode,
    freezeAsset,
    sendFeedback
  };
}
