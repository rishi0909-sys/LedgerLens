import type { CandidateCase } from '../../types';
import { Server, Activity } from 'lucide-react';

interface FusionPanelProps {
  data: CandidateCase;
}

export function FusionPanel({ data }: FusionPanelProps) {
  const hasConflict = data.conflict_tx_doc > 0.2 || data.conflict_tx_seq > 0.2;

  const getBarWidth = (val: number) => `${Math.max(2, val * 100)}%`;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3 text-white">
          <Server size={24} className="text-indigo-400" />
          <h3 className="font-bold text-lg uppercase tracking-wider">Multimodal Evidence Fusion</h3>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-12">
        {/* Evidence Scales */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
              <span>TRANSACTION</span>
              <span>{(data.cal_tx * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500" style={{ width: getBarWidth(data.cal_tx) }} />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
              <span>SEQUENCE</span>
              <span>{(data.cal_seq * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500" style={{ width: getBarWidth(data.cal_seq) }} />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
              <span>GRAPH</span>
              <span>{(data.cal_graph * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500" style={{ width: getBarWidth(data.cal_graph) }} />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
              <span>DOCUMENT</span>
              <span>{(data.cal_doc * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500" style={{ width: getBarWidth(data.cal_doc) }} />
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-slate-800">
            <div className="flex justify-between text-sm font-black text-white mb-2">
              <span>FUSED RISK</span>
              <span className={data.fused_score > 0.8 ? 'text-red-400' : 'text-amber-400'}>
                {(data.fused_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden shadow-inner">
              <div 
                className={`h-full ${data.fused_score > 0.8 ? 'bg-red-500' : 'bg-amber-500'} shadow-[0_0_10px_rgba(239,68,68,0.5)]`} 
                style={{ width: getBarWidth(data.fused_score) }} 
              />
            </div>
          </div>
        </div>

        {/* Conflict Analysis */}
        <div className="flex flex-col">
          <h4 className="text-xs uppercase font-bold text-slate-500 mb-4">Evidence Conflict Analysis</h4>
          
          <div className="space-y-3 mb-6">
            <div className="flex justify-between items-center bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-xs font-medium text-slate-300">Transaction ↔ Document</span>
              <span className={`text-xs font-bold px-2 py-1 rounded ${data.conflict_tx_doc > 0.2 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                {data.conflict_tx_doc > 0.2 ? 'HIGH CONFLICT' : 'AGREEMENT'}
              </span>
            </div>
            <div className="flex justify-between items-center bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-xs font-medium text-slate-300">Transaction ↔ Sequence</span>
              <span className={`text-xs font-bold px-2 py-1 rounded ${data.conflict_tx_seq > 0.2 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                {data.conflict_tx_seq > 0.2 ? 'HIGH CONFLICT' : 'AGREEMENT'}
              </span>
            </div>
          </div>

          {hasConflict && (
            <div className="mt-auto bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4 flex items-start gap-3">
              <Activity className="text-indigo-400 shrink-0 mt-0.5" size={18} />
              <div>
                <p className="text-sm font-bold text-indigo-400 mb-1">Deep Learning Override</p>
                <p className="text-xs text-indigo-200/70 leading-relaxed">
                  The XGBoost fusion meta-model detected significant disagreement between the baseline transaction model and unstructured modalities. 
                  This case was prioritized because the meta-model learned to trust deep learning signals when obfuscation tactics resemble normal tabular patterns.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
