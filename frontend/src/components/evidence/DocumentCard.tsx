import { useState } from 'react';
import type { CandidateCase } from '../../types';
import { FileText, HelpCircle, Eye, EyeOff, PlayCircle, Loader2 } from 'lucide-react';

interface DocumentCardProps {
  data: CandidateCase;
  onAnalyzeDocument: () => void;
}

export function DocumentCard({ data, onAnalyzeDocument }: DocumentCardProps) {
  const isAvailable = data.doc_available === 1;
  const [showOCR, setShowOCR] = useState(false);
  const docState = data.document_analysis;

  return (
    <div className="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden min-h-[300px] flex flex-col">
      {!isAvailable && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center">
          <HelpCircle size={32} className="text-slate-600 mb-2" />
          <p className="text-slate-400 font-medium">Document Data Unavailable</p>
        </div>
      )}
      
      <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900 z-0">
        <div className="flex items-center gap-2 text-slate-300">
          <FileText size={18} className="text-purple-500" />
          <h3 className="font-bold text-sm uppercase tracking-wider">Document Intelligence</h3>
        </div>
        {docState?.isAnalyzed && (
          <span className={`font-mono font-bold ${data.cal_doc > 0.7 ? 'text-red-400' : 'text-purple-400'}`}>
            {(data.cal_doc * 100).toFixed(1)}% Risk
          </span>
        )}
      </div>

      <div className="p-6 flex-1 flex flex-col z-0 relative">
        
        {(!docState?.isAnalyzed && !docState?.isAnalyzing) && (
          <div className="absolute inset-0 bg-slate-900/90 z-10 flex flex-col items-center justify-center p-6 text-center">
            <div className="w-12 h-12 bg-purple-500/10 rounded-full flex items-center justify-center mb-4 border border-purple-500/20">
              <FileText size={24} className="text-purple-400" />
            </div>
            <h4 className="text-white font-bold mb-2">Costly Modality</h4>
            <p className="text-slate-400 text-sm mb-6 max-w-xs">
              Document OCR and FinBERT Semantic Analysis consume significant compute. Run only if necessary.
            </p>
            <button 
              onClick={onAnalyzeDocument}
              className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg font-bold transition-colors flex items-center gap-2"
            >
              <PlayCircle size={18} /> Analyze Document
            </button>
          </div>
        )}

        {docState?.isAnalyzing && (
          <div className="absolute inset-0 bg-slate-900 z-10 flex flex-col justify-center p-8 space-y-6">
            <h4 className="text-white font-bold flex items-center gap-2 uppercase tracking-wider mb-2">
              <Loader2 className="animate-spin text-purple-400" size={18} /> Processing Document
            </h4>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
                  <span>OCR Extraction</span>
                  <span>{docState.progress.ocr}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${docState.progress.ocr}%` }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
                  <span>Field Parsing</span>
                  <span>{docState.progress.extraction}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${docState.progress.extraction}%` }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
                  <span>FinBERT Analysis</span>
                  <span>{docState.progress.finbert}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 transition-all duration-300" style={{ width: `${docState.progress.finbert}%` }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
                  <span>Ledger Reconciliation</span>
                  <span>{docState.progress.reconciliation}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 transition-all duration-300" style={{ width: `${docState.progress.reconciliation}%` }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {docState?.isAnalyzed && (
          <>
            <div className="flex justify-between items-center mb-4">
              <p className="text-xs text-slate-500 uppercase font-bold">FinBERT OCR Extractor</p>
              <button 
                onClick={() => setShowOCR(!showOCR)}
                className="flex items-center gap-1 text-[10px] uppercase font-bold text-slate-400 bg-slate-800 px-2 py-1 rounded hover:bg-slate-700"
              >
                {showOCR ? <EyeOff size={12} /> : <Eye size={12} />}
                Toggle OCR
              </button>
            </div>

            <div className="flex-1 bg-white rounded-lg p-4 font-mono text-xs text-slate-800 relative shadow-inner overflow-hidden flex flex-col">
              <div className="text-center font-bold text-sm border-b pb-2 mb-2">
                INVOICE #INV-1938
              </div>
              <div className="space-y-4">
                <div className={`p-1 rounded ${showOCR ? 'border-2 border-green-500 bg-green-500/20' : 'border-2 border-transparent'}`}>
                  <span className="text-slate-500">Vendor:</span> ACME LTD
                </div>
                
                <div className={`p-1 rounded ${showOCR ? (data.cal_doc > 0.7 ? 'border-2 border-red-500 bg-red-500/20' : 'border-2 border-green-500 bg-green-500/20') : 'border-2 border-transparent'}`}>
                  <span className="text-slate-500">Amount:</span> ₹{data.cal_tx > 0.7 ? '482,000' : '71,000'}
                </div>
                
                <div className={`p-1 rounded ${showOCR ? 'border-2 border-green-500 bg-green-500/20' : 'border-2 border-transparent'}`}>
                  <span className="text-slate-500">Date:</span> 07/09/2026
                </div>
              </div>
              
              {data.conflict_tx_doc > 0.2 && isAvailable && (
                <div className="mt-auto pt-4 border-t border-slate-200">
                  <div className="text-red-600 font-bold flex items-center gap-1">
                    Mismatch: Extracted amount contradicts tabular record
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
