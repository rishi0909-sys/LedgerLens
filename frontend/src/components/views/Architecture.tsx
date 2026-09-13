import { ReactFlow, Background, Controls } from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export function Architecture() {
  const nodes: Node[] = [
    { id: 'synth', position: { x: 400, y: 50 }, data: { label: 'Phase 1: Synthetic Data Generation' }, style: { width: 250, padding: 15, background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'tx', position: { x: 100, y: 200 }, data: { label: 'Phase 2: Transaction ML (XGBoost)' }, style: { width: 200, padding: 15, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'seq', position: { x: 350, y: 200 }, data: { label: 'Phase 3: Sequence ML (LSTM)' }, style: { width: 200, padding: 15, background: '#10b981', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'graph', position: { x: 600, y: 200 }, data: { label: 'Phase 4: Graph ML (GraphSAGE)' }, style: { width: 200, padding: 15, background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'doc', position: { x: 850, y: 200 }, data: { label: 'Phase 5: Doc CV (FinBERT)' }, style: { width: 200, padding: 15, background: '#a855f7', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'fusion', position: { x: 400, y: 350 }, data: { label: 'Phase 6: Evidence Fusion (Meta-XGBoost)' }, style: { width: 350, padding: 15, background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
    { id: 'rl', position: { x: 400, y: 500 }, data: { label: 'Phase 7: RL Investigation (MaskablePPO)' }, style: { width: 350, padding: 15, background: '#ef4444', color: '#fff', border: 'none', borderRadius: 8, textAlign: 'center', fontWeight: 'bold' } },
  ];

  const edges: Edge[] = [
    { id: 'e-tx', source: 'synth', target: 'tx', animated: true },
    { id: 'e-seq', source: 'synth', target: 'seq', animated: true },
    { id: 'e-graph', source: 'synth', target: 'graph', animated: true },
    { id: 'e-doc', source: 'synth', target: 'doc', animated: true },
    { id: 'f-tx', source: 'tx', target: 'fusion', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 } },
    { id: 'f-seq', source: 'seq', target: 'fusion', animated: true, style: { stroke: '#10b981', strokeWidth: 2 } },
    { id: 'f-graph', source: 'graph', target: 'fusion', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 } },
    { id: 'f-doc', source: 'doc', target: 'fusion', animated: true, style: { stroke: '#a855f7', strokeWidth: 2 } },
    { id: 'f-rl', source: 'fusion', target: 'rl', animated: true, style: { stroke: '#6366f1', strokeWidth: 3 } },
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950">
      <div className="p-8 border-b border-slate-800 shrink-0">
        <h2 className="text-2xl md:text-3xl font-black text-white">System Architecture</h2>
        <p className="text-slate-400 mt-2">Interactive Directed Acyclic Graph (DAG) of the LedgerLens 7-Phase ML Pipeline.</p>
      </div>
      <div className="flex-1">
        <ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.5} maxZoom={1.5}>
          <Background color="#334155" gap={24} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
