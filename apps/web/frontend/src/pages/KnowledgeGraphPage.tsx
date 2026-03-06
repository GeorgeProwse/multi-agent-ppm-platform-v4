import { useCallback, useEffect, useMemo, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import { RecommendationSidebar } from '@/components/knowledge/RecommendationSidebar';
import styles from './KnowledgeGraphPage.module.css';

interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  metadata: Record<string, unknown>;
}

interface GraphEdge {
  source: string;
  target: string;
  edge_type: string;
}

interface Recommendation {
  recommendation_id: string;
  title: string;
  description: string;
  priority: string;
  source_lesson_id: string;
  source_lesson_title: string;
  actionable_text: string;
}

interface Pattern {
  pattern_id: string;
  title: string;
  description: string;
  occurrences: number;
  severity: string;
}

const NODE_COLORS: Record<string, string> = {
  lesson: '#22c55e',
  risk: '#ef4444',
  decision: '#3b82f6',
  project: '#6b7280',
  entity: '#f59e0b',
};

const NODE_SHAPES: Record<string, string> = {
  lesson: 'circle',
  risk: 'triangle',
  decision: 'diamond',
  project: 'square',
  entity: 'hexagon',
};

export default function KnowledgeGraphPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [graphData, patternData, recData] = await Promise.all([
        requestJson<{ nodes: GraphNode[]; edges: GraphEdge[] }>('/api/knowledge/graph'),
        requestJson<Pattern[]>('/api/knowledge/patterns'),
        requestJson<Recommendation[]>('/api/knowledge/recommendations', {
          method: 'POST',
          body: JSON.stringify({ project_id: 'default', context_type: 'general' }),
        }),
      ]);
      setNodes(graphData.nodes);
      setEdges(graphData.edges);
      setPatterns(patternData);
      setRecommendations(recData);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filteredNodes = useMemo(() =>
    filterType ? nodes.filter(n => n.node_type === filterType) : nodes,
    [nodes, filterType]
  );

  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

  const nodeTypes = [...new Set(nodes.map(n => n.node_type))];

  // Simple force-like layout positions (deterministic for demo)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const cx = 400, cy = 300, radius = 200;
    filteredNodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / filteredNodes.length;
      positions[node.id] = {
        x: cx + radius * Math.cos(angle) + (i % 3) * 30,
        y: cy + radius * Math.sin(angle) + (i % 2) * 20,
      };
    });
    return positions;
  }, [filteredNodes]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Knowledge Graph</h1>
        <div className={styles.filters}>
          <button className={`${styles.filterBtn} ${!filterType ? styles.filterActive : ''}`} onClick={() => setFilterType('')}>All</button>
          {nodeTypes.map(t => (
            <button key={t} className={`${styles.filterBtn} ${filterType === t ? styles.filterActive : ''}`} onClick={() => setFilterType(t)} style={{ borderColor: NODE_COLORS[t] }}>
              {t}
            </button>
          ))}
        </div>
      </header>

      <div className={styles.layout}>
        <div className={styles.graphContainer}>
          <svg width="100%" height="600" viewBox="0 0 800 600">
            {/* Edges */}
            {filteredEdges.map((e, i) => {
              const from = nodePositions[e.source];
              const to = nodePositions[e.target];
              if (!from || !to) return null;
              return (
                <line key={i} x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                  stroke="#d1d5db" strokeWidth="1.5" opacity="0.6" />
              );
            })}
            {/* Nodes */}
            {filteredNodes.map(node => {
              const pos = nodePositions[node.id];
              if (!pos) return null;
              const color = NODE_COLORS[node.node_type] || '#6b7280';
              const isSelected = selectedNode?.id === node.id;
              return (
                <g key={node.id} onClick={() => setSelectedNode(node)} style={{ cursor: 'pointer' }}>
                  <circle cx={pos.x} cy={pos.y} r={isSelected ? 22 : 18}
                    fill={color} opacity={isSelected ? 1 : 0.8}
                    stroke={isSelected ? '#000' : 'none'} strokeWidth={2} />
                  <text x={pos.x} y={pos.y + 30} textAnchor="middle" fontSize="10" fill="#374151">
                    {node.label.length > 20 ? node.label.slice(0, 20) + '...' : node.label}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className={styles.legend}>
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <span key={type} className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: color }} />
                {type}
              </span>
            ))}
          </div>
        </div>

        <aside className={styles.sidebar}>
          {selectedNode && (
            <div className={styles.nodeDetail}>
              <h3>{selectedNode.label}</h3>
              <span className={styles.nodeType} style={{ background: NODE_COLORS[selectedNode.node_type] }}>{selectedNode.node_type}</span>
              <pre className={styles.nodeMeta}>{JSON.stringify(selectedNode.metadata, null, 2)}</pre>
            </div>
          )}

          {patterns.length > 0 && (
            <div className={styles.patternsSection}>
              <h3>Detected Patterns</h3>
              {patterns.map(p => (
                <div key={p.pattern_id} className={styles.patternCard}>
                  <strong>{p.title}</strong>
                  <p>{p.description}</p>
                  <span className={`${styles.severityBadge} ${styles[`sev-${p.severity}`]}`}>{p.severity} | {p.occurrences} occurrences</span>
                </div>
              ))}
            </div>
          )}

          <RecommendationSidebar
            recommendations={recommendations}
            onSelectSource={(id) => setSelectedNode(nodes.find(n => n.id === id) || null)}
          />
        </aside>
      </div>
    </div>
  );
}
