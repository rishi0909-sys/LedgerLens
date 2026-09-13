import { useState } from 'react';
import { Search, Filter, ArrowRight } from 'lucide-react';
import type { CandidateCase } from '../../../types';

interface CasesViewProps {
  candidates: CandidateCase[];
  onSelectCase: (caseId: string) => void;
}

export function CasesView({ candidates, onSelectCase }: CasesViewProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const filteredCases = candidates.filter(c => {
    if (statusFilter !== 'ALL' && c.status !== statusFilter) return false;
    if (searchTerm && !c.transaction_id.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  }).sort((a, b) => b.fused_score - a.fused_score);

  return (
    <div className="p-8 h-full overflow-y-auto bg-slate-950 flex flex-col">
      <div className="max-w-6xl mx-auto w-full flex-1 flex flex-col">
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">Cases</h1>
          <p className="text-slate-400">Manage and explore investigation cases.</p>
        </div>

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text" 
              placeholder="Search by Transaction ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="appearance-none bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-8 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              <option value="QUEUED">Queued</option>
              <option value="SELECTED">Selected</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse min-w-full">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] md:text-xs uppercase tracking-widest text-slate-500">
                <th className="px-3 py-3 md:px-6 md:py-4 font-bold">Transaction</th>
                <th className="px-3 py-3 md:px-6 md:py-4 font-bold">Status</th>
                <th className="px-3 py-3 md:px-6 md:py-4 font-bold hidden md:table-cell">Fused Risk</th>
                <th className="px-3 py-3 md:px-6 md:py-4 font-bold hidden md:table-cell">Evidence</th>
                <th className="px-3 py-3 md:px-6 md:py-4 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredCases.map(c => (
                <tr key={c.transaction_id} className="border-b border-slate-800/50 hover:bg-slate-800/50 transition-colors group">
                  <td className="px-3 py-3 md:px-6 md:py-4">
                    <span className="font-mono font-bold text-slate-200 text-xs md:text-sm">{c.transaction_id}</span>
                  </td>
                  <td className="px-3 py-3 md:px-6 md:py-4">
                    <span className={`text-[8px] md:text-[10px] uppercase font-bold px-1.5 py-0.5 md:px-2 md:py-1 rounded ${
                      c.status === 'CLOSED' ? 'bg-slate-800 text-slate-400' :
                      c.status === 'INVESTIGATING' ? 'bg-amber-500/20 text-amber-500' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-3 py-3 md:px-6 md:py-4 hidden md:table-cell">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${c.fused_score > 0.8 ? 'bg-red-500' : c.fused_score > 0.5 ? 'bg-amber-500' : 'bg-green-500'}`}
                          style={{ width: `${c.fused_score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-mono text-slate-300">{(c.fused_score * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-3 py-3 md:px-6 md:py-4 hidden md:table-cell">
                    <div className="flex gap-1.5 opacity-50 group-hover:opacity-100 transition-opacity">
                      <div className={`w-1.5 h-4 rounded-sm ${c.tx_available ? 'bg-blue-400' : 'bg-slate-800'}`} title="Transaction" />
                      <div className={`w-1.5 h-4 rounded-sm ${c.seq_available ? 'bg-green-400' : 'bg-slate-800'}`} title="Sequence" />
                      <div className={`w-1.5 h-4 rounded-sm ${c.graph_available ? 'bg-amber-400' : 'bg-slate-800'}`} title="Graph" />
                      <div className={`w-1.5 h-4 rounded-sm ${c.doc_available ? 'bg-purple-400' : 'bg-slate-800'}`} title="Document" />
                    </div>
                  </td>
                  <td className="px-3 py-3 md:px-6 md:py-4 text-right">
                    <button 
                      onClick={() => onSelectCase(c.transaction_id)}
                      className="inline-flex items-center gap-2 px-2 py-1 md:px-4 md:py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-[10px] md:text-sm font-bold transition-colors"
                    >
                      <span className="hidden sm:inline">View</span> Case <ArrowRight size={14} className="hidden sm:block" />
                    </button>
                  </td>
                </tr>
              ))}
              {filteredCases.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    No cases found matching your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
