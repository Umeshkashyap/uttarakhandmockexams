require('dotenv').config();
const mongoose = require('mongoose');
const Admin = require('../models/Admin');
const User = require('../models/User');
const TestResult = require('../models/TestResult');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('✅ MongoDB Connected');
  } catch (error) {
    console.error('❌ MongoDB connection error:', error);
    process.exit(1);
  }
};

const initializeDatabase = async () => {
  try {
    await connectDB();

    console.log('\n🔄 Initializing database...\n');

    // Create default admin if not exists
    const adminExists = await Admin.findOne({ username: process.env.ADMIN_USERNAME });
    
    if (!adminExists) {
      const admin = await Admin.create({
        username: process.env.ADMIN_USERNAME || 'admin',
        email: process.env.ADMIN_EMAIL || 'admin@mocktest.com',
        password: process.env.ADMIN_PASSWORD || 'admin123',
        role: 'superadmin'
      });
      console.log('✅ Default admin created');
      console.log(`   Username: ${admin.username}`);
      console.log(`   Email: ${admin.email}`);
    } else {
      console.log('ℹ️  Admin already exists');
    }

    // Create sample users
    const userCount = await User.countDocuments();
    
    if (userCount === 0) {
      const sampleUsers = [
        {
          name: 'Rahul Kumar',
          email: 'rahul@example.com',
          phone: '9876543210',
          examCategory: 'uttarakhand',
          testsCompleted: 24,
          totalScore: 1872,
          bestScore: 85
        },
        {
          name: 'Priya Sharma',
          email: 'priya@example.com',
          phone: '9876543211',
          examCategory: 'uttar-pradesh',
          testsCompleted: 18,
          totalScore: 1404,
          bestScore: 82
        },
        {
          name: 'Amit Patel',
          email: 'amit@example.com',
          phone: '9876543212',
          examCategory: 'ssc',
          testsCompleted: 22,
          totalScore: 1694,
          bestScore: 91
        },
        {
          name: 'Sneha Verma',
          email: 'sneha@example.com',
          phone: '9876543213',
          examCategory: 'uttarakhand',
          testsCompleted: 16,
          totalScore: 1232,
          bestScore: 89
        },
        {
          name: 'Vikas Singh',
          email: 'vikas@example.com',
          phone: '9876543214',
          examCategory: 'ssc',
          testsCompleted: 30,
          totalScore: 2850,
          bestScore: 95
        }
      ];

      for (let userData of sampleUsers) {
        const user = await User.create(userData);
        user.calculateAverageScore();
        await user.save();
      }

      console.log(`✅ Created ${sampleUsers.length} sample users`);
    } else {
      console.log(`ℹ️  ${userCount} users already exist`);
    }

    // Create sample test results
    const resultCount = await TestResult.countDocuments();
    
    if (resultCount === 0) {
      const users = await User.find().limit(5);
      
      if (users.length > 0) {
        const sampleResults = [];
        
        users.forEach(user => {
          for (let i = 0; i < 3; i++) {
            sampleResults.push({
              userId: user._id,
              examCategory: user.examCategory,
              subjectId: 'general-studies',
              subjectName: 'General Studies',
              totalQuestions: 50,
              answeredQuestions: 45 + Math.floor(Math.random() * 5),
              correctAnswers: 30 + Math.floor(Math.random() * 15),
              wrongAnswers: 10 + Math.floor(Math.random() * 10),
              score: 60 + Math.floor(Math.random() * 35),
              percentage: 60 + Math.floor(Math.random() * 35),
              timeTaken: 2400 + Math.floor(Math.random() * 1200),
              completedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
            });
          }
        });

        await TestResult.insertMany(sampleResults);
        console.log(`✅ Created ${sampleResults.length} sample test results`);
      }
    } else {
      console.log(`ℹ️  ${resultCount} test results already exist`);
    }

    console.log('\n✅ Database initialization complete!\n');
    console.log('📝 You can now login with:');
    console.log(`   Username: ${process.env.ADMIN_USERNAME || 'admin'}`);
    console.log(`   Password: ${process.env.ADMIN_PASSWORD || 'admin123'}\n`);

    process.exit(0);
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  }
};

initializeDatabase();
