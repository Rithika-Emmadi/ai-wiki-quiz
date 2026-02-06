import { useState } from 'react'
import GenerateQuiz from './components/GenerateQuiz'
import PastQuizzes from './components/PastQuizzes'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('generate')

  return (
    <div className="app">
      <header className="header">
        <h1 className="logo">
          <span className="logo-icon">◇</span>
          AI Wiki Quiz Generator
        </h1>
        <nav className="tabs">
          <button
            className={`tab ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
          >
            Generate Quiz
          </button>
          <button
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Past Quizzes
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'generate' && <GenerateQuiz />}
        {activeTab === 'history' && <PastQuizzes />}
      </main>

      <footer className="footer">
        <p>Generate quizzes from any Wikipedia article using AI</p>
      </footer>
    </div>
  )
}

export default App
