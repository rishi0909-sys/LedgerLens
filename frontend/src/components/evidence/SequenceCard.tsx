import type { CandidateCase } from '../../types';
import { Activity, HelpCircle } from 'lucide-react';

interface SequenceCardProps {
  data: CandidateCase;
}

export function SequenceCard({ data }: SequenceCardProps) {
  const isAvailable = data.seq_available === 1;

  // Generate sequence timeline points (T-20 to T-0)
  const points = Array.from({ length: 21 }, (_, i) => {
    const isCurrent = i === 20;
    // Simulate high risk for the sequence if data.cal_seq > 0.7
    const isAnomalousNode = isAvailable && data.cal_seq > 0.7 && (i === 18 || i === 19 || i === 20);
    return {
      id: `T-${20 - i}`,
      isCurrent,
      isAnomalousNode
    };
  });

  return (
    <div className="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden min-h-[300px] flex flex-col">
      {!isAvailable && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center">
          <HelpCircle size={32} className="text-slate-600 mb-2" />
          <p className="text-slate-400 font-medium">Sequence Data Unavailable</p>
        </div>
      )}
      
      <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900 z-0">
        <div className="flex items-center gap-2 text-slate-300">
          <Activity size={18} className="text-emerald-500" />
          <h3 className="font-bold text-sm uppercase tracking-wider">Sequence Deep Learning</h3>
        </div>
        <span className={`font-mono font-bold ${data.cal_seq > 0.7 ? 'text-red-400' : 'text-emerald-400'}`}>
          {(data.cal_seq * 100).toFixed(1)}% Risk
        </span>
      </div>

      <div className="p-6 flex-1 flex flex-col z-0 justify-center">
        <div className="mb-6">
          <p className="text-xs text-slate-500 uppercase font-bold mb-1">SEQ-20 HISTORY</p>
          <p className="text-sm text-slate-400">LSTM context evaluation across past 20 transactions</p>
        </div>

        <div className="relative h-20 flex items-center w-full px-2">
          {/* Connecting Line */}
          <div className="absolute left-2 right-2 h-1 bg-slate-800 rounded-full"></div>
          
          {/* Nodes */}
          <div className="relative flex justify-between w-full z-10">
            {points.map((p, _) => (
              <div key={p.id} className="flex flex-col items-center group relative cursor-help">
                <div 
                  className={`w-3 h-3 rounded-full transition-transform group-hover:scale-150 ${
                    p.isCurrent 
                      ? (data.cal_seq > 0.7 ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]' : 'bg-emerald-500') 
                      : p.isAnomalousNode 
                      ? 'bg-amber-500' 
                      : 'bg-slate-600'
                  }`}
                />
                
                {/* Tooltip */}
                <div className="absolute bottom-6 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 border border-slate-700 text-[10px] text-white px-2 py-1 rounded pointer-events-none whitespace-nowrap">
                  {p.isCurrent ? 'Current (T-0)' : p.id}
                  {p.isAnomalousNode && !p.isCurrent && ' • Suspicious'}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {data.conflict_tx_seq > 0.2 && isAvailable && (
          <div className="mt-4 text-xs font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-2 rounded-lg text-center">
            LSTM detected hidden sequential anomalies missed by tabular baseline.
          </div>
        )}
      </div>
    </div>
  );
}
