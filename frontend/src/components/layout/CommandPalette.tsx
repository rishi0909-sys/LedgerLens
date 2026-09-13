import { useState } from 'react';
import { Search, Code, LayoutDashboard, BrainCircuit, Activity, Database, Check, FileText } from 'lucide-react';
import { getIsDemoMode, setDemoMode } from '../../services/api';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: string) => void;
  onRLAgent: () => void;
  onReload: () => void;
}

export function CommandPalette({ isOpen, onClose, onNavigate, onRLAgent, onReload }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  
  if (!isOpen) return null;
  
  const isDemo = getIsDemoMode();

  const handleDemoToggle = () => {
    setDemoMode(!isDemo);
    onReload();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-start justify-center pt-32">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center px-4 border-b border-slate-700">
          <Search className="text-slate-400 mr-3" size={20} />
          <input 
            autoFocus
            className="w-full bg-transparent py-4 text-slate-100 outline-none placeholder:text-slate-500"
            placeholder="Type a command or search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button onClick={onClose} className="text-xs border border-slate-700 text-slate-400 px-2 py-1 rounded">ESC</button>
        </div>
        
        <div className="max-h-80 overflow-y-auto p-2">
          <div className="px-2 py-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Navigation</div>
          
          <button onClick={() => { onNavigate('overview'); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <LayoutDashboard size={16} className="text-blue-400" />
            Go to Overview
          </button>
          
          <button onClick={() => { onNavigate('investigations'); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <Search size={16} className="text-blue-400" />
            Go to Investigations Queue
          </button>
          
          <button onClick={() => { onNavigate('architecture'); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <Activity size={16} className="text-indigo-400" />
            Show Architecture Diagram
          </button>

          <button onClick={() => { onNavigate('nlp'); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <FileText size={16} className="text-indigo-400" />
            Go to Document Intelligence
          </button>

          <button onClick={() => { onNavigate('models'); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <Database size={16} className="text-indigo-400" />
            Show Model Registry
          </button>

          <div className="px-2 pt-4 pb-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</div>
          
          <button onClick={() => { onRLAgent(); onClose(); }} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <BrainCircuit size={16} className="text-amber-400" />
            Get Investigation Recommendation
          </button>
          
          <button onClick={handleDemoToggle} className="w-full text-left flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-slate-800 text-slate-200">
            <div className="flex items-center gap-3">
              <Code size={16} className={isDemo ? 'text-green-400' : 'text-slate-400'} />
              Toggle Demo Mode (Local Fixtures)
            </div>
            {isDemo && <Check size={16} className="text-green-400" />}
          </button>
        </div>
      </div>
    </div>
  );
}
