import { Server, ShieldCheck } from 'lucide-react';

interface SystemStatusProps {
  mode: 'LIVE' | 'DEMO';
}

export function SystemStatus({ mode }: SystemStatusProps) {
  return (
    <div className="min-h-12 border-t border-slate-800 bg-slate-950 flex items-center justify-between px-4 md:px-6 py-3 md:py-0 text-xs text-slate-400 shrink-0">
      <div className="flex flex-wrap items-center gap-3 md:gap-6 w-full md:w-auto">
        <div className="flex items-center gap-2 shrink-0">
          <Server size={14} className={mode === 'LIVE' ? 'text-green-500' : 'text-amber-500'} />
          <span className="font-medium text-slate-300">API: {mode}</span>
        </div>
        <div className="hidden md:block h-4 w-px bg-slate-800 shrink-0" />
        <div className="flex flex-wrap items-center gap-2 md:gap-4 text-[10px] font-mono tracking-widest uppercase">
          <span className="text-slate-500 hidden md:inline">INTELLIGENCE:</span>
          <span className="text-emerald-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse-subtle" /> TX</span>
          <span className="text-emerald-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse-subtle" /> SEQ</span>
          <span className="text-emerald-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse-subtle" /> GNN</span>
          <span className="text-amber-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-amber-500 rounded-full" /> DOC</span>
          <span className="text-emerald-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse-subtle" /> FUSION</span>
          <span className="text-blue-500 flex items-center gap-1 shrink-0"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse-subtle" /> PPO</span>
        </div>
      </div>
      <div className="hidden md:flex items-center gap-2 ml-4 shrink-0">
        <ShieldCheck size={14} className="text-slate-500" />
        <span>Engine v1.0</span>
      </div>
    </div>
  );
}
