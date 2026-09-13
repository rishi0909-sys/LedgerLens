import { ShieldAlert, CheckCircle, XCircle, Clock } from 'lucide-react';
import type { CandidateCase, CaseStatus } from '../../../types';
import { CopilotPanel } from './CopilotPanel'; // Import the newly created CopilotPanel
import { FusionPanel } from '../../evidence/FusionPanel';
import { TransactionCard } from '../../evidence/TransactionCard';
import { SequenceCard } from '../../evidence/SequenceCard';
import { GraphCard } from '../../evidence/GraphCard';
import { DocumentCard } from '../../evidence/DocumentCard';

interface CaseWorkspaceProps {
  selectedCase: CandidateCase | null;
  onUpdateStatus: (status: CaseStatus, description: string) => void;
  onAddNote: (note: string) => void;
  onAnalyzeDocument: () => void;
  recommendations: any[] | null;
  onClearRecommendations: () => void;
  onFreezeAsset: (amount: number) => void;
  allCases: CandidateCase[];
}

export function CaseWorkspace({ 
  selectedCase, 
  onUpdateStatus, 
  onAddNote, 
  onAnalyzeDocument, 
  recommendations, 
  onClearRecommendations,
  onFreezeAsset,
  allCases
}: CaseWorkspaceProps) {
  if (!selectedCase) {
    return <div className="p-8 text-white">No case selected</div>;
  }

  return (
    <div className="flex flex-col lg:flex-row h-full bg-slate-950 text-white overflow-hidden">
      {/* Main Evidence Workspace */}
      <div className="flex-1 overflow-y-auto flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-slate-900/50 gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold font-mono tracking-tight">{selectedCase.transaction_id}</h2>
              <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${
                selectedCase.status === 'CLOSED' ? 'bg-slate-800 text-slate-400' :
                selectedCase.status === 'FALSE_POSITIVE' ? 'bg-slate-800 text-slate-400' :
                selectedCase.status === 'INVESTIGATING' ? 'bg-amber-500/20 text-amber-500' :
                selectedCase.status === 'CONFIRMED_FRAUD' ? 'bg-red-500/20 text-red-500' :
                selectedCase.status === 'ASSET_FROZEN' ? 'bg-emerald-500/20 text-emerald-500' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {selectedCase.status}
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <ShieldAlert size={14} className={selectedCase.fused_score > 0.8 ? 'text-red-500' : ''} />
                Risk Score: {(selectedCase.fused_score * 100).toFixed(1)}%
              </span>
              <span className="flex items-center gap-2">
                <Clock size={14} />
                Last Updated: {selectedCase.events?.[selectedCase.events?.length - 1]?.timestamp?.split('T')[0] || 'Just now'}
              </span>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto mt-4 sm:mt-0">
            <button 
              onClick={() => onUpdateStatus('FALSE_POSITIVE', 'Marked as false positive by investigator')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-bold transition-colors flex items-center gap-2"
            >
              <XCircle size={16} /> False Positive
            </button>
            <button 
              onClick={() => onUpdateStatus('CONFIRMED_FRAUD', 'Confirmed anomalous by investigator')}
              className="px-4 py-2 bg-red-900/40 hover:bg-red-900/60 text-red-400 border border-red-900/50 rounded-lg text-sm font-bold transition-colors flex items-center gap-2"
            >
              <CheckCircle size={16} /> Confirm Fraud
            </button>
          </div>
        </div>

        {/* Workspace Body */}
        <div className="flex-1 p-6 space-y-6">
          <FusionPanel data={selectedCase} />
          
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <TransactionCard data={selectedCase} />
            <SequenceCard data={selectedCase} />
            <GraphCard data={selectedCase} />
            <DocumentCard data={selectedCase} onAnalyzeDocument={onAnalyzeDocument} />
          </div>
        </div>
      </div>
      
      {/* Copilot Sidebar */}
      <CopilotPanel 
        selectedCase={selectedCase}
        onAddNote={onAddNote}
        onAnalyzeDocument={onAnalyzeDocument}
        recommendations={recommendations}
        onClearRecommendations={onClearRecommendations}
        onFreezeAsset={onFreezeAsset}
        allCases={allCases}
      />
    </div>
  );
}
