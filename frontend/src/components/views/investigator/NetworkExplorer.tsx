import { ReactFlow, Background, Controls, MiniMap, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Share2 } from 'lucide-react';

const initialNodes = [
  { id: '1', position: { x: 250, y: 100 }, data: { label: 'TXN_f8cbab4c (Core)' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #ef4444', borderRadius: '8px', padding: '10px' } },
  { id: '2', position: { x: 100, y: 250 }, data: { label: 'Account A' }, style: { background: '#0f172a', color: '#cbd5e1', border: '1px solid #334155', borderRadius: '8px', padding: '10px' } },
  { id: '3', position: { x: 400, y: 250 }, data: { label: 'Account B' }, style: { background: '#0f172a', color: '#cbd5e1', border: '1px solid #334155', borderRadius: '8px', padding: '10px' } },
  { id: '4', position: { x: 400, y: 400 }, data: { label: 'TXN_7eccdaf4' }, style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #eab308', borderRadius: '8px', padding: '10px' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#ef4444' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#ef4444' } },
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#3b82f6' } },
];

export function NetworkExplorer() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-full flex flex-col bg-slate-950">
      <div className="p-8 pb-4 border-b border-slate-800 bg-slate-900/50">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2 flex items-center gap-3">
          <Share2 size={28} className="text-blue-500" /> Network Explorer
        </h1>
        <p className="text-slate-400">Interactive relationship graph of highly-connected anomalous entities.</p>
      </div>
      
      <div className="flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-slate-950"
        >
          <Background color="#334155" gap={16} />
          <Controls className="bg-slate-900 border-slate-800 fill-white" />
          <MiniMap 
            className="hidden sm:block"
            nodeColor={(node) => {
              const border = node.style?.border as string | undefined;
              if (border?.includes('ef4444')) return '#ef4444';
              if (border?.includes('eab308')) return '#eab308';
              return '#334155';
            }}
            maskColor="rgba(15, 23, 42, 0.7)"
            style={{ backgroundColor: '#020617', border: '1px solid #1e293b' }}
          />
        </ReactFlow>
      </div>
    </div>
  );
}
