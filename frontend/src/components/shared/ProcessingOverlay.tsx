import type { ProcessingState } from '../../types';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';

interface ProcessingOverlayProps {
  state: ProcessingState;
}

export function ProcessingOverlay({ state }: ProcessingOverlayProps) {
  if (state === 'idle' || state === 'complete') return null;

  const steps = [
    { id: 'loading', label: 'Initializing investigation sandbox' },
    { id: 'transaction-analysis', label: 'Retrieving transaction baseline' },
    { id: 'sequence-analysis', label: 'Computing historical sequence context' },
    { id: 'graph-analysis', label: 'Extracting counterparty graph topology' },
    { id: 'document-analysis', label: 'Executing FinBERT OCR extraction' },
    { id: 'fusion-analysis', label: 'Fusing evidence through meta-model' },
    { id: 'rl-decision', label: 'Querying MaskablePPO policy' },
  ];

  const currentIndex = steps.findIndex(s => s.id === state);

  return (
    <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-700 p-8 rounded-2xl w-full max-w-md shadow-2xl">
        <h3 className="text-lg font-bold text-white mb-6 uppercase tracking-wider flex items-center gap-3">
          <Loader2 className="animate-spin text-blue-500" size={20} />
          Investigation In Progress
        </h3>
        
        <div className="space-y-4">
          {steps.map((step, index) => {
            const isComplete = index < currentIndex;
            const isActive = index === currentIndex;
            
            return (
              <div 
                key={step.id} 
                className={`flex items-center gap-4 text-sm font-medium transition-all duration-300 ${
                  isActive ? 'text-white translate-x-2' : 
                  isComplete ? 'text-green-500' : 
                  'text-slate-600'
                }`}
              >
                {isComplete ? (
                  <CheckCircle2 size={18} className="shrink-0" />
                ) : isActive ? (
                  <Loader2 size={18} className="animate-spin shrink-0 text-blue-500" />
                ) : (
                  <Circle size={18} className="shrink-0" />
                )}
                {step.label}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
