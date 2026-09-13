import type { CandidateCase } from '../../types';
import { Share2, HelpCircle } from 'lucide-react';
import { ReactFlow, Background } from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface GraphCardProps {
  data: CandidateCase;
}

export function GraphCard({ data }: GraphCardProps) {
  const isAvailable = data.graph_available === 1;
  const isHighRisk = data.cal_graph > 0.7;

  // Mock a localized graph topology based on the risk score
  const nodes: Node[] = [
    { id: 'center', position: { x: 150, y: 100 }, data: { label: 'Selected TX' }, style: { background: isHighRisk ? '#ef4444' : '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', padding: '10px', fontSize: '10px', fontWeight: 'bold' } },
    { id: 'src', position: { x: 50, y: 40 }, data: { label: 'Account A' }, style: { background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: '4px', padding: '5px', fontSize: '10px' } },
    { id: 'dst1', position: { x: 250, y: 40 }, data: { label: 'Vendor X' }, style: { background: isHighRisk ? '#7f1d1d' : '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: '4px', padding: '5px', fontSize: '10px' } },
    { id: 'dst2', position: { x: 250, y: 160 }, data: { label: 'Account B' }, style: { background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: '4px', padding: '5px', fontSize: '10px' } },
  ];

  if (isHighRisk) {
    nodes.push({ id: 'shell', position: { x: 350, y: 100 }, data: { label: 'Shell Corp (Flagged)' }, style: { background: '#f59e0b', color: '#000', border: 'none', borderRadius: '4px', padding: '5px', fontSize: '10px', fontWeight: 'bold' } });
  }

  const edges: Edge[] = [
    { id: 'e1', source: 'src', target: 'center', animated: true, style: { stroke: '#475569' } },
    { id: 'e2', source: 'center', target: 'dst1', animated: true, style: { stroke: isHighRisk ? '#ef4444' : '#475569' } },
    { id: 'e3', source: 'center', target: 'dst2', style: { stroke: '#475569' } },
  ];

  if (isHighRisk) {
    edges.push({ id: 'e4', source: 'dst1', target: 'shell', animated: true, style: { stroke: '#f59e0b' } });
  }

  return (
    <div className="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden min-h-[300px] flex flex-col">
      {!isAvailable && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center">
          <HelpCircle size={32} className="text-slate-600 mb-2" />
          <p className="text-slate-400 font-medium">Graph Data Unavailable</p>
        </div>
      )}
      
      <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900 z-0 absolute top-0 left-0 right-0 w-full bg-opacity-90 backdrop-blur">
        <div className="flex items-center gap-2 text-slate-300">
          <Share2 size={18} className="text-amber-500" />
          <h3 className="font-bold text-sm uppercase tracking-wider">Financial Graph ML</h3>
        </div>
        <span className={`font-mono font-bold ${data.cal_graph > 0.7 ? 'text-red-400' : 'text-amber-500'}`}>
          {(data.cal_graph * 100).toFixed(1)}% Risk
        </span>
      </div>

      <div className="flex-1 w-full h-[300px] z-0 pt-16">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="#334155" gap={16} />
        </ReactFlow>
      </div>
    </div>
  );
}
