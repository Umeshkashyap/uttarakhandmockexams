# Mock Exam Platform - Backend API

REST API for Mock Exam Platform with MongoDB database and JWT authentication.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI

# Initialize database
npm run init-db

# Start server
npm run dev
```

## 📋 Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| **start** | `npm start` | Start production server |
| **dev** | `npm run dev` | Start development server with auto-reload |
| **init-db** | `npm run init-db` | Initialize database with sample data |

## 🔌 API Endpoints

### Base URL
```
http://localhost:5000/api
```

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/login` | Admin login | No |
| GET | `/admin/profile` | Get admin profile | Yes |
| PUT | `/admin/change-password` | Change password | Yes |

### Dashboard

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/stats` | Dashboard statistics | Yes |
| GET | `/admin/activities` | Recent activities | Yes |
| GET | `/admin/top-scorers` | Top performing users | Yes |
| GET | `/admin/users` | All users list | Yes |

## 🔐 Authentication

All protected endpoints require JWT token:

```bash
Authorization: Bearer {your-jwt-token}
```

## 📊 Database Models

### Admin
- username (unique)
- email (unique)
- password (hashed)
- role (admin/superadmin)
- isActive
- lastLogin

### User
- name
- email (unique)
- examCategory
- testsCompleted
- averageScore
- bestScore

### TestResult
- userId (reference)
- examCategory
- score
- percentage
- timeTaken
- answers

## 🔧 Environment Variables

```env
PORT=5000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/mock-exam-platform
JWT_SECRET=your-secret-key
JWT_EXPIRE=7d
FRONTEND_URL=http://localhost:3000
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Login
```bash
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📦 Dependencies

- **express** - Web framework
- **mongoose** - MongoDB ODM
- **jsonwebtoken** - JWT authentication
- **bcryptjs** - Password hashing
- **cors** - CORS middleware
- **dotenv** - Environment variables
- **express-validator** - Input validation

## 🔒 Security Features

✅ Password hashing with bcrypt
✅ JWT token authentication
✅ Protected routes middleware
✅ CORS configuration
✅ Input validation
✅ Secure password requirements

## 📝 Default Credentials

After running `npm run init-db`:

```
Username: admin
Password: admin123
```

## 🐛 Troubleshooting

**MongoDB Connection Failed**
- Ensure MongoDB is running
- Check MONGODB_URI in .env
- Verify network connectivity

**Port Already in Use**
- Change PORT in .env
- Kill process using the port

**JWT Token Invalid**
- Check JWT_SECRET
- Clear localStorage and re-login
- Verify token in request headers

## 📚 Documentation

See `DATABASE_SETUP_GUIDE.md` for detailed setup instructions.

## 🚀 Deployment

1. Set production environment variables
2. Use MongoDB Atlas for cloud database
3. Deploy to Heroku/Railway/DigitalOcean
4. Enable HTTPS
5. Set strong JWT secret

## 📄 License

MIT

---

**Built with ❤️ for education**
