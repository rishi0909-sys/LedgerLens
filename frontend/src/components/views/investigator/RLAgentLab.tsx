import { useState } from 'react';
import { BrainCircuit, Database, Play, ChevronRight, ChevronDown, CheckCircle2 } from 'lucide-react';
import { useInvestigation } from '../../../hooks/useInvestigation';
import { RLAgentChat } from './RLAgentChat';

export function RLAgentLab() {
  const invState = useInvestigation();
  const { state, runRLProcessingStateMachine } = invState;
  
  const [activeBudget, setActiveBudget] = useState<5|10|20>(5);
  const [expandedState, setExpandedState] = useState<string | null>(null);

  // Hardcoded benchmark data from Phase 7 report
  const benchmarks = {
    5: { Random: 0, 'Transaction Risk': 7, 'Highest Risk': 7, 'Highest Disagreement': 7, 'MaskablePPO': 7, Oracle: 8 },
    10: { Random: 3, 'Transaction Risk': 7, 'Highest Risk': 7, 'Highest Disagreement': 7, 'MaskablePPO': 7, Oracle: 8 },
    20: { Random: 8, 'Transaction Risk': 8, 'Highest Risk': 8, 'Highest Disagreement': 8, 'MaskablePPO': 8, Oracle: 8 }
  };

  const policies = ['Random', 'Transaction Risk', 'Highest Risk', 'Highest Disagreement', 'MaskablePPO', 'Oracle'];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12">
      <div className="max-w-6xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        {/* Header */}
        <section className="space-y-4 border-b border-slate-800 pb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
            <BrainCircuit size={16} /> RL INVESTIGATION LAB
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-black tracking-tight text-white">
            Budget-Constrained Case Prioritization
          </h1>
          <p className="text-lg text-slate-400 max-w-3xl leading-relaxed">
            MaskablePPO • Stable-Baselines3 • Gymnasium
          </p>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex items-center justify-between text-slate-300 font-mono text-sm overflow-x-auto hide-scrollbar gap-4 md:gap-0">
            <div className="text-center min-w-max">20 suspicious cases</div>
            <ChevronRight className="text-slate-600 min-w-max" />
            <div className="text-center min-w-max">Only 5 investigations available</div>
            <ChevronRight className="text-slate-600 min-w-max" />
            <div className="text-center text-blue-400 font-bold min-w-max">Which cases should be investigated first?</div>
            <ChevronRight className="text-slate-600 min-w-max" />
            <div className="text-center min-w-max">RL learns an investigation policy</div>
          </div>
        </section>

        {/* Dashboard Metrics */}
        <section className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group col-span-1 lg:col-span-2">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">Environment</p>
                <p className="font-mono text-white text-lg">FinancialInvestigationEnv</p>
              </div>
              <Database className="text-slate-700" size={32} />
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm mt-6">
              <div>
                <span className="text-slate-500 block text-xs">Candidates</span>
                <span className="font-mono text-slate-200" title="Total number of cases in the queue">20</span>
              </div>
              <div>
                <span className="text-slate-500 block text-xs">Investigation Budget</span>
                <span className="font-mono text-slate-200" title="Maximum number of cases that can be investigated">{state.budget}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-xs">Action Space</span>
                <span className="font-mono text-slate-200" title="The agent chooses which candidate to investigate next">Discrete(20)</span>
              </div>
              <div>
                <span className="text-slate-500 block text-xs">Policy</span>
                <span className="font-mono text-slate-200 text-blue-400">MaskablePPO</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-500 block text-xs">Reward Function</span>
                <span className="font-mono text-slate-200">+1 per True Positive • -0.1 per False Positive</span>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Live Discoveries</p>
              <p className="text-3xl md:text-4xl font-bold text-blue-400">{state.discoveries}</p>
            </div>
            <p className="text-xs text-slate-500 mt-2">Successful fraud confirmations in this session.</p>
          </div>
          
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <p className="text-xs uppercase tracking-widest text-blue-400 font-bold mb-2">Policy Status</p>
              <p className="text-2xl font-bold text-white mt-3">
                {state.processingState === 'idle' || state.processingState === 'complete' ? 'READY' : 'PROCESSING'}
              </p>
            </div>
            <button 
              onClick={runRLProcessingStateMachine}
              disabled={state.processingState !== 'idle' && state.processingState !== 'complete'}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold py-2 rounded-lg transition-all flex items-center justify-center gap-2 text-sm"
            >
              <Play size={14} />
              {state.processingState !== 'idle' && state.processingState !== 'complete' ? 'Simulating...' : 'Start Simulation'}
            </button>
          </div>
        </section>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Batch Simulation Box */}
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col h-[500px]">
            <h3 className="text-sm font-bold text-slate-200 mb-4 flex justify-between items-center">
              <span>Batch Simulation Log</span>
              {state.mode === 'DEMO' && <span className="text-[10px] bg-amber-500/20 text-amber-500 px-2 py-1 rounded uppercase tracking-wider">DEMO SIMULATION</span>}
            </h3>
            
            <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-4 overflow-y-auto font-mono text-xs space-y-3 min-h-[300px]">
              {state.processingState === 'idle' && !state.agentRecommendations && (
                <div className="text-slate-500 text-center mt-20">Click 'Start Simulation' to run the evaluation.</div>
              )}
              {state.processingState !== 'idle' && state.processingState !== 'complete' && (
                <div className="text-blue-400 flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                  Running policy evaluation...
                </div>
              )}
              {state.agentRecommendations && (
                <>
                  <div className="text-slate-400 border-b border-slate-800 pb-2 mb-2">
                    CANDIDATE QUEUE EVALUATED
                  </div>
                  {state.agentRecommendations.slice(0, 3).map((rec, i) => (
                    <div key={rec.transaction_id} className="text-slate-300">
                      STEP 0{i + 1}<br/>
                      <span className="text-blue-400">Selected {rec.transaction_id}</span><br/>
                      Reward {i === 0 ? '+1.0' : '-0.1'}
                    </div>
                  ))}
                  <div className="text-emerald-400 mt-4 border-t border-slate-800 pt-2 flex items-center gap-2">
                    <CheckCircle2 size={14} /> Simulation Complete. Recommendations sent to Copilot.
                  </div>
                </>
              )}
            </div>
          </section>

          {/* RL Copilot Chat */}
          <div className="h-[500px]">
            <RLAgentChat 
              chatHistory={state.chatHistory} 
              isTraining={state.isTraining} 
              onSendFeedback={invState.sendFeedback} 
            />
          </div>

          {/* State Explorer */}
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-[500px] overflow-y-auto">
             <h3 className="text-sm font-bold text-slate-200 mb-4">State Explorer</h3>
             <p className="text-xs text-slate-400 mb-4">Observable state variables passed to the policy for evaluation.</p>
             
             <div className="space-y-2">
               {[
                 { id: 'risk', label: 'Risk Signals', data: { fused_risk_score: 0.94, cal_tx: 0.72, cal_seq: 0.81, cal_graph: 0.22, cal_doc: 0.89 } },
                 { id: 'modality', label: 'Modality Availability', data: { doc_available: true, sequence_available: true, graph_available: true } },
                 { id: 'conflict', label: 'Evidence Conflict', data: { conflict_tx_doc: 0.17, conflict_tx_seq: 0.09 } },
                 { id: 'budget', label: 'Budget', data: { remaining_budget: state.budget, cumulative_discoveries: state.discoveries } }
               ].map(category => (
                 <div key={category.id} className="border border-slate-800 rounded-lg overflow-hidden">
                   <button 
                     onClick={() => setExpandedState(expandedState === category.id ? null : category.id)}
                     className="w-full flex items-center justify-between p-3 bg-slate-950 hover:bg-slate-900 text-sm font-bold text-slate-300 transition-colors"
                   >
                     {category.label}
                     <ChevronDown size={16} className={`transform transition-transform ${expandedState === category.id ? 'rotate-180' : ''}`} />
                   </button>
                   {expandedState === category.id && (
                     <div className="p-3 bg-slate-900 border-t border-slate-800 font-mono text-xs text-slate-400">
                       <pre>{JSON.stringify(category.data, null, 2)}</pre>
                     </div>
                   )}
                 </div>
               ))}
             </div>
          </section>
        </div>

        {/* Policy Comparison */}
        <section className="space-y-6">
          <h3 className="text-sm font-bold text-slate-200 mb-4">Policy Benchmark (Phase 7 Results)</h3>
          
          <div className="flex gap-2 mb-4">
            {[5, 10, 20].map(k => (
              <button 
                key={k} 
                onClick={() => setActiveBudget(k as 5|10|20)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${activeBudget === k ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
              >
                Budget (K={k})
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950 border-b border-slate-800 text-slate-500 font-mono">
                  <tr>
                    <th className="p-4 font-normal">Policy</th>
                    <th className="p-4 text-right font-normal">K=5</th>
                    <th className="p-4 text-right font-normal">K=10</th>
                    <th className="p-4 text-right font-normal">K=20</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {policies.map(policy => (
                    <tr key={policy} className={policy === 'MaskablePPO' ? 'bg-blue-900/10' : ''}>
                      <td className={`p-4 font-mono ${policy === 'MaskablePPO' ? 'text-blue-400 font-bold' : 'text-slate-300'}`}>{policy}</td>
                      <td className="p-4 text-right font-mono text-slate-400">{benchmarks[5][policy as keyof typeof benchmarks[5]]}</td>
                      <td className="p-4 text-right font-mono text-slate-400">{benchmarks[10][policy as keyof typeof benchmarks[10]]}</td>
                      <td className="p-4 text-right font-mono text-slate-400">{benchmarks[20][policy as keyof typeof benchmarks[20]]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-end relative min-h-[300px]">
              <div className="absolute top-6 left-6 text-xs text-slate-500 font-bold tracking-widest uppercase">Anomalies Discovered (K={activeBudget})</div>
              <div className="flex items-end justify-around h-48 mt-8 border-b border-slate-800 pb-2">
                {policies.map(policy => {
                  const val = benchmarks[activeBudget][policy as keyof typeof benchmarks[5]];
                  const maxVal = benchmarks[activeBudget]['Oracle'];
                  const height = `${(val / maxVal) * 100}%`;
                  return (
                    <div key={policy} className="flex flex-col items-center gap-2 group w-full px-2">
                      <div className="w-full flex justify-center items-end h-full">
                        <div 
                          style={{ height }} 
                          className={`w-full max-w-[40px] rounded-t-sm transition-all duration-500 relative ${
                            policy === 'MaskablePPO' ? 'bg-blue-500' : 
                            policy === 'Oracle' ? 'bg-emerald-500/50' : 
                            'bg-slate-700'
                          }`}
                        >
                          <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                            {val}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-around mt-4">
                {policies.map(policy => (
                  <div key={policy} className="text-[9px] sm:text-[10px] text-slate-500 text-center w-full px-0.5 sm:px-1 truncate" title={policy}>
                    {policy === 'Transaction Risk' ? 'Tx Risk' : policy === 'Highest Disagreement' ? 'Disagreem.' : policy}
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="text-xs text-slate-500 italic p-4 bg-slate-900/50 rounded-lg border border-slate-800">
            Note: On the current synthetic benchmark, the learned policy matched the strongest heuristic baseline but did not outperform it.
          </div>
        </section>
        
      </div>
    </div>
  );
}
