import type { CandidateCase } from '../../types';
import { Database, HelpCircle } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, YAxis, Tooltip } from 'recharts';

interface TransactionCardProps {
  data: CandidateCase;
}

export function TransactionCard({ data }: TransactionCardProps) {
  const isAvailable = data.tx_available === 1;

  // Mock historical data centered around the risk profile for visualization
  const historicalData = [
    { value: 65000 }, { value: 71000 }, { value: 68000 }, { value: 72000 }, 
    { value: 69000 }, { value: 70000 }, 
    { value: isAvailable && data.cal_tx > 0.7 ? 482000 : 71000 } // The anomaly
  ];

  return (
    <div className="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden min-h-[300px] flex flex-col">
      {!isAvailable && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center">
          <HelpCircle size={32} className="text-slate-600 mb-2" />
          <p className="text-slate-400 font-medium">Tabular Data Unavailable</p>
        </div>
      )}
      
      <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900 z-0">
        <div className="flex items-center gap-2 text-slate-300">
          <Database size={18} className="text-blue-500" />
          <h3 className="font-bold text-sm uppercase tracking-wider">Transaction Baseline</h3>
        </div>
        <span className={`font-mono font-bold ${data.cal_tx > 0.7 ? 'text-red-400' : 'text-blue-400'}`}>
          {(data.cal_tx * 100).toFixed(1)}% Risk
        </span>
      </div>

      <div className="p-6 flex-1 flex flex-col z-0">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Amount</p>
            <p className="text-lg font-mono text-slate-200">₹{data.cal_tx > 0.7 ? '482,000' : '71,000'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Historical Avg</p>
            <p className="text-lg font-mono text-slate-400">₹71,000</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Deviation</p>
            <p className={`text-lg font-mono ${data.cal_tx > 0.7 ? 'text-red-400' : 'text-slate-400'}`}>
              {data.cal_tx > 0.7 ? '+579%' : '0%'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Type</p>
            <p className="text-lg font-mono text-slate-200">Transfer</p>
          </div>
        </div>

        <div className="flex-1 min-h-[100px] w-full mt-auto">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historicalData}>
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }}
                itemStyle={{ color: '#60a5fa' }}
                labelStyle={{ display: 'none' }}
              />
              <YAxis domain={['dataMin - 10000', 'dataMax + 10000']} hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ r: 4, fill: '#1e293b', strokeWidth: 2 }}
                activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
