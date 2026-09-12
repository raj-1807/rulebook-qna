import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

const STATE_CONFIG = {
  ANSWERABLE: {
    label: 'ANSWERABLE',
    icon: '\u2713',
    className: 'state-answerable',
    description: 'The regulations contain sufficient evidence to answer this question.',
  },
  NOT_FOUND: {
    label: 'NOT FOUND',
    icon: '\u2205',
    className: 'state-not-found',
    description: 'The regulations do not contain enough information to answer this question.',
  },
  CONTRADICTORY: {
    label: 'CONTRADICTORY',
    icon: '\u26A1',
    className: 'state-contradictory',
    description: 'Multiple rules in the regulations conflict on this question.',
  },
}

const DEMO_QUESTIONS = [
  { text: 'What is the minimum attendance requirement for regular students?', tag: 'Answerable' },
  { text: 'Can a student miss an exam because of a family wedding?', tag: 'Not Found' },
  { text: 'Can the Academic Committee waive the 60% minimum attendance requirement for a student with a severe medical condition?', tag: 'Contradictory' },
]

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark')
  const [history, setHistory] = useState([])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

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
      setHistory(prev => [{ question: queryText, state: data.state, timestamp: new Date() }, ...prev.slice(0, 9)])
    } catch (err) {
      setError(err.message || 'Failed to connect to the server. Is the backend running?')
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
      {/* Floating Theme Toggle */}
      <button className="theme-toggle" onClick={toggleTheme} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
        {theme === 'dark' ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        )}
      </button>

      {/* Hero Header */}
      <header className="header">
        <div className="header-bg"></div>
        <div className="header-content">
          <div className="header-badge">Evidence-Grounded AI</div>
          <h1 className="header-title">
            Rulebook <span className="highlight">QnA</span>
          </h1>
          <p className="header-subtitle">
            The Rulebook That Argues With Itself
          </p>
          <div className="header-pills">
            <span className="pill pill-green">Answerable</span>
            <span className="pill pill-amber">Not Found</span>
            <span className="pill pill-red">Contradictory</span>
          </div>
        </div>
      </header>

      <main className="main">
        {/* Search Section */}
        <section className="search-section">
          <form onSubmit={handleSubmit} className="search-form">
            <div className="search-icon-wrapper">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            </div>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about university regulations..."
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading || !question.trim()}>
              {loading ? <span className="btn-spinner"></span> : 'Search'}
            </button>
          </form>

          <div className="demo-chips">
            <span className="demo-label">Quick questions:</span>
            {DEMO_QUESTIONS.map((q, i) => (
              <button key={i} className={`demo-chip demo-chip-${q.tag.toLowerCase().replace(' ', '-')}`} onClick={() => handleDemoClick(q.text)} disabled={loading}>
                <span className="chip-tag">{q.tag}</span>
                <span className="chip-text">{q.text.length > 50 ? q.text.substring(0, 47) + '...' : q.text}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className="alert alert-error animate-in">
            <div className="alert-icon">!</div>
            <div className="alert-body">
              <strong>Connection Error</strong>
              <p>{error}</p>
            </div>
            <button className="alert-dismiss" onClick={() => setError(null)}>&times;</button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="loading-state animate-in">
            <div className="loading-orb">
              <div className="orb-ring orb-ring-1"></div>
              <div className="orb-ring orb-ring-2"></div>
              <div className="orb-ring orb-ring-3"></div>
              <div className="orb-core">?</div>
            </div>
            <div className="loading-steps">
              <div className="step active">Retrieving evidence...</div>
              <div className="step">Analyzing regulations...</div>
              <div className="step">Generating grounded answer...</div>
            </div>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="response animate-in">
            {/* State Banner */}
            <div className={`state-banner ${STATE_CONFIG[response.state]?.className}`}>
              <div className="banner-left">
                <div className="banner-icon">{STATE_CONFIG[response.state]?.icon}</div>
                <div>
                  <div className="banner-label">{STATE_CONFIG[response.state]?.label}</div>
                  <div className="banner-desc">{STATE_CONFIG[response.state]?.description}</div>
                </div>
              </div>
              <div className="banner-confidence">
                <svg width="36" height="36" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeWidth="3" opacity="0.15"/>
                  <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeWidth="3"
                    strokeDasharray={`${response.confidence * 94.25} 94.25`}
                    strokeLinecap="round" transform="rotate(-90 18 18)"
                    style={{transition: 'stroke-dasharray 0.8s ease'}}/>
                </svg>
                <span className="confidence-text">{(response.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            {/* Answer */}
            <div className="card answer-card">
              <div className="card-header">
                <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> Answer</h3>
              </div>
              <div className="card-body">
                <div className="answer-text">{response.answer}</div>
              </div>
            </div>

            {/* Conflicts */}
            {response.state === 'CONTRADICTORY' && response.conflicts.length > 0 && (
              <div className="card conflict-card">
                <div className="card-header conflict-header">
                  <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> Conflicting Rules Detected</h3>
                </div>
                <div className="card-body">
                  {response.conflicts.map((conflict, i) => (
                    <div key={i} className="conflict-block">
                      <div className="conflict-versus">
                        <div className="versus-rule versus-a">
                          <div className="versus-badge">Rule A</div>
                          <div className="versus-source">
                            <strong>{conflict.rule_a.document}</strong>
                            {conflict.rule_a.page && <span> &middot; Page {conflict.rule_a.page}</span>}
                            <span> &middot; {conflict.rule_a.section}</span>
                          </div>
                          <blockquote>{conflict.rule_a.text}</blockquote>
                        </div>

                        <div className="versus-divider">
                          <span>VS</span>
                        </div>

                        <div className="versus-rule versus-b">
                          <div className="versus-badge">Rule B</div>
                          <div className="versus-source">
                            <strong>{conflict.rule_b.document}</strong>
                            {conflict.rule_b.page && <span> &middot; Page {conflict.rule_b.page}</span>}
                            <span> &middot; {conflict.rule_b.section}</span>
                          </div>
                          <blockquote>{conflict.rule_b.text}</blockquote>
                        </div>
                      </div>

                      <div className="conflict-reason">
                        <strong>Why this conflicts:</strong> {conflict.explanation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence */}
            {response.evidence.length > 0 && (
              <div className="card evidence-card">
                <div className="card-header">
                  <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> Evidence ({response.evidence.length})</h3>
                </div>
                <div className="card-body">
                  {response.evidence.map((ev, i) => (
                    <div key={i} className="evidence-item">
                      <div className="ev-top">
                        <span className="ev-id">{ev.evidence_id}</span>
                        <div className="ev-score-bar">
                          <div className="ev-score-fill" style={{ width: `${ev.score * 100}%` }}></div>
                        </div>
                        <span className="ev-score-val">{(ev.score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="ev-source">
                        <span className="ev-tag ev-tag-doc">{ev.document}</span>
                        {ev.page && <span className="ev-tag ev-tag-page">Page {ev.page}</span>}
                        <span className="ev-tag ev-tag-section">{ev.section}</span>
                      </div>
                      <blockquote className="ev-text">{ev.text}</blockquote>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* How it Works - show only when no response */}
        {!response && !loading && !error && (
          <section className="how-it-works animate-in">
            <h2>How It Works</h2>
            <div className="steps-grid">
              <div className="step-card">
                <div className="step-num">1</div>
                <h4>Ask a Question</h4>
                <p>Type any question about university regulations, policies, fees, or procedures.</p>
              </div>
              <div className="step-card">
                <div className="step-num">2</div>
                <h4>Hybrid Retrieval</h4>
                <p>BM25 keyword search + semantic embeddings find the most relevant regulatory passages.</p>
              </div>
              <div className="step-card">
                <div className="step-num">3</div>
                <h4>State Classification</h4>
                <p>The system determines if the question is answerable, not found, or contradictory.</p>
              </div>
              <div className="step-card">
                <div className="step-num">4</div>
                <h4>Grounded Answer</h4>
                <p>Every answer is traced to exact source passages. No hallucination, no guessing.</p>
              </div>
            </div>

            <div className="three-states">
              <div className="ts-card ts-answerable">
                <div className="ts-icon">{'\u2713'}</div>
                <strong>ANSWERABLE</strong>
                <p>Evidence found. Answer with citations.</p>
              </div>
              <div className="ts-card ts-not-found">
                <div className="ts-icon">{'\u2205'}</div>
                <strong>NOT FOUND</strong>
                <p>No evidence. Refuses to guess.</p>
              </div>
              <div className="ts-card ts-contradictory">
                <div className="ts-icon">{'\u26A1'}</div>
                <strong>CONTRADICTORY</strong>
                <p>Conflicting rules. Shows both sides.</p>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <p><strong>Rulebook QnA</strong> &mdash; Evidence-grounded university regulations Q&A</p>
          <p className="footer-sub">Every answer is traceable. When evidence is insufficient, we say so. When rules conflict, we show both sides.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
