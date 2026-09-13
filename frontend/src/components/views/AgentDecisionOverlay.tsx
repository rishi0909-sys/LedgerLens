import { useState, useEffect } from 'react';
import { BrainCircuit, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import type { ProcessingState, AgentRecommendation } from '../../types';

interface AgentDecisionOverlayProps {
  state: ProcessingState;
  recommendations: AgentRecommendation[] | null;
  onSelectRecommendation?: (txId: string) => void;
  onClose: () => void;
  allCases: any[]; // CandidateCase[]
  budget: number;
}

export function AgentDecisionOverlay({ state, recommendations, onSelectRecommendation, onClose, allCases, budget }: AgentDecisionOverlayProps) {
  const [stages, setStages] = useState([
    { id: 'loading', label: 'Candidate queue loaded', done: false, active: false },
    { id: 'transaction-analysis', label: 'Evidence availability checked', done: false, active: false },
    { id: 'sequence-analysis', label: 'Fused risk signals compared', done: false, active: false },
    { id: 'graph-analysis', label: 'Modality conflicts evaluated', done: false, active: false },
    { id: 'document-analysis', label: 'Investigation budget evaluated', done: false, active: false },
    { id: 'fusion-analysis', label: 'Selecting next investigation', done: false, active: false },
  ]);

  useEffect(() => {
    if (state === 'idle' || state === 'complete') return;
    
    // The sequence of states sent from useInvestigation runRLProcessingStateMachine maps to our visual stages
    const mapping = ['loading', 'transaction-analysis', 'sequence-analysis', 'graph-analysis', 'document-analysis', 'fusion-analysis', 'rl-decision'];
    const activeIdx = mapping.indexOf(state);
    
    setStages(prev => prev.map((stage, i) => ({
      ...stage,
      done: i < activeIdx,
      active: i === activeIdx
    })));
  }, [state]);

  if (state === 'idle' && !recommendations) return null;

  return (
    <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-md z-50 flex flex-col items-center justify-center animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-700 p-8 rounded-2xl w-full max-w-4xl shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Cinematic grid background effect */}
        <div className="absolute inset-0 bg-[url('https://transparenttextures.com/patterns/cubes.png')] opacity-5 mix-blend-overlay pointer-events-none" />
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex-shrink-0">
          <div className="flex items-center gap-4 border-b border-slate-800 pb-6 mb-6">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)]">
              <BrainCircuit size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight">INVESTIGATION COPILOT</h2>
              <p className="text-sm font-mono text-blue-400">Policy Evaluation</p>
            </div>
          </div>
          
          {!recommendations && (
            <div className="space-y-6">
              <h3 className="text-xs uppercase tracking-widest font-bold text-slate-500 mb-2">Policy Evaluation</h3>
              {stages.map((stage) => (
                <div 
                  key={stage.id} 
                  className={`flex items-center gap-4 text-sm font-mono transition-all duration-300 ${
                    stage.active ? 'text-white translate-x-2' : 
                    stage.done ? 'text-blue-500' : 
                    'text-slate-600'
                  }`}
                >
                  {stage.done ? (
                    <CheckCircle2 size={18} className="shrink-0" />
                  ) : stage.active ? (
                    <Loader2 size={18} className="animate-spin shrink-0 text-blue-400" />
                  ) : (
                    <Circle size={18} className="shrink-0" />
                  )}
                  {stage.label}
                </div>
              ))}
            </div>
          )}
        </div>

        {recommendations && state === 'complete' && (
          <div className="animate-in slide-in-from-bottom-4 fade-in duration-500 overflow-y-auto custom-scrollbar pr-2 flex-1 relative z-10 flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs uppercase tracking-widest font-bold text-green-400 flex items-center gap-2">
                <CheckCircle2 size={16} /> Top Recommendations
              </h3>
              <button 
                onClick={onClose}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-colors font-bold"
              >
                Dismiss
              </button>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              {recommendations.slice(0, 1).map((rec) => {
                const caseData = allCases.find(c => c.transaction_id === rec.transaction_id);
                return (
                  <div 
                    key={rec.transaction_id}
                    onClick={() => onSelectRecommendation?.(rec.transaction_id)}
                    className="bg-slate-950 border border-blue-500/50 shadow-[0_0_15px_rgba(37,99,235,0.1)] p-5 rounded-xl transition-all cursor-pointer group hover:bg-slate-900"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-lg font-bold text-slate-200">{rec.transaction_id}</span>
                      </div>
                      <span className="text-[10px] uppercase font-bold bg-blue-500/20 text-blue-400 px-2 py-1 rounded">Priority: HIGH</span>
                    </div>
                    
                    <div className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">Decision factors</div>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-slate-300 font-mono mb-4">
                      {caseData?.fused_score > 0.8 && <li>High fused anomaly score ({(caseData.fused_score * 100).toFixed(0)}%)</li>}
                      {caseData?.conflict_tx_doc < 0.1 ? <li>Strong transaction/document agreement</li> : <li>High cross-modality conflict detected</li>}
                      <li>{budget} investigation units remaining</li>
                    </ul>

                    <div className="flex gap-3">
                      <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg text-sm transition-colors" onClick={(e) => { e.stopPropagation(); onClose(); }}>Review Case</button>
                      <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-lg text-sm transition-colors" onClick={(e) => { e.stopPropagation(); onClose(); }}>Dismiss Recommendation</button>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 border-t border-slate-800 pt-6">
              <h3 className="text-xs uppercase tracking-widest font-bold text-slate-500 mb-4">Investigation Opportunities</h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-3 rounded-lg">
                  <span className="text-sm text-slate-300">2 cases have high transaction risk but weak graph evidence.</span>
                  <button className="text-xs font-bold text-blue-400 hover:text-blue-300 bg-blue-900/20 px-3 py-1 rounded">Explore</button>
                </div>
                <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-3 rounded-lg">
                  <span className="text-sm text-slate-300">High-priority cases in queue without document analysis.</span>
                  <button className="text-xs font-bold text-blue-400 hover:text-blue-300 bg-blue-900/20 px-3 py-1 rounded">Explore</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
