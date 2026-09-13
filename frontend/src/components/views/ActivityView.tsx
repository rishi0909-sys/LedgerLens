import { Activity, Clock } from 'lucide-react';

export function ActivityView() {
  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12">
      <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        <section className="space-y-4 border-b border-slate-800 pb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
            <Activity size={16} /> SYSTEM ACTIVITY
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white">
            Activity Log
          </h1>
          <p className="text-lg text-slate-400 max-w-3xl leading-relaxed">
            Monitor system events, investigation updates, and AI actions across the LedgerLens platform.
          </p>
        </section>

        <section className="flex flex-col items-center justify-center py-32 text-slate-500 space-y-4">
          <Clock size={48} className="text-slate-700" />
          <p className="text-lg">No recent activity found.</p>
          <p className="text-sm text-slate-600">Events will appear here as investigations progress.</p>
        </section>
      </div>
    </div>
  );
}
