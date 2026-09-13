import { ArrowRight, BrainCircuit, Activity, FileText, Database, Share2, Server } from 'lucide-react';
import { motion } from 'framer-motion';

export function Overview({ onStart }: { onStart: () => void }) {
  const stats = [
    { label: 'Cases in Queue', value: '20' },
    { label: 'Investigation Budget', value: '5 Units' },
    { label: 'RL Policy', value: 'MaskablePPO' },
    { label: 'Fusion Engine', value: 'XGBoost Meta' }
  ];

  const pipeline = [
    { name: 'Transaction Baseline', icon: Database, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { name: 'Sequence Deep Learning', icon: Activity, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { name: 'Financial Graph ML', icon: Share2, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { name: 'Document Intelligence', icon: FileText, color: 'text-purple-400', bg: 'bg-purple-500/10' },
    { name: 'Evidence Fusion', icon: Server, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { name: 'RL Investigation', icon: BrainCircuit, color: 'text-red-400', bg: 'bg-red-500/10' },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12 relative overflow-hidden">
      <div className="max-w-5xl mx-auto space-y-16 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        {/* Hero */}
        <section className="space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
            <BrainCircuit size={16} /> Phase 8 Workbench
          </div>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white leading-tight">
            Financial Forensics Intelligence
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl leading-relaxed">
            Multimodal evidence fusion for high-risk financial investigations. 
            LedgerLens combines tabular, sequential, topological, and visual evidence into a single RL-prioritized queue.
          </p>
          <div className="pt-4">
            <button 
              onClick={onStart}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all flex items-center gap-2"
            >
              Start Investigation <ArrowRight size={18} />
            </button>
          </div>
        </section>

        {/* Stats */}
        <section className="grid grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-2">{stat.label}</p>
              <p className="text-2xl font-black text-white">{stat.value}</p>
            </div>
          ))}
        </section>

        {/* Pipeline */}
        <section className="bg-slate-900/50 border border-slate-800 rounded-3xl p-4 md:p-8 space-y-8">
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-500">Processing Pipeline</h2>
          
          <div className="flex justify-between items-center relative">
            {/* Connecting Line */}
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-800 -z-10 -translate-y-1/2"></div>
            
            {pipeline.map((node, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex flex-col items-center gap-4 bg-slate-950 p-2 rounded-xl"
              >
                <div className={`w-14 h-14 rounded-2xl ${node.bg} border border-slate-800 flex items-center justify-center ${node.color} shadow-lg cursor-help transition-transform hover:scale-110`}>
                  <node.icon size={24} />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 w-24 text-center leading-tight">
                  {node.name}
                </span>
              </motion.div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}
