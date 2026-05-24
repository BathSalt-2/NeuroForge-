import React, { useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiContext } from '../App';

const USER_ID = 'poc_user_01';

export default function Dashboard() {
  const api = useContext(ApiContext);
  const navigate = useNavigate();
  const [concepts, setConcepts] = useState([]);
  const [paths, setPaths] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [conceptRes, pathRes, profileRes] = await Promise.allSettled([
          fetch(`${api}/api/v1/concepts?limit=8`).then(r => r.json()),
          fetch(`${api}/api/v1/paths?limit=5`).then(r => r.json()),
          fetch(`${api}/api/v1/profiling/users/${USER_ID}/summary`).then(r => r.json()),
        ]);
        if (conceptRes.status === 'fulfilled') setConcepts(conceptRes.value.data || []);
        if (pathRes.status === 'fulfilled') setPaths(pathRes.value.data || []);
        if (profileRes.status === 'fulfilled') setProfile(profileRes.value.summary);
      } catch (e) {
        console.error('Dashboard fetch error:', e);
      } finally {
        setLoading(false);
      }
    })();
  }, [api]);

  if (loading) return <div className="loading"><div className="spinner" /> Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Welcome back 👋</h1>
        <p>Your adaptive learning journey at a glance</p>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-value">{concepts.length}</div>
          <div className="stat-label">Concepts Available</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🛤️</div>
          <div className="stat-value">{paths.length}</div>
          <div className="stat-label">Learning Paths</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-value">∞</div>
          <div className="stat-label">AI Mentor Sessions</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-value">0</div>
          <div className="stat-label">Credentials Earned</div>
        </div>
      </div>

      {/* Quick Actions */}
      <section className="section">
        <h2>Quick Actions</h2>
        <div className="quick-actions">
          <button className="action-card" onClick={() => navigate('/mentor')}>
            <span className="action-icon">🤖</span>
            <span className="action-label">Chat with AI Mentor</span>
            <span className="action-desc">Ask questions, get explanations</span>
          </button>
          <button className="action-card" onClick={() => navigate('/concepts')}>
            <span className="action-icon">📚</span>
            <span className="action-label">Browse Concepts</span>
            <span className="action-desc">Explore the knowledge graph</span>
          </button>
          <button className="action-card" onClick={() => navigate('/paths')}>
            <span className="action-icon">🛤️</span>
            <span className="action-label">Start Learning Path</span>
            <span className="action-desc">Follow structured curriculum</span>
          </button>
        </div>
      </section>

      {/* Learning Profile */}
      {profile && (
        <section className="section">
          <h2>Your Learning Profile</h2>
          <div className="profile-grid">
            <div className="card">
              <h3>🎯 Learning Styles</h3>
              <div className="tag-list">
                {profile.dominantLearningStyles?.map(s => (
                  <span key={s} className="tag">{s}</span>
                ))}
              </div>
            </div>
            <div className="card">
              <h3>💪 Strengths</h3>
              <div className="tag-list">
                {profile.strengths?.map(s => (
                  <span key={s} className="tag tag-success">{s}</span>
                ))}
              </div>
            </div>
            <div className="card">
              <h3>📈 Areas for Growth</h3>
              <div className="tag-list">
                {profile.areasForDevelopment?.map(s => (
                  <span key={s} className="tag tag-warning">{s}</span>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Concept Preview */}
      <section className="section">
        <h2>Explore Concepts</h2>
        <div className="concept-chips">
          {concepts.map(c => (
            <button key={c.conceptId} className="concept-chip" onClick={() => navigate('/concepts')}>
              <span className="chip-name">{c.name}</span>
              <span className={`badge badge-${(c.difficultyLevel || '').toLowerCase()}`}>
                {c.difficultyLevel}
              </span>
            </button>
          ))}
        </div>
      </section>

      <style>{`
        .stats-row {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          margin-bottom: 32px;
        }
        .stat-card {
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
          text-align: center;
        }
        .stat-icon { font-size: 28px; margin-bottom: 8px; }
        .stat-value { font-size: 32px; font-weight: 700; }
        .stat-label { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

        .section { margin-bottom: 32px; }
        .section h2 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }

        .quick-actions {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }
        .action-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          padding: 24px;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          cursor: pointer;
          transition: all 0.15s;
          text-align: center;
          color: inherit;
          font-family: inherit;
        }
        .action-card:hover {
          border-color: var(--accent);
          transform: translateY(-2px);
        }
        .action-icon { font-size: 32px; }
        .action-label { font-size: 15px; font-weight: 600; }
        .action-desc { font-size: 12px; color: var(--text-muted); }

        .profile-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }
        .profile-grid h3 { font-size: 14px; margin-bottom: 12px; }

        .tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag {
          display: inline-block;
          padding: 4px 10px;
          background: var(--accent-light);
          color: var(--accent);
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
        }
        .tag-success { background: rgba(16,185,129,0.15); color: var(--success); }
        .tag-warning { background: rgba(245,158,11,0.15); color: var(--warning); }

        .concept-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }
        .concept-chip {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 14px;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 24px;
          cursor: pointer;
          color: inherit;
          font-family: inherit;
          font-size: 13px;
          transition: all 0.15s;
        }
        .concept-chip:hover {
          border-color: var(--accent);
          background: var(--bg-tertiary);
        }
        .chip-name { font-weight: 500; }

        @media (max-width: 900px) {
          .stats-row { grid-template-columns: repeat(2, 1fr); }
          .quick-actions { grid-template-columns: 1fr; }
          .profile-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
}
