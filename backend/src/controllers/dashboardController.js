const User = require('../models/User');
const TestResult = require('../models/TestResult');

// @desc    Get dashboard statistics
// @route   GET /api/admin/stats
// @access  Private
exports.getDashboardStats = async (req, res) => {
  try {
    // Get total users
    const totalUsers = await User.countDocuments({ isActive: true });

    // Get active tests (tests taken in last 24 hours)
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const activeTests = await TestResult.countDocuments({
      completedAt: { $gte: oneDayAgo }
    });

    // Get total questions (placeholder - update when question bank is implemented)
    const totalQuestions = 2850;

    // Calculate average score
    const avgScoreResult = await TestResult.aggregate([
      {
        $group: {
          _id: null,
          averageScore: { $avg: '$percentage' }
        }
      }
    ]);

    const averageScore = avgScoreResult.length > 0 
      ? Math.round(avgScoreResult[0].averageScore) 
      : 0;

    res.status(200).json({
      success: true,
      data: {
        totalUsers,
        activeTests,
        totalQuestions,
        averageScore
      }
    });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

// @desc    Get recent activities
// @route   GET /api/admin/activities
// @access  Private
exports.getRecentActivities = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;

    const activities = await TestResult.find()
      .populate('userId', 'name')
      .sort({ completedAt: -1 })
      .limit(limit)
      .select('userId subjectName score completedAt');

    const formattedActivities = activities.map(activity => ({
      user: activity.userId?.name || 'Unknown User',
      action: `Completed ${activity.subjectName} Test`,
      score: `${activity.score}%`,
      time: activity.completedAt
    }));

    res.status(200).json({
      success: true,
      data: formattedActivities
    });
  } catch (error) {
    console.error('Get activities error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

// @desc    Get top scorers
// @route   GET /api/admin/top-scorers
// @access  Private
exports.getTopScorers = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 5;

    const topScorers = await User.find({ isActive: true })
      .sort({ bestScore: -1, testsCompleted: -1 })
      .limit(limit)
      .select('name bestScore testsCompleted');

    const formattedScorers = topScorers.map((user, index) => ({
      rank: index + 1,
      name: user.name,
      score: `${user.bestScore}%`,
      tests: user.testsCompleted
    }));

    res.status(200).json({
      success: true,
      data: formattedScorers
    });
  } catch (error) {
    console.error('Get top scorers error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

// @desc    Get all users
// @route   GET /api/admin/users
// @access  Private
exports.getAllUsers = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const users = await User.find()
      .sort({ createdAt: -1 })
      .limit(limit)
      .skip(skip);

    const total = await User.countDocuments();

    res.status(200).json({
      success: true,
      data: {
        users,
        pagination: {
          total,
          page,
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};
