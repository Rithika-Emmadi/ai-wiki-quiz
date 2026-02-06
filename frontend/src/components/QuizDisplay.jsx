import './QuizDisplay.css'

function DifficultyBadge({ difficulty }) {
  const cls = `badge badge-${difficulty}`
  return <span className={cls}>{difficulty}</span>
}

export default function QuizDisplay({ data }) {
  if (!data) return null

  const { title, url, summary, sections, quiz, related_topics, key_entities } = data

  return (
    <div className="quiz-display">
      <article className="article-card">
        <h2 className="article-title">{title}</h2>
        <a href={url} target="_blank" rel="noopener noreferrer" className="article-link">
          View on Wikipedia ↗
        </a>
        {summary && <p className="article-summary">{summary}</p>}
        {sections?.length > 0 && (
          <div className="sections">
            <strong>Sections:</strong>{' '}
            {sections.slice(0, 10).join(' • ')}
            {sections.length > 10 && ' …'}
          </div>
        )}
        {key_entities && (
          <div className="key-entities">
            {key_entities.people?.length > 0 && (
              <span><strong>People:</strong> {key_entities.people.join(', ')}</span>
            )}
            {key_entities.organizations?.length > 0 && (
              <span><strong>Organizations:</strong> {key_entities.organizations.join(', ')}</span>
            )}
            {key_entities.locations?.length > 0 && (
              <span><strong>Locations:</strong> {key_entities.locations.join(', ')}</span>
            )}
          </div>
        )}
      </article>

      <section className="quiz-section">
        <h3 className="section-title">Quiz Questions</h3>
        <div className="quiz-cards">
          {quiz?.map((q, i) => (
            <div key={q.id ?? i} className="quiz-card">
              <div className="quiz-card-header">
                <span className="question-num">Q{i + 1}</span>
                <DifficultyBadge difficulty={q.difficulty} />
                {q.section && <span className="quiz-section-tag">{q.section}</span>}
              </div>
              <p className="question-text">{q.question}</p>
              <ul className="options">
                {q.options?.map((opt, j) => (
                  <li
                    key={j}
                    className={`option ${opt === q.answer ? 'correct' : ''}`}
                  >
                    {String.fromCharCode(65 + j)}. {opt}
                    {opt === q.answer && <span className="check"> ✓</span>}
                  </li>
                ))}
              </ul>
              {q.explanation && (
                <div className="explanation">
                  <strong>Explanation:</strong> {q.explanation}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {related_topics?.length > 0 && (
        <section className="related-section">
          <h3 className="section-title">Related Topics</h3>
          <div className="related-tags">
            {related_topics.map((topic) => (
              <a
                key={topic}
                href={`https://en.wikipedia.org/wiki/${encodeURIComponent(topic.replace(/ /g, '_'))}`}
                target="_blank"
                rel="noopener noreferrer"
                className="related-tag"
              >
                {topic}
              </a>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
