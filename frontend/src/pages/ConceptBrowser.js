import React, { useContext, useEffect, useState } from 'react';
import { ApiContext } from '../App';

export default function ConceptBrowser() {
  const api = useContext(ApiContext);
  const [concepts, setConcepts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [prerequisites, setPrerequisites] = useState([]);
  const [related, setRelated] = useState([]);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${api}/api/v1/concepts?limit=50`);
        const data = await res.json();
        setConcepts(data.data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  const selectConcept = async (concept) => {
    setSelected(concept);
    setDetailLoading(true);
    try {
      const [preRes, relRes, modRes] = await Promise.allSettled([
        fetch(`${api}/api/v1/concepts/${concept.conceptId}/prerequisites`).then(r => r.json()),
        fetch(`${api}/api/v1/concepts/${concept.conceptId}/related`).then(r => r.json()),
        fetch(`${api}/api/v1/concepts/${concept.conceptId}/modules`).then(r => r.json()),
      ]);
      setPrerequisites(preRes.status === 'fulfilled' ? preRes.value : []);
      setRelated(relRes.status === 'fulfilled' ? relRes.value : []);
      setModules(modRes.status === 'fulfilled' ? modRes.value : []);
    } catch (e) {
      console.error(e);
    } finally {
      setDetailLoading(false);
    }
  };

  const filtered = concepts.filter(c =>
    c.name.toLowerCase().includes(filter.toLowerCase()) ||
    (c.domain || '').toLowerCase().includes(filter.toLowerCase())
  );

  const badgeClass = (level) => {
    switch ((level || '').toLowerCase()) {
      case 'beginner': return 'badge-beginner';
      case 'intermediate': return 'badge-intermediate';
      case 'advanced': return 'badge-advanced';
      default: return '';
    }
  };

  const moduleIcon = (type) => {
    switch ((type || '').toUpperCase()) {
      case 'VIDEO': return '🎬';
      case 'ARTICLE': return '📝';
      case 'QUIZ': return '❓';
      case 'INTERACTIVE_SIMULATION': return '🖥️';
      default: return '📄';
    }
  };

  if (loading) return <div className="loading"><div className="spinner" /> Loading concepts...</div>;

  return (
    <div className="concept-browser">
      <div className="page-header">
        <h1>📚 Knowledge Graph Explorer</h1>
        <p>Browse concepts, their relationships, and available learning modules</p>
      </div>

      <div className="browser-layout">
        {/* Left: Concept list */}
        <div className="concept-list-panel">
          <input
            type="text"
            placeholder="Search concepts..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{ marginBottom: 12 }}
          />
          <div className="concept-list">
            {filtered.map(c => (
              <button
                key={c.conceptId}
                className={`concept-item ${selected?.conceptId === c.conceptId ? 'selected' : ''}`}
                onClick={() => selectConcept(c)}
              >
                <div className="concept-item-name">{c.name}</div>
                <div className="concept-item-meta">
                  <span className={`badge ${badgeClass(c.difficultyLevel)}`}>{c.difficultyLevel}</span>
                  <span className="concept-domain">{c.domain}</span>
                </div>
              </button>
            ))}
            {filtered.length === 0 && (
              <div className="empty-state">No concepts found</div>
            )}
          </div>
        </div>

        {/* Right: Detail */}
        <div className="concept-detail-panel">
          {!selected ? (
            <div className="empty-state">
              <div className="icon">🔍</div>
              <p>Select a concept to explore its details, prerequisites, and learning modules</p>
            </div>
          ) : detailLoading ? (
            <div className="loading"><div className="spinner" /> Loading details...</div>
          ) : (
            <div className="concept-detail">
              <div className="detail-header">
                <h2>{selected.name}</h2>
                <div className="detail-badges">
                  <span className={`badge ${badgeClass(selected.difficultyLevel)}`}>
                    {selected.difficultyLevel}
                  </span>
                  <span className="badge" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    {selected.domain} › {selected.subDomain}
                  </span>
                </div>
              </div>

              <p className="detail-desc">{selected.description}</p>

              {selected.keywords?.length > 0 && (
                <div className="keyword-tags">
                  {selected.keywords.map(k => (
                    <span key={k} className="keyword-tag">{k}</span>
                  ))}
                </div>
              )}

              {/* Prerequisites */}
              <div className="detail-section">
                <h3>🔗 Prerequisites</h3>
                {prerequisites.length === 0 ? (
                  <p className="subtle">No prerequisites — start here!</p>
                ) : (
                  <div className="relation-list">
                    {prerequisites.map(p => (
                      <button
                        key={p.conceptId}
                        className="relation-chip"
                        onClick={() => selectConcept(p)}
                      >
                        {p.name}
                        <span className={`badge badge-sm ${badgeClass(p.difficultyLevel)}`}>
                          {p.difficultyLevel}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Related */}
              <div className="detail-section">
                <h3>🌐 Related Concepts</h3>
                {related.length === 0 ? (
                  <p className="subtle">No related concepts found</p>
                ) : (
                  <div className="relation-list">
                    {related.map(r => (
                      <button
                        key={r.conceptId}
                        className="relation-chip"
                        onClick={() => selectConcept(r)}
                      >
                        {r.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Modules */}
              <div className="detail-section">
                <h3>📦 Learning Modules</h3>
                {modules.length === 0 ? (
                  <p className="subtle">No modules available for this concept yet</p>
                ) : (
                  <div className="module-list">
                    {modules.map(m => (
                      <div key={m.moduleId} className="module-card">
                        <span className="module-icon">{moduleIcon(m.type)}</span>
                        <div className="module-info">
                          <div className="module-title">{m.title}</div>
                          <div className="module-meta">
                            <span className={`badge badge-${(m.type || '').toLowerCase().replace('_', '-')}`}>
                              {m.type}
                            </span>
                            {m.estimatedDurationMinutes && (
                              <span className="module-duration">⏱ {m.estimatedDurationMinutes} min</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .browser-layout {
          display: flex;
          gap: 20px;
          height: calc(100vh - 180px);
        }

        .concept-list-panel {
          width: 300px;
          flex-shrink: 0;
          display: flex;
          flex-direction: column;
        }
        .concept-list {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .concept-item {
          display: block;
          width: 100%;
          text-align: left;
          padding: 12px 14px;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all 0.15s;
          color: inherit;
          font-family: inherit;
        }
        .concept-item:hover { border-color: var(--accent); }
        .concept-item.selected {
          border-color: var(--accent);
          background: var(--accent-light);
        }
        .concept-item-name { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
        .concept-item-meta { display: flex; align-items: center; gap: 8px; }
        .concept-domain { font-size: 11px; color: var(--text-muted); }

        .concept-detail-panel {
          flex: 1;
          overflow-y: auto;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 24px;
        }

        .detail-header { margin-bottom: 16px; }
        .detail-header h2 { font-size: 22px; margin-bottom: 8px; }
        .detail-badges { display: flex; gap: 8px; flex-wrap: wrap; }
        .detail-desc { color: var(--text-secondary); font-size: 14px; line-height: 1.7; margin-bottom: 16px; }

        .keyword-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 20px; }
        .keyword-tag {
          padding: 3px 10px;
          background: var(--bg-tertiary);
          border-radius: 12px;
          font-size: 11px;
          color: var(--text-muted);
        }

        .detail-section { margin-bottom: 24px; }
        .detail-section h3 { font-size: 15px; margin-bottom: 12px; }
        .subtle { color: var(--text-muted); font-size: 13px; font-style: italic; }

        .relation-list { display: flex; flex-wrap: wrap; gap: 8px; }
        .relation-chip {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 14px;
          background: var(--bg-tertiary);
          border: 1px solid var(--border);
          border-radius: 20px;
          font-family: inherit;
          font-size: 13px;
          color: var(--text-primary);
          cursor: pointer;
          transition: all 0.15s;
        }
        .relation-chip:hover { border-color: var(--accent); color: var(--accent); }
        .badge-sm { font-size: 10px; padding: 1px 6px; }

        .module-list { display: flex; flex-direction: column; gap: 8px; }
        .module-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 14px;
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
        }
        .module-icon { font-size: 24px; }
        .module-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
        .module-meta { display: flex; align-items: center; gap: 8px; }
        .module-duration { font-size: 12px; color: var(--text-muted); }
      `}</style>
    </div>
  );
}
