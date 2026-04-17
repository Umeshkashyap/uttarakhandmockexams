# Mock Exam Platform - Python Backend (Flask)

Complete REST API backend built with Flask, MongoDB, and JWT authentication.

---

## 🐍 Tech Stack

- **Flask** - Web framework
- **PyMongo** - MongoDB driver
- **PyJWT** - JWT authentication
- **Bcrypt** - Password hashing
- **Flask-CORS** - CORS handling
- **Python-dotenv** - Environment variables
- **Gunicorn** - Production server

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- pip (Python package manager)

### Installation

```bash
cd backend-python

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy .env file (already configured for local MongoDB)
# Edit .env if needed

# For MongoDB Atlas:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/mock-exam-platform
```

### Initialize Database

```bash
python app/config/init_database.py
```

**Output:**
```
✅ MongoDB Connected
✅ Default admin created
   Username: admin
   Email: admin@mocktest.com
✅ Created 5 sample users
✅ Created 15 sample test results
✅ Database initialization complete!
```

### Run Server

```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

**Server will start at:** http://localhost:5000

---

## 📁 Project Structure

```
backend-python/
├── app/
│   ├── config/
│   │   ├── database.py          # MongoDB connection
│   │   └── init_database.py     # Database initialization
│   ├── models/
│   │   ├── admin.py             # Admin model
│   │   ├── user.py              # User model
│   │   └── test_result.py       # TestResult model
│   ├── controllers/
│   │   ├── auth_controller.py   # Authentication logic
│   │   └── dashboard_controller.py  # Dashboard APIs
│   ├── middleware/
│   │   └── auth.py              # JWT middleware
│   └── routes/
│       └── admin_routes.py      # API routes
├── app.py                        # Flask application entry
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── README.md                     # This file
```

---

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
| GET | `/admin/top-scorers` | Top scorers | Yes |
| GET | `/admin/users` | All users | Yes |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Server health | No |

---

## 🧪 Testing Endpoints

### Using curl

**Login:**
```bash
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Get Stats (with token):**
```bash
curl -X GET http://localhost:5000/api/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

### Using Python requests

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/admin/login', json={
    'username': 'admin',
    'password': 'admin123'
})
data = response.json()
token = data['data']['token']

# Get stats
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/admin/stats', headers=headers)
print(response.json())
```

---

## 🔐 Authentication Flow

1. **Login** with username/password
2. **Receive** JWT token
3. **Include** token in Authorization header
4. **Access** protected routes

**Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🗄️ Database Models

### Admin Model

```python
{
    '_id': ObjectId,
    'username': str,
    'email': str,
    'password': bytes,  # bcrypt hash
    'role': str,  # 'admin' or 'superadmin'
    'isActive': bool,
    'lastLogin': datetime,
    'createdAt': datetime,
    'updatedAt': datetime
}
```

### User Model

```python
{
    '_id': ObjectId,
    'name': str,
    'email': str,
    'phone': str,
    'examCategory': str,
    'testsCompleted': int,
    'totalScore': int,
    'averageScore': int,
    'bestScore': int,
    'isActive': bool,
    'lastActive': datetime,
    'createdAt': datetime,
    'updatedAt': datetime
}
```

### TestResult Model

```python
{
    '_id': ObjectId,
    'userId': ObjectId,
    'examCategory': str,
    'subjectId': str,
    'subjectName': str,
    'totalQuestions': int,
    'answeredQuestions': int,
    'correctAnswers': int,
    'wrongAnswers': int,
    'score': int,
    'percentage': int,
    'timeTaken': int,  # seconds
    'markedForReview': list,
    'answers': dict,
    'completedAt': datetime,
    'createdAt': datetime
}
```

---

## 🔧 Environment Variables

```env
# Server
PORT=5000
FLASK_ENV=development  # or production

# MongoDB
MONGODB_URI=mongodb://localhost:27017/mock-exam-platform

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRE_DAYS=7

# CORS
FRONTEND_URL=http://localhost:3000

# Admin
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@mocktest.com
ADMIN_PASSWORD=admin123
```

---

## 🐛 Troubleshooting

### ModuleNotFoundError

**Issue:** Python can't find modules

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### MongoDB Connection Failed

**Issue:** Can't connect to MongoDB

**Solution:**
```bash
# Check if MongoDB is running
# Windows
net start MongoDB

# Mac
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Verify connection string in .env
```

### Import Error: No module named 'app'

**Issue:** Python can't find app module

**Solution:**
```bash
# Run from backend-python directory
cd backend-python
python app.py

# Or use absolute imports
PYTHONPATH=. python app.py
```

### JWT Decode Error

**Issue:** Token verification fails

**Solution:**
- Check JWT_SECRET matches on all requests
- Ensure token hasn't expired (7 days default)
- Verify token format: `Bearer <token>`

---

## 🚀 Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'

# With timeout
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 'app:create_app()'
```

### Using systemd (Linux)

Create `/etc/systemd/system/mockexam.service`:

```ini
[Unit]
Description=Mock Exam Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend-python
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start mockexam
sudo systemctl enable mockexam
```

### Render.com

```yaml
# In render.yaml
services:
  - type: web
    name: mock-exam-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT 'app:create_app()'
```

---

## 🔒 Security Best Practices

1. **Change default credentials** in production
2. **Use strong JWT_SECRET** (32+ characters)
3. **Enable HTTPS** in production
4. **Restrict CORS** to specific domains
5. **Keep dependencies updated**: `pip list --outdated`
6. **Never commit .env** to version control
7. **Use environment variables** for secrets
8. **Implement rate limiting** for production

---

## 📊 Performance Tips

1. **Use connection pooling** (PyMongo handles this)
2. **Add database indexes** for common queries
3. **Cache frequently accessed data**
4. **Use Gunicorn workers** (4 workers recommended)
5. **Enable compression** in production
6. **Monitor with logging**

---

## 🔄 Migration from Node.js

This Python backend is **100% compatible** with the existing Node.js backend. Same:

- ✅ API endpoints
- ✅ Request/response formats
- ✅ Database schema
- ✅ JWT tokens
- ✅ Authentication flow

**Switch backends without changing frontend!**

---

## 📝 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Change these in production!**

---

## 🧪 Running Tests

```bash
# Install pytest
pip install pytest pytest-flask

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| Flask-CORS | 4.0.0 | CORS handling |
| pymongo | 4.6.0 | MongoDB driver |
| python-dotenv | 1.0.0 | Environment variables |
| PyJWT | 2.8.0 | JWT tokens |
| bcrypt | 4.1.2 | Password hashing |
| gunicorn | 21.2.0 | Production server |

---

## 🆚 Python vs Node.js Comparison

| Feature | Python (Flask) | Node.js (Express) |
|---------|----------------|-------------------|
| Performance | Fast | Faster (async) |
| Learning Curve | Easy | Moderate |
| Community | Large | Very Large |
| Deployment | Simple | Simple |
| Best For | Data science integration | Real-time apps |

---

## 💡 Tips

- Use **virtual environment** to avoid conflicts
- Keep **requirements.txt** updated
- Use **type hints** for better code
- Enable **debug mode** in development only
- Use **logging** instead of print in production
- Implement **request validation**

---

## 📞 Support

**Common Commands:**

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python app/config/init_database.py

# Run server
python app.py

# Freeze dependencies
pip freeze > requirements.txt
```

---

## ✨ Features

- ✅ RESTful API design
- ✅ JWT authentication
- ✅ Bcrypt password hashing
- ✅ MongoDB integration
- ✅ CORS configuration
- ✅ Error handling
- ✅ Request logging
- ✅ Environment variables
- ✅ Production-ready
- ✅ Easy to deploy

---

**Built with ❤️ using Python & Flask**
