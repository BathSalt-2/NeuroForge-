import React, { useContext, useState, useRef, useEffect } from 'react';
import { ApiContext } from '../App';

const USER_ID = 'poc_user_01';

export default function MentorChat() {
  const api = useContext(ApiContext);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [persona, setPersona] = useState('default');
  const [conversationId, setConversationId] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text }]);
    setLoading(true);

    try {
      const res = await fetch(`${api}/api/v1/mentor/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: USER_ID,
          text,
          conversationId,
          persona,
        }),
      });
      const data = await res.json();
      if (data.conversationId) setConversationId(data.conversationId);

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: data.responseText || data.detail || 'No response received.',
          suggestedActions: data.suggestedActions || [],
        },
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', text: `⚠️ Error: ${e.message}. Make sure the AI Mentor and Ollama services are running (Gemma 4 E4B model).` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggested = (action) => {
    if (action.type === 'VIEW_CONCEPT') {
      setInput(`Tell me about ${action.label.replace('Explore: ', '')}`);
    } else if (action.type === 'VIEW_MODULE') {
      setInput(`Can you summarize the module "${action.label.replace('View: ', '')}"?`);
    }
  };

  return (
    <div className="mentor-chat">
      <div className="page-header">
        <h1>🤖 AI Mentor</h1>
        <p>Your personal learning companion — powered by LLM + Knowledge Graph</p>
      </div>

      {/* Persona Selector */}
      <div className="persona-bar">
        {['default', 'socratic', 'coach', 'expert'].map(p => (
          <button
            key={p}
            className={`persona-btn ${persona === p ? 'active' : ''}`}
            onClick={() => setPersona(p)}
          >
            {p === 'default' ? '🧠 Adaptive' : p === 'socratic' ? '❓ Socratic' : p === 'coach' ? '💪 Coach' : '🎓 Expert'}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="chat-area">
        {messages.length === 0 && (
          <div className="welcome">
            <div className="welcome-icon">🧠</div>
            <h2>Hello! I'm your NeuroForge AI Mentor</h2>
            <p>Ask me about any concept — I'll use the Knowledge Graph to give you context-rich answers.</p>
            <div className="suggestions">
              <button onClick={() => setInput('What is machine learning?')}>What is machine learning?</button>
              <button onClick={() => setInput('Explain neural networks')}>Explain neural networks</button>
              <button onClick={() => setInput('Help me learn Python')}>Help me learn Python</button>
              <button onClick={() => setInput('What concepts should I learn first?')}>Where should I start?</button>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? 'You' : '🤖'}
            </div>
            <div className="message-body">
              <div className="message-text">{msg.text}</div>
              {msg.suggestedActions?.length > 0 && (
                <div className="suggested-actions">
                  {msg.suggestedActions.map((a, j) => (
                    <button key={j} className="btn btn-sm btn-secondary" onClick={() => handleSuggested(a)}>
                      {a.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-body">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <div className="input-row">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask your AI Mentor anything..."
            rows={1}
          />
          <button className="btn btn-primary send-btn" onClick={sendMessage} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>

      <style>{`
        .mentor-chat {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 64px);
        }

        .persona-bar {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
        }
        .persona-btn {
          padding: 6px 14px;
          border: 1px solid var(--border);
          border-radius: 20px;
          background: var(--bg-secondary);
          color: var(--text-secondary);
          font-family: inherit;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.15s;
        }
        .persona-btn:hover { border-color: var(--accent); }
        .persona-btn.active {
          background: var(--accent-light);
          color: var(--accent);
          border-color: var(--accent);
        }

        .chat-area {
          flex: 1;
          overflow-y: auto;
          padding-bottom: 16px;
        }

        .welcome {
          text-align: center;
          padding: 60px 20px;
        }
        .welcome-icon { font-size: 56px; margin-bottom: 16px; }
        .welcome h2 { font-size: 22px; margin-bottom: 8px; }
        .welcome p { color: var(--text-secondary); margin-bottom: 24px; }
        .suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          justify-content: center;
        }
        .suggestions button {
          padding: 8px 16px;
          border: 1px solid var(--border);
          border-radius: 20px;
          background: var(--bg-secondary);
          color: var(--text-primary);
          font-family: inherit;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.15s;
        }
        .suggestions button:hover { border-color: var(--accent); }

        .message {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
          align-items: flex-start;
        }
        .message-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 600;
          flex-shrink: 0;
        }
        .message.user .message-avatar {
          background: var(--accent);
          color: white;
          font-size: 11px;
        }
        .message.assistant .message-avatar {
          background: var(--bg-tertiary);
          font-size: 18px;
        }
        .message-body { flex: 1; min-width: 0; }
        .message-text {
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 12px 16px;
          font-size: 14px;
          line-height: 1.6;
          white-space: pre-wrap;
          word-wrap: break-word;
        }
        .message.user .message-text {
          background: var(--accent-light);
          border-color: transparent;
        }
        .suggested-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 8px;
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 12px 16px;
          background: var(--bg-secondary);
          border-radius: var(--radius);
          border: 1px solid var(--border);
        }
        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: var(--text-muted);
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
          0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
          30% { opacity: 1; transform: translateY(-4px); }
        }

        .chat-input-area {
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }
        .input-row {
          display: flex;
          gap: 10px;
          align-items: flex-end;
        }
        .input-row textarea {
          flex: 1;
          resize: none;
          min-height: 42px;
          max-height: 120px;
        }
        .send-btn {
          height: 42px;
          padding: 0 20px;
        }
        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}
