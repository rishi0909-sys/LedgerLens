import { useState } from 'react';
import { FileText, Cpu, Layout, Image as ImageIcon, Search, Activity, AlignRight, Share2, Layers, CheckCircle2 } from 'lucide-react';

export function DocumentForensics() {
  const [activeTab, setActiveTab] = useState<'WHY' | 'HOW' | 'WHEN' | 'IF'>('WHY');
  const [activeStage, setActiveStage] = useState<number>(0);
  const [pipelineState, setPipelineState] = useState<'IDLE' | 'PROCESSING' | 'COMPLETE'>('IDLE');
  const [processingIndex, setProcessingIndex] = useState<number>(-1);

  const runPipeline = async () => {
    setPipelineState('PROCESSING');
    for (let i = 0; i < pipelineStages.length; i++) {
      setProcessingIndex(i);
      setActiveStage(i);
      await new Promise(r => setTimeout(r, 600)); // Simulate delay
    }
    setPipelineState('COMPLETE');
    setProcessingIndex(-1);
  };

  const pipelineStages = [
    { id: 'image', label: 'Image', icon: ImageIcon, desc: 'Original scanned financial document or invoice.', model: 'N/A', latency: '12ms', input: 'Pixels', output: 'Raw Image Array', purpose: 'Capture visual evidence.' },
    { id: 'ocr', label: 'OCR', icon: AlignRight, desc: 'Tesseract optical character recognition extracts raw text.', model: 'Tesseract v5', latency: '420ms', input: 'Raw Image', output: 'Text String', purpose: 'Convert image to machine-readable text.' },
    { id: 'extract', label: 'Extraction', icon: Layout, desc: 'Heuristic parsing of key-value pairs (Amount, Date, Vendor).', model: 'Regex/Rules', latency: '15ms', input: 'Text String', output: 'JSON Key-Values', purpose: 'Extract structured metadata from unstructured text.' },
    { id: 'embed', label: 'FinBERT', icon: Cpu, desc: 'FinBERT tokenizes and generates a 768-dimensional semantic embedding.', model: 'ProsusAI/finbert', latency: '850ms', input: 'OCR Text', output: '768-dimensional embedding', purpose: 'Financial-language representation.' },
    { id: 'recon', label: 'Reconciliation', icon: Share2, desc: 'Extracted fields are compared against structured ledger data.', model: 'Deterministic', latency: '5ms', input: 'JSON Key-Values + Ledger', output: 'Conflict Score', purpose: 'Identify cross-modal discrepancies.' },
    { id: 'evidence', label: 'Evidence', icon: Activity, desc: 'Semantic anomaly score is produced for the fusion layer.', model: 'Cosine Similarity', latency: '2ms', input: 'Conflict Score + Embedding', output: 'Final Anomaly Score', purpose: 'Feed the RL policy.' }
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12">
      <div className="max-w-6xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        {/* Header */}
        <section className="space-y-4 border-b border-slate-800 pb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-sm font-medium">
            <FileText size={16} /> NLP DOCUMENT INTELLIGENCE
          </div>
          <h1 className="text-2xl md:text-4xl font-black tracking-tight text-white">
            From pixels → language → evidence
          </h1>
          <p className="text-lg text-slate-400 max-w-3xl leading-relaxed">
            LedgerLens leverages Computer Vision and Natural Language Processing (NLP) to extract, embed, and reconcile unstructured evidence. Explore the pipeline below.
          </p>
        </section>

        {/* Educational Tabs */}
        <section>
          <div className="flex gap-4 border-b border-slate-800 mb-8">
            {['WHY', 'HOW', 'WHEN', 'IF'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`pb-4 px-2 font-bold tracking-widest text-sm transition-colors border-b-2 ${
                  activeTab === tab ? 'text-purple-400 border-purple-400' : 'text-slate-500 border-transparent hover:text-slate-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 md:p-8 min-h-[200px]">
            {activeTab === 'WHY' && (
              <div className="space-y-4 animate-in fade-in">
                <h3 className="text-xl font-bold text-white">Why does LedgerLens need NLP?</h3>
                <p className="text-slate-300 leading-relaxed max-w-4xl">
                  Structured transaction data tells us <em>what</em> moved through the ledger. However, fraudsters often manipulate structured fields to blend in. 
                  NLP lets LedgerLens analyze the language contained in supporting financial documents (like invoices or receipts). By semantically comparing the document text against the structured transaction, we can detect subtle obfuscation tactics that a purely tabular model would miss.
                </p>
              </div>
            )}
            
            {activeTab === 'HOW' && (
              <div className="space-y-6 animate-in fade-in">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-white">Interactive Processing Pipeline</h3>
                  <button 
                    onClick={runPipeline}
                    disabled={pipelineState === 'PROCESSING'}
                    className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-white px-4 py-2 rounded-lg font-bold text-sm transition-colors"
                  >
                    {pipelineState === 'PROCESSING' ? 'Running Pipeline...' : 'RUN DOCUMENT ANALYSIS'}
                  </button>
                </div>
                <div className="flex items-center justify-between relative">
                  <div className="absolute left-0 right-0 h-1 bg-slate-800 top-1/2 -translate-y-1/2 z-0" />
                  {pipelineStages.map((stage, idx) => (
                    <button
                      key={stage.id}
                      onClick={() => setActiveStage(idx)}
                      className={`relative z-10 flex flex-col items-center gap-3 w-32 ${idx === activeStage ? 'scale-110' : 'hover:scale-105'} transition-all`}
                    >
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-lg ${
                        pipelineState === 'COMPLETE' || idx < processingIndex
                          ? 'bg-emerald-900/20 border-emerald-500 text-emerald-400'
                          : idx === activeStage 
                          ? 'bg-purple-600 border-purple-400 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)]' 
                          : 'bg-slate-950 border-slate-700 text-slate-400'
                      }`}>
                        {pipelineState === 'COMPLETE' || idx < processingIndex ? <CheckCircle2 size={20} /> : <stage.icon size={20} className={idx === processingIndex ? 'animate-pulse' : ''} />}
                      </div>
                      <span className={`text-[10px] font-bold uppercase tracking-wider text-center ${
                        pipelineState === 'COMPLETE' || idx < processingIndex ? 'text-emerald-400' :
                        idx === activeStage ? 'text-purple-300' : 'text-slate-500'}`}>
                        {stage.label}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="mt-8 bg-slate-950 border border-slate-800 rounded-xl p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-xs uppercase font-bold tracking-widest text-slate-500 mb-4">Stage Execution</h4>
                    <p className="text-white font-medium text-lg mb-2">{pipelineStages[activeStage].label}</p>
                    <p className="text-slate-400 text-sm">{pipelineStages[activeStage].desc}</p>
                  </div>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Model / Method</p>
                        <p className="font-mono text-sm text-purple-400">{pipelineStages[activeStage].model}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Latency</p>
                        <p className="font-mono text-sm text-slate-300">{pipelineStages[activeStage].latency}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Input</p>
                        <p className="font-mono text-sm text-slate-300">{pipelineStages[activeStage].input}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Output</p>
                        <p className="font-mono text-sm text-slate-300">{pipelineStages[activeStage].output}</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Purpose</p>
                        <p className="font-mono text-sm text-slate-300">{pipelineStages[activeStage].purpose}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'WHEN' && (
              <div className="space-y-4 animate-in fade-in">
                <h3 className="text-xl font-bold text-white">Resource-Aware Invocation</h3>
                <p className="text-slate-300 leading-relaxed max-w-4xl">
                  Document analysis is computationally expensive compared to tabular baselines. 
                  It is invoked only when transaction-level evidence is ambiguous (yielding a moderate risk score) 
                  or when a supporting invoice contains information unavailable in structured records. 
                  This selective execution is managed by the RL policy to preserve the investigation budget.
                </p>
              </div>
            )}

            {activeTab === 'IF' && (
              <div className="space-y-6 animate-in fade-in">
                <h3 className="text-xl font-bold text-white">Scenario Evaluation</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <p className="font-mono text-xs text-purple-400 mb-2">IF invoice_amount != ledger_amount</p>
                    <p className="text-sm text-slate-300">Produce reconciliation anomaly signal for Fusion layer.</p>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <p className="font-mono text-xs text-purple-400 mb-2">IF vendor_language ≈ known_fraud_invoice</p>
                    <p className="text-sm text-slate-300">Produce semantic similarity anomaly signal.</p>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <p className="font-mono text-xs text-purple-400 mb-2">IF ocr_confidence &lt; 0.6</p>
                    <p className="text-sm text-slate-300">Reduce document modality confidence to prevent false positives.</p>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <p className="font-mono text-xs text-purple-400 mb-2">IF document_unavailable</p>
                    <p className="text-sm text-slate-300">Preserve missing-modality state; rely on Graph/Sequence context.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* NLP Comparison Tool */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Layers size={24} className="text-purple-500" /> Document Comparison Mode
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-wider border-b border-slate-800 pb-2">Document A (INV-1938)</h3>
              <div className="font-mono text-sm space-y-2 text-slate-300">
                <p><span className="text-slate-500">Vendor:</span> ACME LTD</p>
                <p><span className="text-slate-500">Amount:</span> ₹482,000</p>
                <p><span className="text-slate-500">Date:</span> 07/09/2026</p>
              </div>
            </div>
            
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-wider border-b border-slate-800 pb-2">Document B (INV-1941)</h3>
              <div className="font-mono text-sm space-y-2 text-slate-300">
                <p><span className="text-slate-500">Vendor:</span> ACME LTD</p>
                <p><span className="text-slate-500">Amount:</span> ₹482,000</p>
                <p><span className="text-slate-500">Date:</span> 14/09/2026</p>
              </div>
            </div>

            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-6 flex flex-col justify-center text-center">
              <p className="text-xs uppercase font-bold text-purple-400 mb-2">Semantic Similarity</p>
              <p className="text-4xl md:text-5xl font-black text-purple-400 mb-4 drop-shadow-[0_0_15px_rgba(168,85,247,0.4)]">94%</p>
              <div className="bg-purple-950 border border-purple-800 text-purple-200 text-xs px-3 py-2 rounded">
                High probability of reused invoice template for duplicate billing.
              </div>
            </div>
          </div>
        </section>

        {/* Semantic Search */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-4 md:p-8">
           <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-6">
            <Search size={20} className="text-blue-400" /> Semantic Document Search
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <input 
              type="text" 
              className="flex-1 min-w-0 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white outline-none focus:border-blue-500 transition-colors"
              placeholder="e.g. Find invoices mentioning emergency consulting..."
              defaultValue="Find invoices mentioning emergency consulting"
            />
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold shrink-0">Search (pgvector)</button>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="font-mono text-sm text-slate-300">INV-1938</span>
              <span className="text-sm font-bold text-blue-400">similarity 0.91</span>
            </div>
            <div className="flex justify-between items-center bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="font-mono text-sm text-slate-300">INV-1821</span>
              <span className="text-sm font-bold text-slate-400">similarity 0.84</span>
            </div>
            <div className="flex justify-between items-center bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="font-mono text-sm text-slate-300">INV-1402</span>
              <span className="text-sm font-bold text-slate-500">similarity 0.72</span>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
