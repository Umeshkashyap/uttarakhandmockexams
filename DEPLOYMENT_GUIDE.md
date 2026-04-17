# Deployment Guide - Mock Test Platform

## Quick Start Commands

### Development
```bash
npm install
npm start
```

### Production Build
```bash
npm run build
```

---

## Platform-Specific Deployment

### 1. Netlify (Recommended for beginners)

#### Via Netlify CLI
```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Build your app
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=build
```

#### Via Netlify UI (Easiest)
1. Push your code to GitHub/GitLab/Bitbucket
2. Go to https://app.netlify.com
3. Click "Add new site" → "Import an existing project"
4. Connect your repository
5. Configure build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `build`
6. Click "Deploy site"

**Environment Variables in Netlify:**
- Go to Site settings → Build & deploy → Environment
- Add your variables:
  ```
  REACT_APP_API_URL=your-api-url
  ```

---

### 2. Vercel (Great for React apps)

#### Via Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Deploy
vercel --prod
```

#### Via Vercel UI
1. Push your code to GitHub
2. Go to https://vercel.com
3. Click "New Project"
4. Import your repository
5. Vercel auto-detects React settings
6. Click "Deploy"

**Environment Variables in Vercel:**
- Go to Project Settings → Environment Variables
- Add your variables for Production, Preview, and Development

---

### 3. GitHub Pages

#### Setup
```bash
# Install gh-pages
npm install --save-dev gh-pages
```

#### Update package.json
Add these lines to your `package.json`:
```json
{
  "homepage": "https://your-username.github.io/mock-exam-platform",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

#### Deploy
```bash
npm run deploy
```

Your site will be live at: `https://your-username.github.io/mock-exam-platform`

---

### 4. Firebase Hosting

#### Setup
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init hosting
```

During initialization:
- Choose "Use an existing project" or create new
- Set public directory to: `build`
- Configure as single-page app: Yes
- Don't overwrite index.html: No

#### Deploy
```bash
# Build the app
npm run build

# Deploy to Firebase
firebase deploy
```

Your site will be live at: `https://your-project.web.app`

---

### 5. AWS S3 + CloudFront (Advanced)

#### Prerequisites
- AWS Account
- AWS CLI installed and configured

#### Steps
```bash
# Install AWS CLI (if not already)
# Follow: https://aws.amazon.com/cli/

# Build the app
npm run build

# Create S3 bucket
aws s3 mb s3://mock-exam-platform

# Enable static website hosting
aws s3 website s3://mock-exam-platform --index-document index.html --error-document index.html

# Upload build files
aws s3 sync build/ s3://mock-exam-platform

# Make files public
aws s3 policy put-bucket-policy --bucket mock-exam-platform --policy file://bucket-policy.json
```

Create `bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::mock-exam-platform/*"
    }
  ]
}
```

---

### 6. Heroku (With Express Server)

#### Create server.js
```javascript
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, 'build')));

app.get('/*', function (req, res) {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

#### Deploy
```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create mock-exam-platform

# Add express to package.json
npm install express --save

# Update package.json scripts
"scripts": {
  "start": "node server.js",
  "build": "react-scripts build"
}

# Deploy
git push heroku main
```

---

## Environment Variables Setup

### Local Development (.env)
```env
REACT_APP_NAME=Mock Test Platform
REACT_APP_VERSION=1.0.0
NODE_ENV=development
```

### Production
```env
REACT_APP_NAME=Mock Test Platform
REACT_APP_VERSION=1.0.0
NODE_ENV=production
REACT_APP_API_URL=https://api.yoursite.com
```

### Setting Env Vars by Platform

**Netlify**: Site Settings → Build & deploy → Environment
**Vercel**: Project Settings → Environment Variables
**Heroku**: Settings → Config Vars
**Firebase**: Use `.env.production` file
**GitHub Pages**: Not supported (use build-time variables only)

---

## Build Optimization

### Before Deploying

1. **Remove console.logs**
```bash
# Install babel plugin
npm install --save-dev babel-plugin-transform-remove-console
```

2. **Optimize images**
- Use WebP format
- Compress images
- Use lazy loading

3. **Check bundle size**
```bash
npm run build
# Check build/static/js folder
```

4. **Test production build locally**
```bash
npm install -g serve
serve -s build -p 3000
```

---

## Post-Deployment Checklist

- [ ] Site loads correctly
- [ ] All routes work (test navigation)
- [ ] Images load properly
- [ ] Responsive design works on mobile
- [ ] No console errors
- [ ] Environment variables are set
- [ ] HTTPS is enabled
- [ ] Custom domain configured (if applicable)
- [ ] Analytics installed (Google Analytics, etc.)
- [ ] Performance tested (Lighthouse)

---

## Custom Domain Setup

### Netlify
1. Go to Domain settings
2. Add custom domain
3. Update DNS records with your domain provider
4. HTTPS automatically enabled

### Vercel
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records
4. SSL certificate auto-generated

### GitHub Pages
1. Add `CNAME` file to `public/` folder with your domain
2. Update DNS records:
   ```
   CNAME record: www → your-username.github.io
   A records: @ → GitHub IPs
   ```

---

## Continuous Deployment (CD)

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Netlify

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: npm install
    
    - name: Build
      run: npm run build
    
    - name: Deploy to Netlify
      uses: netlify/actions/cli@master
      with:
        args: deploy --prod --dir=build
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

---

## Monitoring & Analytics

### Add Google Analytics

1. Get tracking ID from Google Analytics
2. Add to `public/index.html`:
```html
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## Troubleshooting

### Build Fails
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Routes don't work after deployment
- Ensure platform is configured for SPA
- Check redirect rules (Netlify: `_redirects`, Vercel: `vercel.json`)

### Environment variables not working
- Verify they start with `REACT_APP_`
- Rebuild after adding new variables
- Check platform-specific env var settings

---

## Performance Tips

1. **Enable Gzip compression** (most platforms do this automatically)
2. **Use CDN** (Netlify and Vercel include this)
3. **Optimize images** before building
4. **Code splitting** (React Router does this)
5. **Lazy load components**

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] No sensitive data in client code
- [ ] Environment variables properly secured
- [ ] CORS configured correctly
- [ ] Content Security Policy headers set
- [ ] Regular dependency updates

---

**Need help?** Check platform-specific documentation or the main README.md file.
