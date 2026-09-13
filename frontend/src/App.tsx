import { useState } from 'react';
import { Navigation } from './components/layout/Navigation';
import { SystemStatus } from './components/layout/SystemStatus';
import { CommandPalette } from './components/layout/CommandPalette';
import { Architecture } from './components/views/Architecture';
import { ModelRegistry } from './components/views/ModelRegistry';
import { DocumentForensics } from './components/views/investigator/DocumentForensics';
import { CommandCenter } from './components/views/investigator/CommandCenter';
import { CasesView } from './components/views/investigator/CasesView';
import { NetworkExplorer } from './components/views/investigator/NetworkExplorer';
import { CaseWorkspace } from './components/views/investigator/CaseWorkspace';
import { AgentDecisionOverlay } from './components/views/AgentDecisionOverlay';
import { ProcessingOverlay } from './components/shared/ProcessingOverlay';
import { RLAgentLab } from './components/views/investigator/RLAgentLab';
import { ActivityView } from './components/views/ActivityView';
import { EvaluationView } from './components/views/EvaluationView';
import { useInvestigation } from './hooks/useInvestigation';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

export default function App() {
  const [currentView, setCurrentView] = useState('command-center');
  const [isCmdKOpen, setIsCmdKOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const invState = useInvestigation();
  
  // Expose keyboard navigation
  useKeyboardShortcuts({
    onCmdK: () => setIsCmdKOpen(prev => !prev),
    onEscape: () => setIsCmdKOpen(false),
    onRL: invState.runRLProcessingStateMachine
  });

  return (
    <div className="h-screen w-full flex bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30 overflow-hidden">
      <CommandPalette 
        isOpen={isCmdKOpen} 
        onClose={() => setIsCmdKOpen(false)}
        onNavigate={setCurrentView}
        onRLAgent={invState.runRLProcessingStateMachine}
        onReload={invState.loadQueue}
      />
      
      <AgentDecisionOverlay 
        state={invState.state.processingState} 
        recommendations={invState.state.agentRecommendations}
        onClose={invState.clearRecommendations}
        allCases={invState.state.candidates || []}
        budget={invState.state.budget}
        onSelectRecommendation={(txId) => {
          const c = invState.state.candidates?.find(c => c.transaction_id === txId);
          if (c) invState.selectCase(c);
        }}
      />
      <ProcessingOverlay state={invState.state.processingState} />
      
      <Navigation 
        currentView={currentView} 
        onNavigate={setCurrentView} 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950">
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-bold tracking-tight text-white leading-none">LedgerLens</h1>
            <span className="text-[8px] uppercase tracking-widest text-slate-500 font-bold">Workbench</span>
          </div>
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-900"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
        </div>
        
        <div className="flex-1 overflow-hidden flex flex-col">
          {currentView === 'command-center' && (
            <CommandCenter 
              candidates={invState.state.candidates || []} 
              budget={invState.state.budget} 
              fundsProtected={invState.state.fundsProtected}
              onNavigateToCase={(caseId) => {
                const c = invState.state.candidates.find(c => c.transaction_id === caseId);
                if(c) {
                  invState.selectCase(c);
                  setCurrentView('case-detail');
                }
              }} 
            />
          )}
          {currentView === 'cases' && (
            <CasesView 
              candidates={invState.state.candidates || []}
              onSelectCase={(caseId) => {
                const c = invState.state.candidates.find(c => c.transaction_id === caseId);
                if (c) {
                  invState.selectCase(c);
                  setCurrentView('case-detail');
                }
              }}
            />
          )}
          {currentView === 'case-detail' && (
            <CaseWorkspace 
              selectedCase={invState.state.selectedCandidate} 
              onUpdateStatus={invState.updateCaseStatusManual}
              onAddNote={invState.addNote}
              onAnalyzeDocument={invState.triggerDocumentAnalysis}
              recommendations={invState.state.agentRecommendations}
              onClearRecommendations={invState.clearRecommendations}
              onFreezeAsset={(amount) => {
                invState.freezeAsset(amount);
                setCurrentView('command-center'); // Navigate back after success
              }}
              allCases={invState.state.candidates || []}
            />
          )}
          {currentView === 'network' && <NetworkExplorer />}
          {currentView === 'document-forensics' && <DocumentForensics />}
          {currentView === 'activity' && <ActivityView />}
          {currentView === 'rl-agent-lab' && <RLAgentLab />}
          
          {currentView === 'architecture' && <Architecture />}
          {currentView === 'models' && <ModelRegistry />}
          {currentView === 'evaluation' && <EvaluationView />}
        </div>
        
        <SystemStatus mode={invState.state.mode} />
      </div>
    </div>
  );
}
