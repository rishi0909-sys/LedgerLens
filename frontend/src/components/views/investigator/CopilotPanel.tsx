import React, { useState } from 'react';
import { Send, FileText, BrainCircuit, Clock } from 'lucide-react';
import type { CandidateCase } from '../../../types';

interface CopilotPanelProps {
  selectedCase: CandidateCase;
  onAddNote: (note: string) => void;
  onAnalyzeDocument: () => void;
  recommendations: any[] | null;
  onClearRecommendations: () => void;
  onFreezeAsset: (amount: number) => void;
  allCases: CandidateCase[];
}

export function CopilotPanel({ 
  selectedCase, 
  onAddNote, 
  onAnalyzeDocument, 
  recommendations, 
  onClearRecommendations,
  onFreezeAsset,
  allCases
}: CopilotPanelProps) {
  const [noteText, setNoteText] = useState('');

  const handleSubmitNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (noteText.trim()) {
      onAddNote(noteText);
      setNoteText('');
    }
  };

  // Combine events and notes into a single timeline, sorted by timestamp
  const timeline = [
    ...(selectedCase.events || []).map(e => ({ ...e, _type: 'event' })),
    ...(selectedCase.notes || []).map(n => ({ ...n, _type: 'note' }))
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  // Find recommendation for this case if any
  const caseRecommendation = recommendations?.find(r => r.transaction_id === selectedCase.transaction_id);

  // Compute related cases
  const relatedCases = (allCases || []).filter(c => 
    c.transaction_id !== selectedCase.transaction_id && 
    c.fused_score > 0.8 && 
    c.status !== 'CONFIRMED_FRAUD'
  ).slice(0, 2);

  return (
    <div className="w-96 border-l border-slate-800 bg-slate-950 flex flex-col h-full shrink-0">
      
      {/* Copilot Header */}
      <div className="p-4 border-b border-slate-800 bg-blue-900/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
            <BrainCircuit size={18} className="text-white" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-200">LedgerLens Copilot</h3>
            <p className="text-[9px] text-slate-500 uppercase tracking-widest font-mono">Powered by MaskablePPO</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        
        {/* Contextual Suggestions */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-300 mb-4">
            You're reviewing <span className="font-bold text-white">{selectedCase.transaction_id}</span>.
          </p>

          {/* Missing Evidence */}
          {selectedCase.doc_available === 0 && (
            <div className="mb-4 text-xs text-amber-400 bg-amber-900/10 border border-amber-900/30 p-2 rounded">
              <strong>Missing Evidence:</strong> No unstructured documents found.
            </div>
          )}

          {/* Evidence Conflicts */}
          {selectedCase.conflict_tx_doc > 0.2 && (
            <div className="mb-4 text-xs text-red-400 bg-red-900/10 border border-red-900/30 p-2 rounded">
              <strong>Evidence Conflict:</strong> High discrepancy between transaction log and document.
            </div>
          )}

          {/* Related Cases */}
          {relatedCases.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 mb-2">I found {relatedCases.length} related cases that may be worth comparing.</p>
              <div className="space-y-2">
                {relatedCases.map(c => (
                  <div key={c.transaction_id} className="flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
                    <span className="font-mono text-xs text-slate-300">{c.transaction_id}</span>
                    <span className="text-xs text-slate-500">Risk {(c.fused_score * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-2 mt-3">
                <button className="text-[10px] uppercase font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded">Compare</button>
                <button className="text-[10px] uppercase font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded">Add</button>
                <button className="text-[10px] uppercase font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded">Dismiss</button>
              </div>
            </div>
          )}
        </div>

        {/* RL Recommendation Summary (if this case was recommended) */}
        {caseRecommendation && (
          <div className="bg-blue-900/20 border border-blue-500 rounded-xl p-4 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-sm font-bold text-blue-400 flex items-center gap-2">
                🤖 RL Agent Recommendation
              </h4>
              <button onClick={onClearRecommendations} className="text-xs text-slate-500 hover:text-slate-300">Dismiss</button>
            </div>
            <p className="text-xs text-slate-300 whitespace-pre-wrap">{caseRecommendation.reasoning}</p>
          </div>
        )}

        {/* Action Required: Freeze Funds */}
        {selectedCase.status === 'CONFIRMED_FRAUD' && (
          <div className="bg-emerald-900/20 border border-emerald-500/50 rounded-xl p-4 animate-pulse-subtle">
            <h4 className="text-sm font-bold text-emerald-400 mb-2">Action Required</h4>
            <p className="text-xs text-slate-300 mb-4">
              You have confirmed this transaction as anomalous. To complete the investigation and protect corporate assets, you must freeze the associated funds immediately.
            </p>
            <button 
              onClick={() => onFreezeAsset(selectedCase.cal_tx > 0.7 ? 482000 : 71000)}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all"
            >
              Freeze ₹{(selectedCase.cal_tx > 0.7 ? 482000 : 71000).toLocaleString()} & Recover
            </button>
          </div>
        )}

        {/* Document Intelligence trigger & Report */}
        {!selectedCase.document_analysis?.isAnalyzed ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
              <FileText size={14} className="text-purple-400" /> NLP Document Intelligence
            </h4>
            
            {selectedCase.doc_available === 1 ? (
              <>
                <p className="text-xs text-slate-400 mb-3">
                  Unstructured documents are attached to this transaction. Run the NLP pipeline to extract text and compute FinBERT embeddings.
                </p>
                <button 
                  onClick={onAnalyzeDocument}
                  disabled={selectedCase.document_analysis?.isAnalyzing}
                  className={`w-full py-2 rounded-lg text-xs font-bold transition-colors ${
                    selectedCase.document_analysis?.isAnalyzing 
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                      : 'bg-purple-600 hover:bg-purple-500 text-white'
                  }`}
                >
                  {selectedCase.document_analysis?.isAnalyzing ? 'Running Pipeline...' : '🧠 Run NLP / FinBERT Extraction'}
                </button>
              </>
            ) : (
              <p className="text-xs text-slate-500 italic">
                No unstructured documents or invoices were found attached to this transaction. NLP extraction is unavailable.
              </p>
            )}
          </div>
        ) : (
          <div className="bg-purple-900/10 border border-purple-500/30 rounded-xl p-4">
            <h4 className="text-sm font-bold text-purple-400 flex items-center gap-2 mb-3">
              <FileText size={14} /> NLP Extraction Report
            </h4>
            <div className="space-y-3 text-xs text-slate-300">
              <div className="flex justify-between items-center bg-slate-950/50 p-2 rounded">
                <span className="text-slate-400">Semantic Risk Score:</span>
                <span className={`font-mono font-bold ${selectedCase.cal_doc > 0.7 ? 'text-red-400' : 'text-purple-400'}`}>
                  {(selectedCase.cal_doc * 100).toFixed(1)}%
                </span>
              </div>
              <p>
                <strong>Cross-Modal Reconciliation:</strong>{' '}
                {selectedCase.conflict_tx_doc > 0.2 ? (
                  <span className="text-red-400">High discrepancy between transaction log and parsed invoice amount detected.</span>
                ) : (
                  <span className="text-green-400">Parsed invoice data reconciles perfectly with the ledger.</span>
                )}
              </p>
              <div className="pt-3 border-t border-purple-500/20 text-slate-400 italic">
                {selectedCase.cal_doc > 0.6 
                  ? "Agent Summary: The FinBERT embeddings of the attached documents suggest risky business context. Combined with structured evidence, this strongly indicates potential fraud or anomalous activity." 
                  : "Agent Summary: The semantic context of the invoice appears standard and low-risk. Document text aligns with expected business operations."}
              </div>
            </div>
          </div>
        )}

        {/* Timeline / Audit Trail */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <Clock size={14} /> Investigation Timeline
          </h4>
          <div className="space-y-4">
            {timeline.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No activity recorded yet.</p>
            ) : (
              timeline.map((item, idx) => {
                const isNote = item._type === 'note';
                const author = isNote ? (item as any).author : (item as any).actor;
                const content = isNote ? (item as any).content : (item as any).description;
                
                return (
                  <div key={item.id || idx} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-slate-700 mt-1.5" />
                      {idx !== timeline.length - 1 && <div className="w-px h-full bg-slate-800 mt-2" />}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-bold text-slate-300">
                          {author}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </span>
                      </div>
                      <p className={`text-xs ${isNote ? 'text-slate-400 bg-slate-900 p-2 rounded mt-1' : 'text-slate-500'}`}>
                        {content}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>

      {/* Add Note Input */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/50">
        <form onSubmit={handleSubmitNote} className="relative">
          <input 
            type="text" 
            placeholder="Add a note..." 
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-3 pr-10 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <button 
            type="submit"
            disabled={!noteText.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-500 hover:text-blue-400 disabled:opacity-50 disabled:hover:text-slate-500 transition-colors"
          >
            <Send size={16} />
          </button>
        </form>
      </div>

    </div>
  );
}
