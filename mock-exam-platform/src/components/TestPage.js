import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './TestPage.css';

const TestPage = () => {
  const navigate = useNavigate();
  const { examId, subjectId } = useParams();
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answers, setAnswers] = useState({});
  const [markedQuestions, setMarkedQuestions] = useState(new Set());
  const [timeRemaining, setTimeRemaining] = useState(3600);

  const questions = [
    {
      id: 1,
      text: 'Which article of the Indian Constitution deals with the abolition of untouchability?',
      options: ['Article 14', 'Article 15', 'Article 17', 'Article 19'],
      marks: 2
    },
    {
      id: 2,
      text: 'The Tropic of Cancer does not pass through which of the following Indian states?',
      options: ['Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Uttarakhand'],
      marks: 2
    },
    {
      id: 3,
      text: 'Who was the first President of India?',
      options: ['Jawaharlal Nehru', 'Dr. Rajendra Prasad', 'Sardar Vallabhbhai Patel', 'Dr. B.R. Ambedkar'],
      marks: 2
    },
    {
      id: 4,
      text: 'Which is the longest river in India?',
      options: ['Ganga', 'Godavari', 'Yamuna', 'Brahmaputra'],
      marks: 2
    },
    {
      id: 5,
      text: 'In which year did India gain independence?',
      options: ['1945', '1946', '1947', '1948'],
      marks: 2
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 0) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSelectOption = (index) => {
    setSelectedAnswer(index);
  };

  const handleSaveAndNext = () => {
    if (selectedAnswer !== null) {
      setAnswers({ ...answers, [currentQuestion]: selectedAnswer });
    }
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(answers[currentQuestion + 1] ?? null);
    }
  };

  const handleMarkForReview = () => {
    const newMarked = new Set(markedQuestions);
    newMarked.add(currentQuestion);
    setMarkedQuestions(newMarked);
    
    if (selectedAnswer !== null) {
      setAnswers({ ...answers, [currentQuestion]: selectedAnswer });
    }
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(answers[currentQuestion + 1] ?? null);
    }
  };

  const handleClearResponse = () => {
    setSelectedAnswer(null);
    const newAnswers = { ...answers };
    delete newAnswers[currentQuestion];
    setAnswers(newAnswers);
  };

  const handleQuestionClick = (index) => {
    setCurrentQuestion(index);
    setSelectedAnswer(answers[index] ?? null);
  };

  const handleSubmitTest = () => {
    const confirmed = window.confirm('Are you sure you want to submit the test?');
    if (confirmed) {
      alert('Test submitted successfully!');
      navigate('/');
    }
  };

  const answeredCount = Object.keys(answers).length;
  const notAnsweredCount = questions.length - answeredCount;
  const markedCount = markedQuestions.size;

  return (
    <div className="test-container">
      <header className="test-header">
        <div className="test-info">
          <h1>General Studies Test</h1>
          <p>{examId.charAt(0).toUpperCase() + examId.slice(1)} Exams • India & World</p>
        </div>

        <div className="timer-section">
          <div className="timer">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span className="timer-text">{formatTime(timeRemaining)}</span>
          </div>

          <div className="question-counter">
            Question <span>{currentQuestion + 1}</span> of <span>{questions.length}</span>
          </div>
        </div>
      </header>

      <div className="test-body">
        <div className="question-area">
          <div className="question-header">
            <div className="question-number">Question {currentQuestion + 1}</div>
            <div className="question-marks">Marks: <span>{questions[currentQuestion].marks}</span></div>
          </div>

          <div className="question-text">
            {questions[currentQuestion].text}
          </div>

          <div className="options-list">
            {questions[currentQuestion].options.map((option, index) => (
              <div
                key={index}
                className={`option ${selectedAnswer === index ? 'selected' : ''}`}
                onClick={() => handleSelectOption(index)}
              >
                <div className="option-radio"></div>
                <span className="option-label">{String.fromCharCode(65 + index)}.</span>
                <span className="option-text">{option}</span>
              </div>
            ))}
          </div>

          <div className="question-actions">
            <button className="action-btn warning" onClick={handleMarkForReview}>
              Mark for review
            </button>
            <button className="action-btn" onClick={handleClearResponse}>
              Clear
            </button>
            <button className="action-btn primary" onClick={handleSaveAndNext}>
              Save & Next
            </button>
          </div>
        </div>

        <aside className="sidebar">
          <div className="sidebar-card">
            <div className="sidebar-title">Question palette</div>

            <div className="question-grid">
              {questions.map((_, index) => (
                <button
                  key={index}
                  className={`question-btn ${
                    index === currentQuestion
                      ? 'current'
                      : answers[index] !== undefined
                      ? 'answered'
                      : markedQuestions.has(index)
                      ? 'marked'
                      : ''
                  }`}
                  onClick={() => handleQuestionClick(index)}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            <div className="legend">
              <div className="legend-item">
                <div className="legend-box answered"></div>
                <span>Answered</span>
              </div>
              <div className="legend-item">
                <div className="legend-box marked"></div>
                <span>Marked for review</span>
              </div>
              <div className="legend-item">
                <div className="legend-box current"></div>
                <span>Current question</span>
              </div>
              <div className="legend-item">
                <div className="legend-box"></div>
                <span>Not visited</span>
              </div>
            </div>
          </div>

          <div className="sidebar-card">
            <div className="sidebar-title">Test summary</div>

            <div className="summary-stats">
              <div className="summary-item">
                <span>Answered</span>
                <span className="count answered">{answeredCount}</span>
              </div>
              <div className="summary-item">
                <span>Not answered</span>
                <span className="count">{notAnsweredCount}</span>
              </div>
              <div className="summary-item">
                <span>Marked</span>
                <span className="count marked">{markedCount}</span>
              </div>
            </div>

            <div className="submit-section">
              <button className="submit-btn" onClick={handleSubmitTest}>
                Submit test
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default TestPage;
