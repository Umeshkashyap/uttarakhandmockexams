const express = require('express');
const router = express.Router();
const { protect } = require('../middleware/auth');
const {
  login,
  getProfile,
  changePassword
} = require('../controllers/authController');

const {
  getDashboardStats,
  getRecentActivities,
  getTopScorers,
  getAllUsers
} = require('../controllers/dashboardController');

// Authentication routes
router.post('/login', login);
router.get('/profile', protect, getProfile);
router.put('/change-password', protect, changePassword);

// Dashboard routes
router.get('/stats', protect, getDashboardStats);
router.get('/activities', protect, getRecentActivities);
router.get('/top-scorers', protect, getTopScorers);
router.get('/users', protect, getAllUsers);

module.exports = router;
