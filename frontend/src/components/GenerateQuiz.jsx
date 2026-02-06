import { useState } from 'react'
import QuizDisplay from './QuizDisplay'
import TakeQuizMode from './TakeQuizMode'
import './GenerateQuiz.css'

import { apiGet, apiPost } from '../lib/api'

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
      const data = await apiGet(`/preview?url=${encodeURIComponent(url.trim())}`)
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
      const data = await apiPost('/generate', { url: url.trim() })
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
