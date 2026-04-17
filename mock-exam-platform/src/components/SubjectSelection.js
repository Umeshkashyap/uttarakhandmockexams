import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './SubjectSelection.css';

const SubjectSelection = () => {
  const navigate = useNavigate();
  const { examId } = useParams();

  const examInfo = {
    'uttarakhand': {
      name: 'Uttarakhand Exams',
      description: 'Comprehensive test series covering all major topics for Uttarakhand state examinations',
      icon: '🏔️',
      color: 'blue'
    },
    'uttar-pradesh': {
      name: 'Uttar Pradesh Exams',
      description: 'Comprehensive test series covering all major topics for UP state examinations',
      icon: '🏛️',
      color: 'green'
    },
    'ssc': {
      name: 'SSC Exams',
      description: 'Comprehensive test series for Staff Selection Commission examinations',
      icon: '📋',
      color: 'orange'
    }
  };

  const subjectsData = {
    'uttarakhand': [
      {
        id: 'uttarakhand-special',
        name: 'Uttarakhand Special',
        description: 'Complete coverage of Uttarakhand specific topics including history, geography, culture, economy and current affairs',
        icon: '🏔️',
        color: 'blue',
        topics: ['History', 'Geography', 'Culture', 'Economy', 'Current Affairs'],
        stats: {
          totalTests: 18,
          questions: 900,
          duration: 60
        }
      },
      {
        id: 'general-studies',
        name: 'General Studies',
        description: 'Comprehensive general knowledge covering India and world affairs, polity, science, and general awareness',
        icon: '🌍',
        color: 'green',
        topics: ['Indian Polity', 'World Geography', 'Science', 'General Awareness'],
        stats: {
          totalTests: 12,
          questions: 600,
          duration: 60
        }
      },
      {
        id: 'aptitude-reasoning',
        name: 'Aptitude & Reasoning',
        description: 'Sharpen your analytical and logical reasoning skills with comprehensive aptitude tests',
        icon: '🧠',
        color: 'orange',
        topics: ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'Data Analysis'],
        stats: {
          totalTests: 8,
          questions: 400,
          duration: 45
        }
      }
    ],
    'uttar-pradesh': [
      {
        id: 'up-special',
        name: 'UP Special',
        description: 'Complete coverage of Uttar Pradesh specific topics',
        icon: '🏛️',
        color: 'green',
        topics: ['UP History', 'UP Geography', 'Culture', 'Economy'],
        stats: {
          totalTests: 20,
          questions: 1000,
          duration: 60
        }
      },
      {
        id: 'general-studies',
        name: 'General Studies',
        description: 'Comprehensive general knowledge for UP exams',
        icon: '🌍',
        color: 'blue',
        topics: ['Indian Polity', 'Geography', 'Science', 'Current Affairs'],
        stats: {
          totalTests: 15,
          questions: 750,
          duration: 60
        }
      }
    ],
    'ssc': [
      {
        id: 'ssc-general',
        name: 'General Intelligence',
        description: 'Reasoning and analytical ability for SSC exams',
        icon: '🧠',
        color: 'orange',
        topics: ['Logical Reasoning', 'Analytical Ability', 'Problem Solving'],
        stats: {
          totalTests: 25,
          questions: 1250,
          duration: 60
        }
      },
      {
        id: 'quantitative',
        name: 'Quantitative Aptitude',
        description: 'Mathematics and numerical ability',
        icon: '📊',
        color: 'blue',
        topics: ['Arithmetic', 'Algebra', 'Geometry', 'Data Interpretation'],
        stats: {
          totalTests: 22,
          questions: 1100,
          duration: 60
        }
      }
    ]
  };

  const currentExam = examInfo[examId];
  const subjects = subjectsData[examId] || [];

  return (
    <div className="subject-selection-container">
      <header className="subject-header">
        <div className="header-content">
          <button className="back-btn" onClick={() => navigate('/')}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </button>
          <div className="header-title">
            <h1>{currentExam.name}</h1>
            <p>Select your subject to begin practice</p>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="breadcrumb">
          <span className="breadcrumb-item" onClick={() => navigate('/')}>Dashboard</span>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-item active">{currentExam.name}</span>
        </div>

        <div className={`exam-info-banner ${currentExam.color}`}>
          <div className="banner-icon">{currentExam.icon}</div>
          <div className="banner-content">
            <h2>{currentExam.name}</h2>
            <p>{currentExam.description}</p>
          </div>
        </div>

        <h3 className="section-title">Choose your subject category</h3>

        <div className="subjects-grid">
          {subjects.map((subject) => (
            <div key={subject.id} className="subject-card">
              <div className="subject-header">
                <div className={`subject-icon ${subject.color}`}>
                  {subject.icon}
                </div>
                <div className="subject-info">
                  <h3>{subject.name}</h3>
                  <p>{subject.description}</p>
                </div>
              </div>

              <div className="subject-body">
                <div className="topics-list">
                  <span className="topic-label">Topics covered</span>
                  <div className="topic-tags">
                    {subject.topics.map((topic, index) => (
                      <span key={index} className="topic-tag">{topic}</span>
                    ))}
                  </div>
                </div>

                <div className="subject-stats">
                  <div className="subject-stat">
                    <div className="subject-stat-label">Total tests</div>
                    <div className="subject-stat-value">{subject.stats.totalTests}</div>
                  </div>
                  <div className="subject-stat">
                    <div className="subject-stat-label">Questions</div>
                    <div className="subject-stat-value">{subject.stats.questions}</div>
                  </div>
                  <div className="subject-stat">
                    <div className="subject-stat-label">Duration</div>
                    <div className="subject-stat-value">{subject.stats.duration} min</div>
                  </div>
                </div>
              </div>

              <div className="subject-footer">
                <button className="subject-btn">Practice</button>
                <button 
                  className={`subject-btn primary ${subject.color}`}
                  onClick={() => navigate(`/test/${examId}/${subject.id}`)}
                >
                  Start test
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SubjectSelection;
