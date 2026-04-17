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
        id: 'uttarakhand-history',
        name: 'Uttarakhand History',
        description: 'Ancient to modern history of Uttarakhand including dynasties, freedom movement, and state formation',
        icon: '📜',
        color: 'blue',
        topics: ['Ancient Period', 'Medieval Period', 'British Era', 'Freedom Movement', 'State Formation 2000'],
        stats: {
          totalTests: 15,
          questions: 750,
          duration: 60
        }
      },
      {
        id: 'uttarakhand-geography',
        name: 'Uttarakhand Geography',
        description: 'Physical features, rivers, mountains, climate, natural resources, and administrative divisions',
        icon: '🗻',
        color: 'green',
        topics: ['Physical Geography', 'Rivers & Glaciers', 'Climate', 'Flora & Fauna', 'Districts'],
        stats: {
          totalTests: 12,
          questions: 600,
          duration: 60
        }
      },
      {
        id: 'uttarakhand-culture',
        name: 'Art & Culture',
        description: 'Folk music, dance, festivals, traditions, handicrafts, and cultural heritage of Uttarakhand',
        icon: '🎭',
        color: 'orange',
        topics: ['Folk Music & Dance', 'Festivals', 'Handicrafts', 'Temples', 'Traditions'],
        stats: {
          totalTests: 10,
          questions: 500,
          duration: 45
        }
      },
      {
        id: 'uttarakhand-economy',
        name: 'Economy & Development',
        description: 'Agriculture, industries, tourism, infrastructure, and economic development of Uttarakhand',
        icon: '📊',
        color: 'blue',
        topics: ['Agriculture', 'Industries', 'Tourism', 'Infrastructure', 'Budget & Finance'],
        stats: {
          totalTests: 8,
          questions: 400,
          duration: 45
        }
      },
      {
        id: 'uttarakhand-polity',
        name: 'Polity & Governance',
        description: 'State government structure, administrative setup, local governance, and constitutional provisions',
        icon: '🏛️',
        color: 'green',
        topics: ['State Government', 'Administration', 'Local Bodies', 'Acts & Policies', 'Electoral System'],
        stats: {
          totalTests: 10,
          questions: 500,
          duration: 60
        }
      },
      {
        id: 'current-affairs-uk',
        name: 'Current Affairs',
        description: 'Recent developments, government schemes, national and state level current affairs',
        icon: '📰',
        color: 'orange',
        topics: ['State News', 'Government Schemes', 'National Events', 'Awards & Honors', 'Sports'],
        stats: {
          totalTests: 20,
          questions: 1000,
          duration: 30
        }
      },
      {
        id: 'environment-ecology',
        name: 'Environment & Ecology',
        description: 'Environmental issues, conservation, wildlife, national parks, and sustainable development',
        icon: '🌲',
        color: 'green',
        topics: ['National Parks', 'Wildlife', 'Conservation', 'Climate Change', 'Biodiversity'],
        stats: {
          totalTests: 8,
          questions: 400,
          duration: 45
        }
      },
      {
        id: 'general-studies',
        name: 'General Studies',
        description: 'Comprehensive general knowledge covering India and world affairs, polity, science, and awareness',
        icon: '🌍',
        color: 'blue',
        topics: ['Indian Polity', 'History', 'Geography', 'Science', 'World Affairs'],
        stats: {
          totalTests: 15,
          questions: 750,
          duration: 75
        }
      },
      {
        id: 'aptitude-reasoning',
        name: 'Aptitude & Reasoning',
        description: 'Mathematical aptitude, logical reasoning, verbal ability, and analytical skills',
        icon: '🧠',
        color: 'orange',
        topics: ['Quantitative Aptitude', 'Logical Reasoning', 'Verbal Ability', 'Data Interpretation', 'Mental Ability'],
        stats: {
          totalTests: 12,
          questions: 600,
          duration: 60
        }
      },
      {
        id: 'hindi-language',
        name: 'Hindi Language',
        description: 'Hindi grammar, comprehension, vocabulary, and language proficiency tests',
        icon: '📝',
        color: 'green',
        topics: ['Grammar', 'Comprehension', 'Vocabulary', 'Writing Skills', 'Literature'],
        stats: {
          totalTests: 10,
          questions: 500,
          duration: 60
        }
      },
      {
        id: 'english-language',
        name: 'English Language',
        description: 'English grammar, comprehension, vocabulary, and communication skills',
        icon: '📖',
        color: 'blue',
        topics: ['Grammar', 'Comprehension', 'Vocabulary', 'Sentence Formation', 'Writing Skills'],
        stats: {
          totalTests: 10,
          questions: 500,
          duration: 60
        }
      },
      {
        id: 'computer-knowledge',
        name: 'Computer Awareness',
        description: 'Basic computer knowledge, MS Office, internet, and digital literacy',
        icon: '💻',
        color: 'orange',
        topics: ['Computer Basics', 'MS Office', 'Internet', 'Digital India', 'Cyber Security'],
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
