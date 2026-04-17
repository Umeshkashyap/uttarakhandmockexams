import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);

  const examData = [
    {
      id: 'uttarakhand',
      name: 'Uttarakhand Exams',
      description: 'State level competitive examinations for Uttarakhand',
      icon: '🏔️',
      color: 'blue',
      stats: {
        totalTests: 128,
        bestScore: 85,
        questions: 6400,
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

  const handleAdminLogin = () => {
    setIsAdmin(true);
    setShowAdminDashboard(true);
  };

  const handleAdminLogout = () => {
    setIsAdmin(false);
    setShowAdminDashboard(false);
  };

  const handleBackToDashboard = () => {
    setShowAdminDashboard(false);
  };

  // Show admin dashboard when admin is logged in and dashboard is requested
  if (showAdminDashboard) {
    return <AdminDashboard onBackToDashboard={handleBackToDashboard} />;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content-wrapper">
          <div className="header-text">
            <h1>Mock Test Dashboard</h1>
            <p>Select your exam category to begin your preparation journey</p>
          </div>
          
          <div className="admin-section">
            {isAdmin ? (
              <div className="admin-info">
                <span className="admin-badge">Admin</span>
                <button className="admin-btn logout" onClick={handleAdminLogout}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  Logout
                </button>
              </div>
            ) : (
              <button className="admin-btn login" onClick={() => setShowAdminLogin(true)}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                  <polyline points="10 17 15 12 10 7"/>
                  <line x1="15" y1="12" x2="3" y2="12"/>
                </svg>
                Admin Login
              </button>
            )}
          </div>
        </div>
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

      {showAdminLogin && (
        <AdminLogin 
          onLogin={handleAdminLogin}
          onClose={() => setShowAdminLogin(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
