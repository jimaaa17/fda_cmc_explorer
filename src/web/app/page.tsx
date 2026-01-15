'use client';

import { useState, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Search, Database, Share2, Info, LayoutGrid, Network } from 'lucide-react';
import styles from './page.module.css';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [facets, setFacets] = useState<any>({});
  const [selectedFilters, setSelectedFilters] = useState<any>({ System: [], Site: [], Risk: [] });
  const [viewMode, setViewMode] = useState<'list' | 'graph'>('list');

  // Graph State
  const [graphData, setGraphData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const fgRef = useRef<any>(null);

  // Initial Data Load (Empty Search to get Facets)
  useEffect(() => {
    executeSearch();
  }, []); // Run once on mount

  const executeSearch = async (overrideQuery?: string) => {
    const q = overrideQuery !== undefined ? overrideQuery : query;
    try {
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          filters: selectedFilters
        })
      });
      const data = await res.json();
      setResults(data.hits.hits || []);
      setFacets(data.aggregations || {});
    } catch (err) {
      console.error("Search Error", err);
    }
  };

  // Re-run search when filters change
  useEffect(() => {
    executeSearch();
  }, [selectedFilters]);

  const toggleFilter = (category: string, value: string) => {
    const current = selectedFilters[category] || [];
    const updated = current.includes(value)
      ? current.filter((i: string) => i !== value)
      : [...current, value];

    setSelectedFilters({ ...selectedFilters, [category]: updated });
  };

  const handleSearchSubmit = (e: any) => {
    e.preventDefault();
    executeSearch();
    setViewMode('list');
  };

  const selectEventForGraph = async (id: string, label: string) => {
    setViewMode('graph');
    // Fetch Graph Data
    try {
      const res = await fetch(`/api/graph?id=${id}`);
      const data = await res.json();

      const bindings = data.results.bindings;
      const nodes: any[] = [{ id: `http://example.org/resource/event/${id}`, name: label, val: 20, color: '#ff3d00' }];
      const links: any[] = [];
      const nodeIds = new Set([nodes[0].id]);

      bindings.forEach((b: any) => {
        const targetId = b.o.value;
        const targetLabel = b.label ? b.label.value : targetId.split('/').pop();
        const type = b.type ? b.type.value : 'Literal';

        let color = '#ccc';
        if (b.p.value.includes('hasFailureType')) color = '#00e676';
        if (b.p.value.includes('mentionsEntity')) color = '#2979ff';

        if (!nodeIds.has(targetId)) {
          nodes.push({ id: targetId, name: targetLabel, val: 10, color, type });
          nodeIds.add(targetId);
        }
        links.push({ source: nodes[0].id, target: targetId });
      });

      setGraphData({ nodes, links });
      setSelectedNode(null);

      // Auto zoom
      setTimeout(() => {
        if (fgRef.current) fgRef.current.zoomToFit(400);
      }, 500);

    } catch (err) {
      console.error(err);
    }
  };

  return (
    <main className={styles.container}>

      {/* Left Sidebar: Filters */}
      <aside className={styles.sidebar}>
        <div className={styles.logoArea}>
          <Database size={20} />
          <span>FDA CMC Explorer</span>
        </div>

        <form onSubmit={handleSearchSubmit} className={styles.searchWrapper}>
          <Search size={16} style={{ position: 'absolute', top: 12, left: 12, color: '#94a3b8' }} />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search..."
            className={styles.searchInput}
          />
        </form>

        {/* Facets */}
        {['System', 'Site', 'Risk'].map(cat => (
          <div key={cat} className={styles.facetGroup}>
            <div className={styles.facetTitle}>{cat}</div>
            <div className={styles.facetList}>
              {facets[cat] && facets[cat].buckets.map((b: any) => (
                <label key={b.key} className={styles.facetItem}>
                  <input
                    type="checkbox"
                    className={styles.facetCheckbox}
                    checked={selectedFilters[cat]?.includes(b.key)}
                    onChange={() => toggleFilter(cat, b.key)}
                  />
                  <span style={{ maxWidth: '180px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={b.key}>
                    {b.key}
                  </span>
                  <span className={styles.facetCount}>{b.doc_count}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </aside>

      {/* Main Content */}
      <section className={styles.mainContent}>
        {/* View Toggles */}
        <div className={styles.modeSwitcher}>
          <div className={`${styles.modeButton} ${viewMode === 'list' ? styles.active : ''}`} onClick={() => setViewMode('list')}>
            <LayoutGrid size={16} style={{ display: 'inline', marginRight: 4 }} /> Grid
          </div>
          <div className={`${styles.modeButton} ${viewMode === 'graph' ? styles.active : ''}`} onClick={() => setViewMode('graph')}>
            <Network size={16} style={{ display: 'inline', marginRight: 4 }} /> Graph
          </div>
        </div>

        {viewMode === 'list' ? (
          <div className={styles.resultsGrid}>
            {results.map((hit: any) => (
              <div key={hit._id} className={styles.resultCard} onClick={() => selectEventForGraph(hit._id, hit._source.recalling_firm)}>
                <div className={styles.cardHeader}>
                  <span className={styles.cardTag}>{hit._source.classification}</span>
                  <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{hit._source.report_date}</span>
                </div>
                <div className={styles.cardTitle}>{hit._source.recalling_firm}</div>
                <div className={styles.cardMeta}>
                  <span>{hit._source.state}, {hit._source.country}</span>
                </div>
                <div className={styles.cardSnippet}>
                  {hit._source.reason_for_recall}
                </div>
                <div style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                  <span style={{ fontSize: '0.75rem', color: '#f472b6' }}>{hit._source.failure_type}</span>
                </div>
              </div>
            ))}
            {results.length === 0 && <div style={{ width: '100%', textAlign: 'center', color: '#64748b' }}>No results found.</div>}
          </div>
        ) : (
          <div className={styles.graphContainer}>
            <ForceGraph2D
              ref={fgRef}
              graphData={graphData}
              nodeLabel="name"
              nodeColor="color"
              nodeRelSize={6}
              linkColor={() => '#334155'}
              backgroundColor="#0f172a"
              onNodeClick={(node) => {
                setSelectedNode(node);
                fgRef.current.centerAt(node.x, node.y, 1000);
              }}
            />
          </div>
        )}
      </section>

      {/* Right Drawer: Details */}
      {selectedNode && (
        <aside className={styles.detailsPanel}>
          <div className={styles.detailsHeader}>
            <h2 className={styles.detailsTitle}>{selectedNode.name}</h2>
            <div className={styles.detailsSubtitle}>{selectedNode.type}</div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            <div className={styles.badge}>{selectedNode.id.split('/').pop()}</div>
            <p style={{ fontSize: '0.9rem', lineHeight: '1.5', color: '#cbd5e1' }}>
              Knowledge Graph Node.
            </p>
          </div>

          {selectedNode.id && selectedNode.id.includes('/fda/quality/failure_type/') && (
            <a
              href={`${process.env.NEXT_PUBLIC_SKOSMOS_URL || 'http://localhost:80'}/fda/en/page/?uri=${encodeURIComponent(selectedNode.id)}`}
              target="_blank"
              className={styles.skosLink}
            >
              Open in Skosmos
            </a>
          )}

          <button
            onClick={() => setSelectedNode(null)}
            style={{ marginTop: '0.5rem', width: '100%', padding: '0.75rem', background: 'transparent', border: '1px solid #334155', borderRadius: '8px', color: '#94a3b8', cursor: 'pointer' }}
          >
            Close
          </button>
        </aside>
      )}
    </main>
  );
}
