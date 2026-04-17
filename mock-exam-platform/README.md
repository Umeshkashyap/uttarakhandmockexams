# Mock Test Platform

A modern, responsive mock examination platform built with React for competitive exam preparation.

## Features

- 📱 Fully responsive design
- 🎯 Three main exam categories: Uttarakhand, Uttar Pradesh, and SSC
- 📚 Subject-wise test organization
- ⏱️ Real-time test timer
- 🎨 Clean and professional UI
- ✅ Question palette with status tracking
- 📊 Test summary and progress tracking

## Tech Stack

- **Frontend**: React 18
- **Routing**: React Router DOM v6
- **Styling**: CSS3 (custom styles)
- **Build Tool**: Create React App

## Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js**: v14.0.0 or higher
- **npm**: v6.0.0 or higher (comes with Node.js)

To check your versions:
```bash
node --version
npm --version
```

## Installation

1. **Clone or navigate to the project directory**
```bash
cd mock-exam-platform
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
```
Edit `.env` file if you need to customize any settings.

## Development

### Start Development Server

```bash
npm start
```

This will:
- Start the development server at `http://localhost:3000`
- Automatically open your browser
- Enable hot-reloading (changes reflect automatically)

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

## Production Build

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder with:
- Minified JavaScript and CSS
- Optimized images
- Hashed filenames for caching
- Production-ready assets

### Test Production Build Locally

```bash
npm install -g serve
serve -s build
```

Visit `http://localhost:3000` to see the production build.

## Deployment

### Deploy to Netlify

1. **Install Netlify CLI**
```bash
npm install -g netlify-cli
```

2. **Build and deploy**
```bash
npm run build
netlify deploy --prod --dir=build
```

Or use the Netlify web interface:
- Connect your Git repository
- Set build command: `npm run build`
- Set publish directory: `build`

### Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Deploy**
```bash
vercel --prod
```

Or use the Vercel web interface:
- Import your Git repository
- Vercel auto-detects React
- Click "Deploy"

### Deploy to GitHub Pages

1. **Install gh-pages**
```bash
npm install --save-dev gh-pages
```

2. **Add to package.json**
```json
{
  "homepage": "https://yourusername.github.io/mock-exam-platform",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

3. **Deploy**
```bash
npm run deploy
```

### Deploy to Firebase Hosting

1. **Install Firebase CLI**
```bash
npm install -g firebase-tools
```

2. **Login and initialize**
```bash
firebase login
firebase init hosting
```

3. **Build and deploy**
```bash
npm run build
firebase deploy
```

## Environment Setup

### Development Environment

```env
REACT_APP_NAME=Mock Test Platform
REACT_APP_VERSION=1.0.0
NODE_ENV=development
```

### Production Environment

```env
REACT_APP_NAME=Mock Test Platform
REACT_APP_VERSION=1.0.0
NODE_ENV=production
REACT_APP_API_URL=https://your-production-api.com
```

## Project Structure

```
mock-exam-platform/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Dashboard.js
│   │   ├── Dashboard.css
│   │   ├── SubjectSelection.js
│   │   ├── SubjectSelection.css
│   │   ├── TestPage.js
│   │   └── TestPage.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── .env
├── .env.example
├── package.json
└── README.md
```

## Configuration

### Build Commands

| Platform | Build Command | Output Directory |
|----------|---------------|------------------|
| Netlify  | `npm run build` | `build` |
| Vercel   | `npm run build` | `build` |
| GitHub Pages | `npm run build` | `build` |
| Firebase | `npm run build` | `build` |

### Environment Variables

Set these in your deployment platform:

- `REACT_APP_NAME` - Application name
- `REACT_APP_VERSION` - Application version
- `REACT_APP_API_URL` - API endpoint (when backend is ready)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimization

The production build includes:
- Code splitting
- Tree shaking
- Minification
- Gzip compression
- Asset optimization

## Troubleshooting

### Port 3000 already in use
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

### Build fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Deployment issues
- Ensure `homepage` in package.json matches your deployment URL
- Check that environment variables are set correctly
- Verify build output in `build/` directory

## Future Enhancements

- [ ] Backend API integration
- [ ] User authentication
- [ ] Test result analytics
- [ ] Performance tracking
- [ ] Leaderboards
- [ ] Practice mode with explanations
- [ ] PDF result download
- [ ] Email notifications

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review deployment platform documentation
3. Check browser console for errors

## License

This project is licensed under the MIT License.

## Author

Created for competitive exam preparation.

---

**Happy Testing! 📚✨**
