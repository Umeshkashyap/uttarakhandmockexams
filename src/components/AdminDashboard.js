import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = ({ onBackToDashboard }) => {
  const [stats, setStats] = useState([
    { label: 'Total Users', value: '0', change: '+0%', icon: '👥' },
    { label: 'Active Tests', value: '0', change: '+0%', icon: '📝' },
    { label: 'Questions Bank', value: '0', change: '+0', icon: '❓' },
    { label: 'Avg Score', value: '0%', change: '+0%', icon: '📊' }
  ]);

  const [recentActivities, setRecentActivities] = useState([]);
  const [topScorers, setTopScorers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('adminToken');
    
    if (!token) {
      console.error('No admin token found');
      return;
    }

    try {
      // Fetch stats
      const statsResponse = await fetch(`${process.env.REACT_APP_API_URL}/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        if (statsData.success) {
          setStats([
            { label: 'Total Users', value: statsData.data.totalUsers.toString(), change: '+12%', icon: '👥' },
            { label: 'Active Tests', value: statsData.data.activeTests.toString(), change: '+5%', icon: '📝' },
            { label: 'Questions Bank', value: statsData.data.totalQuestions.toString(), change: '+28', icon: '❓' },
            { label: 'Avg Score', value: `${statsData.data.averageScore}%`, change: '+3%', icon: '📊' }
          ]);
        }
      }

      // Fetch activities
      const activitiesResponse = await fetch(`${process.env.REACT_APP_API_URL}/admin/activities?limit=4`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json();
        if (activitiesData.success) {
          setRecentActivities(activitiesData.data.map(activity => ({
            user: activity.user,
            action: activity.action,
            time: getTimeAgo(new Date(activity.time))
          })));
        }
      }

      // Fetch top scorers
      const scorersResponse = await fetch(`${process.env.REACT_APP_API_URL}/admin/top-scorers?limit=5`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (scorersResponse.ok) {
        const scorersData = await scorersResponse.json();
        if (scorersData.success) {
          setTopScorers(scorersData.data);
        }
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const getTimeAgo = (date) => {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds} seconds ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  };

  return (
    <div className="admin-dashboard-container">
      <header className="admin-header">
        <div className="admin-header-content">
          <div className="admin-title">
            <h1>Admin Dashboard</h1>
            <p>Monitor and manage your mock test platform</p>
          </div>
          <button className="back-to-dashboard-btn" onClick={onBackToDashboard}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Dashboard
          </button>
        </div>
      </header>

      {loading ? (
        <div className="admin-content">
          <div className="loading-message">Loading dashboard data...</div>
        </div>
      ) : (
        <div className="admin-content">
        <div className="admin-stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="admin-stat-card">
              <div className="stat-icon">{stat.icon}</div>
              <div className="stat-details">
                <div className="stat-label">{stat.label}</div>
                <div className="stat-value">{stat.value}</div>
                <div className="stat-change positive">{stat.change}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="admin-grid">
          <div className="admin-card">
            <div className="admin-card-header">
              <h3>Recent Activity</h3>
              <button className="view-all-btn">View All</button>
            </div>
            <div className="admin-card-body">
              <div className="activity-list">
                {recentActivities.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-avatar">
                      {activity.user.charAt(0)}
                    </div>
                    <div className="activity-details">
                      <div className="activity-user">{activity.user}</div>
                      <div className="activity-action">{activity.action}</div>
                    </div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="admin-card">
            <div className="admin-card-header">
              <h3>Top Scorers</h3>
              <button className="view-all-btn">View All</button>
            </div>
            <div className="admin-card-body">
              <div className="scorers-list">
                {topScorers.map((scorer) => (
                  <div key={scorer.rank} className="scorer-item">
                    <div className={`scorer-rank rank-${scorer.rank}`}>
                      {scorer.rank}
                    </div>
                    <div className="scorer-details">
                      <div className="scorer-name">{scorer.name}</div>
                      <div className="scorer-tests">{scorer.tests} tests completed</div>
                    </div>
                    <div className="scorer-score">{scorer.score}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="actions-grid">
            <button className="action-card">
              <div className="action-icon">➕</div>
              <div className="action-text">Add Question</div>
            </button>
            <button className="action-card">
              <div className="action-icon">📝</div>
              <div className="action-text">Create Test</div>
            </button>
            <button className="action-card">
              <div className="action-icon">👥</div>
              <div className="action-text">Manage Users</div>
            </button>
            <button className="action-card">
              <div className="action-icon">📊</div>
              <div className="action-text">View Reports</div>
            </button>
          </div>
        </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
