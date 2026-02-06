import { useState, useEffect } from 'react'
import QuizDisplay from './QuizDisplay'
import TakeQuizMode from './TakeQuizMode'
import './PastQuizzes.css'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default function PastQuizzes() {
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedQuiz, setSelectedQuiz] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailViewMode, setDetailViewMode] = useState('study') // 'study' | 'take'

  const fetchQuizzes = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/quizzes`)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Failed to load quizzes')
      setQuizzes(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuizzes()
  }, [])

  const openDetails = async (id) => {
    setDetailLoading(true)
    setSelectedQuiz(null)
    setDetailViewMode('study')
    try {
      const res = await fetch(`${API_BASE}/quizzes/${id}`)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Failed to load quiz')
      setSelectedQuiz(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeModal = () => {
    setSelectedQuiz(null)
  }

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="past-quizzes">
      <h2 className="page-title">Past Quizzes</h2>

      {loading ? (
        <p className="loading">Loading quizzes…</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : quizzes.length === 0 ? (
        <p className="empty">No quizzes yet. Generate one from the Generate Quiz tab!</p>
      ) : (
        <div className="table-wrapper">
          <table className="quizzes-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>URL</th>
                <th>Questions</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {quizzes.map((q) => (
                <tr key={q.id}>
                  <td className="title-cell">{q.title}</td>
                  <td className="url-cell">
                    <a
                      href={q.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      title={q.url}
                    >
                      {q.url.length > 50 ? q.url.slice(0, 50) + '…' : q.url}
                    </a>
                  </td>
                  <td>{q.question_count}</td>
                  <td>{formatDate(q.created_at)}</td>
                  <td>
                    <button
                      className="btn-details"
                      onClick={() => openDetails(q.id)}
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(detailLoading || selectedQuiz) && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Quiz Details</h3>
              <button className="modal-close" onClick={closeModal} aria-label="Close">
                ×
              </button>
            </div>
            <div className="modal-body">
              {detailLoading ? (
                <p className="loading">Loading…</p>
              ) : selectedQuiz ? (
                <>
                  <div className="result-actions">
                    <button
                      className={`mode-btn ${detailViewMode === 'study' ? 'active' : ''}`}
                      onClick={() => setDetailViewMode('study')}
                    >
                      Study Mode
                    </button>
                    <button
                      className={`mode-btn ${detailViewMode === 'take' ? 'active' : ''}`}
                      onClick={() => setDetailViewMode('take')}
                    >
                      Take Quiz
                    </button>
                  </div>
                  {detailViewMode === 'study' ? (
                    <QuizDisplay data={selectedQuiz} />
                  ) : (
                    <TakeQuizMode data={selectedQuiz} />
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
