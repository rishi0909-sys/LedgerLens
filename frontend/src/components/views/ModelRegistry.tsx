import { Database, CheckCircle2 } from 'lucide-react';

export function ModelRegistry() {
  const models = [
    { name: 'Transaction Baseline', type: 'XGBoost', phase: 2, metric: 'PR-AUC 0.887', status: 'Frozen' },
    { name: 'Sequence Context', type: 'LSTM', phase: 3, metric: 'PR-AUC 0.819', status: 'Frozen' },
    { name: 'Graph Topology', type: 'GraphSAGE', phase: 4, metric: 'PR-AUC 0.742', status: 'Frozen' },
    { name: 'Document Intelligence', type: 'FinBERT/OCR', phase: 5, metric: 'F1 0.891', status: 'Frozen' },
    { name: 'Evidence Fusion', type: 'Meta-XGBoost', phase: 6, metric: 'PR-AUC 0.903', status: 'Frozen' },
    { name: 'Investigation Agent', type: 'MaskablePPO', phase: 7, metric: '7/8 Discovered @ K=5', status: 'Frozen' },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12">
      <div className="max-w-5xl mx-auto">
        <div className="mb-12">
          <h2 className="text-2xl md:text-3xl font-black text-white flex items-center gap-3">
            <Database className="text-blue-500" size={32} />
            Model Registry
          </h2>
          <p className="text-slate-400 mt-2">All ML models are currently frozen as research artifacts for Phase 8 productization.</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-x-auto shadow-2xl">
          <table className="w-full text-left border-collapse min-w-full">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800">
                <th className="py-2 md:py-4 px-3 md:px-6 text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-widest">Phase</th>
                <th className="py-2 md:py-4 px-3 md:px-6 text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-widest">Model Name</th>
                <th className="py-2 md:py-4 px-3 md:px-6 text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-widest hidden md:table-cell">Architecture</th>
                <th className="py-2 md:py-4 px-3 md:px-6 text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-widest hidden md:table-cell">Evaluation Metric</th>
                <th className="py-2 md:py-4 px-3 md:px-6 text-[10px] md:text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m, i) => (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 md:py-4 px-3 md:px-6">
                    <span className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center text-xs font-bold">
                      {m.phase}
                    </span>
                  </td>
                  <td className="py-3 md:py-4 px-3 md:px-6 font-bold text-slate-200 text-xs md:text-sm">{m.name}</td>
                  <td className="py-3 md:py-4 px-3 md:px-6 font-mono text-[10px] md:text-xs text-slate-400 hidden md:table-cell">{m.type}</td>
                  <td className="py-3 md:py-4 px-3 md:px-6 text-xs md:text-sm text-slate-300 hidden md:table-cell">{m.metric}</td>
                  <td className="py-3 md:py-4 px-3 md:px-6 text-right">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 md:px-3 md:py-1 rounded-full bg-slate-800 text-slate-400 text-[10px] md:text-xs font-bold border border-slate-700 whitespace-nowrap">
                      <CheckCircle2 size={10} className="text-slate-500 md:w-3 md:h-3" />
                      {m.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
