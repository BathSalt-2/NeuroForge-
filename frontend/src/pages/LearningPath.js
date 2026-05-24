import React, { useContext, useEffect, useState } from 'react';
import { ApiContext } from '../App';

const USER_ID = 'poc_user_01';

export default function LearningPath() {
  const api = useContext(ApiContext);
  const [paths, setPaths] = useState([]);
  const [selected, setSelected] = useState(null);
  const [enrollment, setEnrollment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [moduleContent, setModuleContent] = useState(null);
  const [contentLoading, setContentLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${api}/api/v1/paths?limit=20`);
        const data = await res.json();
        setPaths(data.data || []);
        if (data.data?.length > 0) selectPath(data.data[0]);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  const selectPath = async (path) => {
    setSelected(path);
    setModuleContent(null);
    // Check enrollment
    try {
      const res = await fetch(`${api}/api/v1/users/${USER_ID}/paths/${path.pathId}/enrollment`);
      if (res.ok) {
        setEnrollment(await res.json());
      } else {
        setEnrollment(null);
      }
    } catch {
      setEnrollment(null);
    }
  };

  const enroll = async () => {
    if (!selected) return;
    setEnrolling(true);
    try {
      const res = await fetch(`${api}/api/v1/users/${USER_ID}/paths/${selected.pathId}/enroll`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setEnrollment({
          ...data,
          completedModules: [],
          progressPercentage: 0,
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setEnrolling(false);
    }
  };

  const viewModule = async (moduleId) => {
    setContentLoading(true);
    try {
      const res = await fetch(`${api}/api/v1/content/${moduleId}`);
      if (res.ok) setModuleContent(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setContentLoading(false);
    }
  };

  const completeModule = async (moduleId) => {
    if (!selected || !enrollment) return;
    try {
      const res = await fetch(`${api}/api/v1/users/${USER_ID}/paths/${selected.pathId}/progress`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completedModuleId: moduleId }),
      });
      if (res.ok) {
        setEnrollment(await res.json());
      }
    } catch (e) {
      console.error(e);
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

  if (loading) return <div className="loading"><div className="spinner" /> Loading paths...</div>;

  return (
    <div className="learning-paths">
      <div className="page-header">
        <h1>🛤️ Learning Paths</h1>
        <p>Follow structured curricula to master skills from beginner to advanced</p>
      </div>

      <div className="paths-layout">
        {/* Left: Path list */}
        <div className="path-list-panel">
          {paths.map(p => (
            <button
              key={p.pathId}
              className={`path-item ${selected?.pathId === p.pathId ? 'selected' : ''}`}
              onClick={() => selectPath(p)}
            >
              <div className="path-item-name">{p.name}</div>
              <div className="path-item-desc">{p.description?.slice(0, 80)}...</div>
              <div className="path-item-meta">
                {p.moduleSequence?.length || 0} modules
              </div>
            </button>
          ))}
          {paths.length === 0 && (
            <div className="empty-state">No learning paths available</div>
          )}
        </div>

        {/* Right: Path detail */}
        <div className="path-detail-panel">
          {!selected ? (
            <div className="empty-state">
              <div className="icon">🛤️</div>
              <p>Select a learning path</p>
            </div>
          ) : (
            <div className="path-detail">
              <div className="path-header">
                <h2>{selected.name}</h2>
                <p className="path-desc">{selected.description}</p>
                {selected.targetAudience && (
                  <div className="path-audience">
                    <strong>Target audience:</strong> {selected.targetAudience}
                  </div>
                )}
              </div>

              {/* Enrollment / Progress */}
              <div className="enrollment-section">
                {enrollment ? (
                  <div className="enrollment-card">
                    <div className="enrollment-header">
                      <span className={`enrollment-status status-${enrollment.status}`}>
                        {enrollment.status === 'completed' ? '🏆 Completed' : '📖 Enrolled'}
                      </span>
                      <span className="enrollment-progress">
                        {Math.round(enrollment.progressPercentage || 0)}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${enrollment.progressPercentage || 0}%` }} />
                    </div>
                    <div className="enrollment-meta">
                      {enrollment.completedModules?.length || 0} of {selected.moduleSequence?.length || 0} modules completed
                    </div>
                  </div>
                ) : (
                  <button className="btn btn-primary" onClick={enroll} disabled={enrolling}>
                    {enrolling ? 'Enrolling...' : '🚀 Enroll in this Path'}
                  </button>
                )}
              </div>

              {/* Module sequence */}
              <div className="module-sequence">
                <h3>Module Sequence</h3>
                <div className="timeline">
                  {(selected.moduleSequence || []).map((m, i) => {
                    const isCompleted = enrollment?.completedModules?.includes(m.moduleId);
                    const isCurrent = enrollment?.currentModuleId === m.moduleId;
                    return (
                      <div key={m.moduleId} className={`timeline-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}>
                        <div className="timeline-marker">
                          {isCompleted ? '✅' : isCurrent ? '▶️' : <span className="marker-num">{i + 1}</span>}
                        </div>
                        <div className="timeline-content">
                          <div className="timeline-title">
                            {m.moduleId.replace(/^module_/, '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                            {m.isOptional && <span className="optional-badge">Optional</span>}
                          </div>
                          <div className="timeline-actions">
                            <button className="btn btn-sm btn-secondary" onClick={() => viewModule(m.moduleId)}>
                              👁 View
                            </button>
                            {enrollment && !isCompleted && (
                              <button className="btn btn-sm btn-primary" onClick={() => completeModule(m.moduleId)}>
                                ✓ Complete
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Module Content Viewer */}
              {contentLoading && <div className="loading"><div className="spinner" /> Loading module...</div>}
              {moduleContent && !contentLoading && (
                <div className="content-viewer">
                  <div className="content-header">
                    <h3>{moduleIcon(moduleContent.type)} {moduleContent.title}</h3>
                    <button className="btn btn-sm btn-secondary" onClick={() => setModuleContent(null)}>✕ Close</button>
                  </div>
                  <div
                    className="content-body"
                    dangerouslySetInnerHTML={{ __html: moduleContent.contentHtml }}
                  />
                  {moduleContent.quizData && (
                    <div className="quiz-section">
                      <h4>Quiz Questions</h4>
                      {moduleContent.quizData.questions?.map((q, i) => (
                        <div key={q.id} className="quiz-question">
                          <p className="q-text">{i + 1}. {q.text}</p>
                          <div className="q-options">
                            {q.options?.map((opt, j) => (
                              <div key={j} className={`q-option ${j === q.correctIndex ? 'correct' : ''}`}>
                                {String.fromCharCode(65 + j)}. {opt}
                                {j === q.correctIndex && <span className="correct-marker">✓</span>}
                              </div>
                            ))}
                          </div>
                          <p className="q-explanation">💡 {q.explanation}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Skills & Concepts */}
              <div className="path-tags">
                {selected.conceptsTargeted?.length > 0 && (
                  <div>
                    <h4>Concepts Covered</h4>
                    <div className="tag-list">
                      {selected.conceptsTargeted.map(c => (
                        <span key={c} className="tag">{c.replace('concept_', '').replace(/_/g, ' ')}</span>
                      ))}
                    </div>
                  </div>
                )}
                {selected.skillsDeveloped?.length > 0 && (
                  <div>
                    <h4>Skills Developed</h4>
                    <div className="tag-list">
                      {selected.skillsDeveloped.map(s => (
                        <span key={s} className="tag tag-skill">{s.replace('skill_', '').replace(/_/g, ' ')}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .paths-layout {
          display: flex;
          gap: 20px;
          height: calc(100vh - 180px);
        }

        .path-list-panel {
          width: 320px;
          flex-shrink: 0;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .path-item {
          display: block;
          width: 100%;
          text-align: left;
          padding: 16px;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          cursor: pointer;
          transition: all 0.15s;
          color: inherit;
          font-family: inherit;
        }
        .path-item:hover { border-color: var(--accent); }
        .path-item.selected { border-color: var(--accent); background: var(--accent-light); }
        .path-item-name { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
        .path-item-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
        .path-item-meta { font-size: 11px; color: var(--text-muted); }

        .path-detail-panel {
          flex: 1;
          overflow-y: auto;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 28px;
        }

        .path-header { margin-bottom: 20px; }
        .path-header h2 { font-size: 22px; margin-bottom: 8px; }
        .path-desc { color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 8px; }
        .path-audience { font-size: 13px; color: var(--text-muted); }
        .path-audience strong { color: var(--text-secondary); }

        .enrollment-section { margin-bottom: 24px; }
        .enrollment-card {
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          padding: 16px;
        }
        .enrollment-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .enrollment-status { font-weight: 600; font-size: 14px; }
        .status-active { color: var(--info); }
        .status-completed { color: var(--success); }
        .enrollment-progress { font-weight: 700; font-size: 18px; color: var(--accent); }
        .enrollment-meta { font-size: 12px; color: var(--text-muted); margin-top: 8px; }

        .module-sequence { margin-bottom: 28px; }
        .module-sequence h3 { font-size: 16px; margin-bottom: 16px; }

        .timeline { display: flex; flex-direction: column; gap: 0; }
        .timeline-item {
          display: flex;
          gap: 14px;
          padding: 12px 0;
          border-left: 2px solid var(--border);
          margin-left: 17px;
          padding-left: 20px;
          position: relative;
        }
        .timeline-item.completed { border-left-color: var(--success); }
        .timeline-item.current { border-left-color: var(--accent); }
        .timeline-marker {
          position: absolute;
          left: -14px;
          width: 26px;
          height: 26px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
        }
        .marker-num {
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background: var(--bg-tertiary);
          border: 2px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 600;
        }
        .timeline-content { flex: 1; }
        .timeline-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; }
        .optional-badge {
          display: inline-block;
          margin-left: 8px;
          padding: 2px 8px;
          background: var(--bg-tertiary);
          border-radius: 10px;
          font-size: 10px;
          font-weight: 500;
          color: var(--text-muted);
        }
        .timeline-actions { display: flex; gap: 6px; }
        .timeline-item.completed .timeline-title { color: var(--success); }

        .content-viewer {
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 24px;
          margin-bottom: 24px;
        }
        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid var(--border);
        }
        .content-header h3 { font-size: 16px; }
        .content-body { font-size: 14px; line-height: 1.7; color: var(--text-secondary); }
        .content-body h2, .content-body h3, .content-body h4 {
          color: var(--text-primary);
          margin: 16px 0 8px;
        }
        .content-body ul, .content-body ol { margin-left: 20px; margin-bottom: 12px; }
        .content-body li { margin-bottom: 4px; }
        .content-body iframe { border-radius: var(--radius-sm); margin: 12px 0; }

        .quiz-section {
          margin-top: 20px;
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }
        .quiz-section h4 { margin-bottom: 16px; }
        .quiz-question { margin-bottom: 20px; }
        .q-text { font-weight: 600; margin-bottom: 8px; }
        .q-options { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
        .q-option {
          padding: 8px 12px;
          background: var(--bg-tertiary);
          border-radius: var(--radius-sm);
          font-size: 13px;
        }
        .q-option.correct { background: rgba(16,185,129,0.15); color: var(--success); }
        .correct-marker { margin-left: 8px; }
        .q-explanation { font-size: 12px; color: var(--text-muted); font-style: italic; }

        .path-tags { display: flex; flex-direction: column; gap: 16px; }
        .path-tags h4 { font-size: 14px; margin-bottom: 8px; }
        .tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag {
          display: inline-block;
          padding: 4px 12px;
          background: var(--accent-light);
          color: var(--accent);
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
          text-transform: capitalize;
        }
        .tag-skill { background: rgba(16,185,129,0.12); color: var(--success); }
      `}</style>
    </div>
  );
}
