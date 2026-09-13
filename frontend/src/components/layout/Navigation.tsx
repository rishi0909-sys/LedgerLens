import { LayoutDashboard, Database, ShieldAlert, Activity, FileText, FileSearch, BrainCircuit, BarChart2, CheckSquare, X } from 'lucide-react';

interface NavigationProps {
  currentView: string;
  onNavigate: (view: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function Navigation({ currentView, onNavigate, isOpen, onClose }: NavigationProps) {
  const workspaceItems = [
    { id: 'command-center', label: 'Command Center', icon: LayoutDashboard },
    { id: 'cases', label: 'Cases', icon: FileSearch },
    { id: 'network', label: 'Network Explorer', icon: Activity },
    { id: 'document-forensics', label: 'NLP Document Intelligence', icon: FileText },
    { id: 'activity', label: 'Activity', icon: CheckSquare },
  ];

  const aiLabsItems = [
    { id: 'rl-agent-lab', label: 'RL Agent Lab', icon: BrainCircuit },
    { id: 'models', label: 'AI Models', icon: Database },
    { id: 'architecture', label: 'Architecture', icon: Activity },
    { id: 'evaluation', label: 'Evaluation', icon: BarChart2 },
  ];

  const renderNavGroup = (title: string, items: typeof workspaceItems) => (
    <div className="mb-6">
      <h3 className="px-3 mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">{title}</h3>
      <div className="space-y-1">
        {items.map((item) => {
          const isActive = currentView === item.id || (currentView === 'case-detail' && item.id === 'cases');
          return (
            <button
              key={item.id}
              onClick={() => {
                onNavigate(item.id);
                onClose();
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? 'bg-blue-900/20 text-blue-400 border border-blue-900/30' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 md:hidden"
          onClick={onClose}
        />
      )}
      <nav className={`
        fixed inset-y-0 left-0 z-50 w-64 border-r border-slate-800 bg-slate-950 flex flex-col h-screen shrink-0
        transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
      <div className="p-6 flex items-center justify-between gap-3 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(37,99,235,0.4)]">
            <ShieldAlert size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white leading-none">LedgerLens</h1>
            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Workbench v1.0</span>
          </div>
        </div>
        <button onClick={onClose} className="md:hidden text-slate-400 hover:text-white">
          <X size={20} />
        </button>
      </div>
      
      <div className="flex-1 py-6 px-3 overflow-y-auto">
        {renderNavGroup('Investigation Workspace', workspaceItems)}
        {renderNavGroup('AI Labs', aiLabsItems)}
      </div>
      
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-400 border border-slate-800">
          <p className="mb-2 font-semibold text-slate-300">Keyboard Shortcuts</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex justify-between"><span>Cmd+K</span> <span className="bg-slate-800 px-1 rounded text-slate-300">Menu</span></div>
            <div className="flex justify-between"><span>J/K</span> <span className="bg-slate-800 px-1 rounded text-slate-300">Nav</span></div>
            <div className="flex justify-between"><span>Enter</span> <span className="bg-slate-800 px-1 rounded text-slate-300">Open</span></div>
            <div className="flex justify-between"><span>R</span> <span className="bg-slate-800 px-1 rounded text-slate-300">Agent</span></div>
          </div>
        </div>
      </div>
    </nav>
    </>
  );
}
