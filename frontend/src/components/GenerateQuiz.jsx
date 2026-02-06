import { useState } from 'react'
import QuizDisplay from './QuizDisplay'
import TakeQuizMode from './TakeQuizMode'
import './GenerateQuiz.css'

const API_BASE = 'http://127.0.0.1:8000/api'

export default function GenerateQuiz() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewTitle, setPreviewTitle] = useState(null)
  const [error, setError] = useState(null)
  const [quizData, setQuizData] = useState(null)
  const [viewMode, setViewMode] = useState('study') // 'study' | 'take'

  const handlePreview = async () => {
    if (!url.trim()) return
    setError(null)
    setPreviewTitle(null)
    setPreviewLoading(true)
    try {
      const res = await fetch(`${API_BASE}/preview?url=${encodeURIComponent(url.trim())}`)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Invalid URL')
      setPreviewTitle(data.title)
    } catch (err) {
      setError(err.message)
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setQuizData(null)
    setPreviewTitle(null)
    if (!url.trim()) {
      setError('Please enter a Wikipedia URL')
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        const msg = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || d.message).join(', ')
          : data.detail || 'Failed to generate quiz'
        throw new Error(msg)
      }
      setQuizData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="generate-quiz">
      <form onSubmit={handleSubmit} className="generate-form">
        <label htmlFor="url">Wikipedia Article URL</label>
        <div className="input-row">
          <input
            id="url"
            type="url"
            placeholder="https://en.wikipedia.org/wiki/Alan_Turing"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setPreviewTitle(null) }}
            disabled={loading}
          />
          <div className="button-group">
            <button
              type="button"
              onClick={handlePreview}
              disabled={loading || previewLoading || !url.trim()}
              className="btn-secondary"
            >
              {previewLoading ? 'Checking…' : 'Validate & Preview'}
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Generating…' : 'Generate Quiz'}
            </button>
          </div>
        </div>
        {previewTitle && <p className="preview-msg">✓ Article: <strong>{previewTitle}</strong></p>}
        {error && <p className="error">{error}</p>}
      </form>

      {quizData && (
        <div className="quiz-result">
          <div className="result-actions">
            <button
              className={`mode-btn ${viewMode === 'study' ? 'active' : ''}`}
              onClick={() => setViewMode('study')}
            >
              Study Mode
            </button>
            <button
              className={`mode-btn ${viewMode === 'take' ? 'active' : ''}`}
              onClick={() => setViewMode('take')}
            >
              Take Quiz
            </button>
          </div>
          {viewMode === 'study' ? (
            <QuizDisplay data={quizData} />
          ) : (
            <TakeQuizMode data={quizData} />
          )}
        </div>
      )}
    </div>
  )
}
