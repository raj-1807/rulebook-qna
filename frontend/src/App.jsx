import { useState } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

const STATE_CONFIG = {
  ANSWERABLE: {
    label: 'ANSWERABLE',
    icon: '✓',
    className: 'state-answerable',
    description: 'The regulations contain sufficient evidence to answer this question.',
  },
  NOT_FOUND: {
    label: 'NOT FOUND',
    icon: '∅',
    className: 'state-not-found',
    description: 'The regulations do not contain specific information to answer this question.',
  },
  CONTRADICTORY: {
    label: 'CONTRADICTORY',
    icon: '⚡',
    className: 'state-contradictory',
    description: 'Multiple rules in the regulations conflict on this question.',
  },
}

const DEMO_QUESTIONS = [
  'What is the minimum attendance requirement for regular students?',
  'Can a student miss an exam because of a family wedding?',
  'Can the Academic Committee waive the 60% minimum attendance requirement for a student with a severe medical condition?',
]

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const askQuestion = async (q) => {
    const queryText = q || question
    if (!queryText.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err.message || 'Failed to connect to the server')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    askQuestion()
  }

  const handleDemoClick = (q) => {
    setQuestion(q)
    askQuestion(q)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">📚</span>
            <h1>Rulebook QnA</h1>
          </div>
          <p className="tagline">Evidence-grounded university regulations Q&A with three-state reasoning</p>
        </div>
      </header>

      <main className="main">
        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-wrapper">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about university regulations..."
                className="query-input"
                disabled={loading}
              />
              <button type="submit" className="ask-button" disabled={loading || !question.trim()}>
                {loading ? (
                  <span className="spinner"></span>
                ) : (
                  'Ask'
                )}
              </button>
            </div>
          </form>

          <div className="demo-section">
            <span className="demo-label">Try:</span>
            {DEMO_QUESTIONS.map((q, i) => (
              <button
                key={i}
                className="demo-button"
                onClick={() => handleDemoClick(q)}
                disabled={loading}
              >
                {q.length > 60 ? q.substring(0, 57) + '...' : q}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="error-card">
            <span className="error-icon">⚠</span>
            <div>
              <strong>Error</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-card">
            <div className="loading-animation">
              <div className="pulse-ring"></div>
              <span className="loading-icon">🔍</span>
            </div>
            <p>Searching regulations and analyzing evidence...</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <StateIndicator state={response.state} confidence={response.confidence} />

            <div className="answer-card">
              <h3>Answer</h3>
              <div className="answer-text">{response.answer}</div>
            </div>

            {response.state === 'CONTRADICTORY' && response.conflicts.length > 0 && (
              <ConflictPanel conflicts={response.conflicts} />
            )}

            {response.evidence.length > 0 && (
              <EvidencePanel evidence={response.evidence} />
            )}
          </div>
        )}

        <div className="states-info">
          <h3>Three-State Reasoning</h3>
          <div className="states-grid">
            {Object.entries(STATE_CONFIG).map(([key, config]) => (
              <div key={key} className={`state-info-card ${config.className}`}>
                <span className="state-info-icon">{config.icon}</span>
                <strong>{config.label}</strong>
                <p>{config.description}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Rulebook QnA — "The Rulebook That Argues With Itself"</p>
        <p className="footer-sub">Every answer is grounded in evidence. When evidence is insufficient, we say so. When rules conflict, we show both sides.</p>
      </footer>
    </div>
  )
}

function StateIndicator({ state, confidence }) {
  const config = STATE_CONFIG[state] || STATE_CONFIG.NOT_FOUND

  return (
    <div className={`state-indicator ${config.className}`}>
      <div className="state-badge">
        <span className="state-icon">{config.icon}</span>
        <span className="state-label">{config.label}</span>
      </div>
      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: `${(confidence * 100)}%` }}></div>
      </div>
      <span className="confidence-value">{(confidence * 100).toFixed(0)}% confidence</span>
    </div>
  )
}

function ConflictPanel({ conflicts }) {
  return (
    <div className="conflict-panel">
      <h3>⚡ Conflicting Rules Detected</h3>
      {conflicts.map((conflict, i) => (
        <div key={i} className="conflict-item">
          <div className="conflict-rules">
            <div className="conflict-rule rule-a">
              <div className="rule-header">
                <span className="rule-label">Rule A</span>
                <span className="rule-source">{conflict.rule_a.document}</span>
              </div>
              {conflict.rule_a.page && <div className="rule-meta">Page {conflict.rule_a.page}</div>}
              <div className="rule-meta">{conflict.rule_a.section}</div>
              <blockquote className="rule-text">"{conflict.rule_a.text}"</blockquote>
            </div>

            <div className="conflict-vs">VS</div>

            <div className="conflict-rule rule-b">
              <div className="rule-header">
                <span className="rule-label">Rule B</span>
                <span className="rule-source">{conflict.rule_b.document}</span>
              </div>
              {conflict.rule_b.page && <div className="rule-meta">Page {conflict.rule_b.page}</div>}
              <div className="rule-meta">{conflict.rule_b.section}</div>
              <blockquote className="rule-text">"{conflict.rule_b.text}"</blockquote>
            </div>
          </div>

          <div className="conflict-explanation">
            <strong>Why this conflicts:</strong> {conflict.explanation}
          </div>
        </div>
      ))}
    </div>
  )
}

function EvidencePanel({ evidence }) {
  return (
    <div className="evidence-panel">
      <h3>📄 Supporting Evidence</h3>
      <div className="evidence-list">
        {evidence.map((ev, i) => (
          <div key={i} className="evidence-item">
            <div className="evidence-header">
              <span className="evidence-id">{ev.evidence_id}</span>
              <span className="evidence-score">Score: {(ev.score * 100).toFixed(0)}%</span>
            </div>
            <div className="evidence-source">
              <span className="source-doc">📁 {ev.document}</span>
              {ev.page && <span className="source-page">📃 Page {ev.page}</span>}
              <span className="source-section">§ {ev.section}</span>
            </div>
            <blockquote className="evidence-text">"{ev.text}"</blockquote>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
