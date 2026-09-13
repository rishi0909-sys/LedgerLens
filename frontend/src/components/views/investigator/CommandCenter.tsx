import { ShieldAlert, AlertTriangle, ArrowRight, Activity, Clock, ShieldCheck, CheckCircle2 } from 'lucide-react';
import type { CandidateCase } from '../../../types';

interface CommandCenterProps {
  candidates: CandidateCase[];
  budget: number;
  fundsProtected: number;
  onNavigateToCase: (caseId: string) => void;
}

export function CommandCenter({ candidates, budget, fundsProtected, onNavigateToCase }: CommandCenterProps) {
  const activeCases = candidates.filter(c => !['CLOSED', 'ASSET_FROZEN', 'FALSE_POSITIVE'].includes(c.status));
  const highPriority = activeCases.filter(c => c.fused_score > 0.8);
  const underReview = activeCases.filter(c => ['INVESTIGATING', 'EVIDENCE_REVIEW'].includes(c.status));
  
  // Fake "Recent Alerts" that look like deterministic Priority Inbox items for the demo
  const inboxAlerts = [
    {
      id: 'alert-1',
      title: 'New high-conflict transaction detected',
      message: '3 evidence streams disagree on TXN_f8cbab4c.',
      caseId: 'TXN_f8cbab4c',
      time: '2 mins ago',
      isHighRisk: true
    },
    {
      id: 'alert-2',
      title: 'Graph Anomaly Spike',
      message: 'Account activity for TXN_7eccdaf4 deviates 400% from baseline.',
      caseId: 'TXN_7eccdaf4',
      time: '15 mins ago',
      isHighRisk: false
    }
  ];

  return (
    <div className="p-8 h-full overflow-y-auto bg-slate-950">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Mission Statement */}
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck size={24} className="text-blue-400" />
            <div>
              <h2 className="text-sm font-bold text-blue-100">Your Mission: Protect Corporate Assets</h2>
              <p className="text-xs text-blue-300">Review flagged transactions, leverage AI evidence, and confirm fraud to freeze at-risk funds.</p>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 md:gap-0">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">Command Center</h1>
            <p className="text-slate-400">Welcome back. You have {activeCases.length} active cases requiring attention.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
            <div className="bg-emerald-900/30 border border-emerald-500/30 rounded-xl px-5 py-3 flex items-center justify-between sm:justify-start gap-4">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-emerald-500 font-bold mb-1">Corporate Funds Protected</p>
                <p className="text-2xl font-mono font-bold text-emerald-400 leading-none">₹{(fundsProtected || 0).toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 rounded-full border-4 border-emerald-900/50 flex items-center justify-center">
                <ShieldCheck size={20} className="text-emerald-500" />
              </div>
            </div>
            
            <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-3 flex items-center justify-between sm:justify-start gap-4">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">Investigation Budget</p>
                <p className="text-2xl font-mono font-bold text-white leading-none">{budget} <span className="text-sm text-slate-500 font-sans font-medium">units</span></p>
              </div>
              <div className="w-12 h-12 rounded-full border-4 border-slate-800 flex items-center justify-center">
                <Activity size={20} className="text-blue-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShieldAlert size={64} />
            </div>
            <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">High Priority</p>
            <p className="text-3xl md:text-4xl font-bold text-white">{highPriority.length}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Clock size={64} />
            </div>
            <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Under Review</p>
            <p className="text-3xl md:text-4xl font-bold text-white">{underReview.length}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <CheckCircle2 size={64} />
            </div>
            <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Total Active Cases</p>
            <p className="text-3xl md:text-4xl font-bold text-white">{activeCases.length}</p>
          </div>
        </div>

        {/* Priority Inbox */}
        <div className="mt-12">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle size={20} className="text-amber-500" />
            Priority Inbox
          </h2>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
            {inboxAlerts.map((alert, idx) => (
              <div key={alert.id} className={`p-5 flex items-start gap-4 ${idx !== inboxAlerts.length - 1 ? 'border-b border-slate-800' : ''}`}>
                <div className={`mt-1 w-2 h-2 rounded-full ${alert.isHighRisk ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' : 'bg-blue-500'}`} />
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="font-bold text-slate-200 text-sm">{alert.title}</h3>
                    <span className="text-xs font-mono text-slate-500">{alert.time}</span>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">{alert.message}</p>
                  <div className="flex gap-3">
                    <button 
                      onClick={() => onNavigateToCase(alert.caseId)}
                      className="text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                    >
                      Review Case <ArrowRight size={14} />
                    </button>
                    <button className="text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg transition-colors">
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
