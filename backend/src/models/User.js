const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true
  },
  phone: {
    type: String,
    trim: true
  },
  examCategory: {
    type: String,
    enum: ['uttarakhand', 'uttar-pradesh', 'ssc', 'all'],
    default: 'all'
  },
  testsCompleted: {
    type: Number,
    default: 0
  },
  totalScore: {
    type: Number,
    default: 0
  },
  averageScore: {
    type: Number,
    default: 0
  },
  bestScore: {
    type: Number,
    default: 0
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastActive: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Calculate average score
userSchema.methods.calculateAverageScore = function() {
  if (this.testsCompleted > 0) {
    this.averageScore = Math.round(this.totalScore / this.testsCompleted);
  }
};

module.exports = mongoose.model('User', userSchema);
