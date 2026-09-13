import { BarChart2, LineChart, PieChart } from 'lucide-react';

export function EvaluationView() {
  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 p-4 md:p-8 lg:p-12">
      <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        <section className="space-y-4 border-b border-slate-800 pb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
            <BarChart2 size={16} /> METRICS & EVALUATION
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white">
            Model Evaluation
          </h1>
          <p className="text-lg text-slate-400 max-w-3xl leading-relaxed">
            Review performance metrics, benchmark results, and calibration data for LedgerLens AI models.
          </p>
        </section>

        <section className="flex flex-col items-center justify-center py-32 text-slate-500 space-y-4">
          <div className="flex gap-4 mb-4 opacity-50">
            <LineChart size={32} />
            <PieChart size={32} />
            <BarChart2 size={32} />
          </div>
          <p className="text-lg">Evaluation metrics are currently unavailable.</p>
          <p className="text-sm text-slate-600">Run an evaluation pipeline to populate these dashboards.</p>
        </section>
      </div>
    </div>
  );
}
