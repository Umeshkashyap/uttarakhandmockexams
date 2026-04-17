import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();

  const examData = [
    {
      id: 'uttarakhand',
      name: 'Uttarakhand Exams',
      description: 'State level competitive examinations for Uttarakhand',
      icon: '🏔️',
      color: 'blue',
      stats: {
        totalTests: 38,
        bestScore: 85,
        questions: 1900,
        completed: 8
      }
    },
    {
      id: 'uttar-pradesh',
      name: 'Uttar Pradesh Exams',
      description: 'UP state competitive examinations and recruitment tests',
      icon: '🏛️',
      color: 'green',
      stats: {
        totalTests: 52,
        bestScore: 82,
        questions: 2600,
        completed: 12
      }
    },
    {
      id: 'ssc',
      name: 'SSC Exams',
      description: 'Staff Selection Commission examinations and tests',
      icon: '📋',
      color: 'orange',
      stats: {
        totalTests: 67,
        bestScore: 79,
        questions: 3350,
        completed: 4
      }
    }
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Mock Test Dashboard</h1>
        <p>Select your exam category to begin your preparation journey</p>
      </header>

      <div className="container">
        <div className="cards-grid">
          {examData.map((exam) => (
            <div 
              key={exam.id}
              className={`exam-card ${exam.color}`}
              onClick={() => navigate(`/exam/${exam.id}`)}
            >
              <div className="card-header">
                <div className={`card-icon ${exam.color}`}>
                  {exam.icon}
                </div>
                <h2>{exam.name}</h2>
                <p>{exam.description}</p>
              </div>

              <div className="card-body">
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{exam.stats.totalTests}</div>
                    <div className="stat-label">Total tests</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{exam.stats.bestScore}%</div>
                    <div className="stat-label">Best score</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{exam.stats.questions.toLocaleString()}</div>
                    <div className="stat-label">Questions</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{exam.stats.completed}</div>
                    <div className="stat-label">Completed</div>
                  </div>
                </div>
              </div>

              <div className="card-footer">
                <button className={`open-btn ${exam.color}`}>
                  Open
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
