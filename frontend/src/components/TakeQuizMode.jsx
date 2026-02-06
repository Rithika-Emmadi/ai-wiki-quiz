import { useState } from 'react'
import './TakeQuizMode.css'

function DifficultyBadge({ difficulty }) {
  return <span className={`badge badge-${difficulty}`}>{difficulty}</span>
}

export default function TakeQuizMode({ data }) {
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)

  const quiz = data?.quiz || []
  const total = quiz.length

  const handleSelect = (qIndex, option) => {
    if (submitted) return
    setAnswers((prev) => ({ ...prev, [qIndex]: option }))
  }

  const handleSubmit = () => {
    setSubmitted(true)
  }

  const correct = quiz.filter((q, i) => answers[i] === q.answer).length
  const score = total ? Math.round((correct / total) * 100) : 0

  return (
    <div className="take-quiz">
      <div className="take-quiz-header">
        <h3>{data?.title} – Quiz</h3>
        {submitted && (
          <div className="score-display">
            Score: {correct}/{total} ({score}%)
          </div>
        )}
      </div>

      <div className="take-quiz-questions">
        {quiz.map((q, i) => (
          <div key={q.id ?? i} className="take-quiz-card">
            <div className="take-quiz-card-header">
              <span className="question-num">Q{i + 1}</span>
              <DifficultyBadge difficulty={q.difficulty} />
            </div>
            <p className="question-text">{q.question}</p>
            <ul className="take-options">
              {q.options?.map((opt, j) => {
                const isSelected = answers[i] === opt
                const isCorrect = opt === q.answer
                const showResult = submitted
                let optionClass = 'take-option'
                if (showResult) {
                  if (isCorrect) optionClass += ' correct'
                  else if (isSelected && !isCorrect) optionClass += ' wrong'
                } else if (isSelected) {
                  optionClass += ' selected'
                }
                return (
                  <li
                    key={j}
                    className={optionClass}
                    onClick={() => handleSelect(i, opt)}
                  >
                    {String.fromCharCode(65 + j)}. {opt}
                    {showResult && isCorrect && <span className="check"> ✓</span>}
                    {showResult && isSelected && !isCorrect && <span className="cross"> ✗</span>}
                  </li>
                )
              })}
            </ul>
            {submitted && q.explanation && (
              <div className="explanation">{q.explanation}</div>
            )}
          </div>
        ))}
      </div>

      <div className="take-quiz-actions">
        <button
          className="btn-primary"
          onClick={handleSubmit}
          disabled={submitted || Object.keys(answers).length === 0}
        >
          {submitted ? 'Quiz Complete' : 'Submit Answers'}
        </button>
      </div>
    </div>
  )
}
