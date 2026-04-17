const mongoose = require('mongoose');

const testResultSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  examCategory: {
    type: String,
    required: true,
    enum: ['uttarakhand', 'uttar-pradesh', 'ssc']
  },
  subjectId: {
    type: String,
    required: true
  },
  subjectName: {
    type: String,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  },
  answeredQuestions: {
    type: Number,
    default: 0
  },
  correctAnswers: {
    type: Number,
    default: 0
  },
  wrongAnswers: {
    type: Number,
    default: 0
  },
  score: {
    type: Number,
    required: true
  },
  percentage: {
    type: Number,
    required: true
  },
  timeTaken: {
    type: Number, // in seconds
    required: true
  },
  markedForReview: {
    type: [Number],
    default: []
  },
  answers: {
    type: Map,
    of: Number
  },
  completedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for faster queries
testResultSchema.index({ userId: 1, completedAt: -1 });
testResultSchema.index({ examCategory: 1, score: -1 });

module.exports = mongoose.model('TestResult', testResultSchema);
