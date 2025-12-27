# Web Dashboard Guide

Complete guide to using the CV Mailer Web Dashboard - a modern React-based interface for managing your job applications.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

The CV Mailer Web Dashboard is a modern, professional web interface that provides:

- 📊 **Visual Analytics** - Charts and statistics about your applications
- 📝 **Application Management** - View, search, filter, and update applications
- 👥 **Recruiter Management** - Track and manage recruiter contacts
- 📧 **Email History** - Complete communication timeline
- 🎨 **Modern UI** - Clean, responsive design that works on all devices

**Technology Stack:**
- React 18 with TypeScript
- Tailwind CSS for styling
- TanStack Query for data fetching
- Recharts for visualizations
- Vite for fast development

## Getting Started

### Prerequisites

Before you start, ensure you have:

1. **Node.js 18 or higher** installed
   ```bash
   node --version  # Should be v18.0.0 or higher
   ```

2. **CV Mailer API running** on port 8000
   ```bash
   # In the project root
   source venv/bin/activate
   cv-mailer-api
   ```

3. **Existing data** in your database (run the CLI at least once to sync from Google Sheets)

### Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open your browser to **http://localhost:3000**

## Features

### 1. Dashboard

**Overview Statistics:**
- Total applications count
- Total emails sent
- Follow-up emails count
- Response rate percentage

**Visualizations:**
- Bar chart of applications by status
- Pie chart showing status distribution
- Recent applications list

**Navigation:**
- Quick access to all major sections
- Real-time data updates

### 2. Applications Page

**Features:**
- **Search**: Find applications by company name or position
- **Filter**: Filter by status (draft, applied, interviewing, etc.)
- **Pagination**: Navigate through large lists efficiently
- **Quick Actions**: Click any application to view details

**Application Cards Show:**
- Company name and position
- Location
- Current status (color-coded)
- Creation and application dates
- Number of emails sent

### 3. Application Detail Page

**Complete Information:**
- Full job details (location, salary, posting URL)
- Timeline (created, applied, updated, closed dates)
- Custom messages and notes
- Associated recruiters with contact info

**Email History:**
- Complete communication log
- Email type (cold email, follow-up, etc.)
- Recipient information
- Send status and timestamps
- Follow-up tracking

**Status Management:**
- Update application status
- Add notes for each status change
- Real-time updates across the dashboard

### 4. Recruiters Page

**Features:**
- Grid view of all recruiters
- Contact information at a glance
- Application count per recruiter
- Click to view detailed information

### 5. Recruiter Detail Page

**Shows:**
- Complete contact information
- All associated applications
- Timeline of interactions
- Quick navigation to applications

## Installation

### Development Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server with hot reload
npm run dev
```

The development server includes:
- Hot module replacement (instant updates)
- Proxy to backend API
- Type checking
- ESLint integration

### Production Build

```bash
# Build optimized production bundle
npm run build

# Output will be in 'dist' directory
# Preview production build locally
npm run preview
```

## Usage

### Starting the Dashboard

**Step 1: Start the API**
```bash
# Terminal 1 - In project root
source venv/bin/activate
cv-mailer-api

# API will run on http://localhost:8000
```

**Step 2: Start the Frontend**
```bash
# Terminal 2 - In frontend directory
npm run dev

# Dashboard will run on http://localhost:3000
```

**Step 3: Open Browser**
- Navigate to http://localhost:3000
- Dashboard will automatically connect to API

### Common Workflows

#### View Application Statistics

1. Click **Dashboard** in sidebar
2. View overview cards at top
3. Analyze charts for status distribution
4. Check recent applications list

#### Search for Applications

1. Go to **Applications** page
2. Use search bar to find by company/position
3. Or use status filter dropdown
4. Click any application for details

#### Update Application Status

1. Open application detail page
2. Scroll to **Update Status** card (right sidebar)
3. Select new status from dropdown
4. Optionally add notes
5. Click **Update Status** button

#### Track Recruiter Communications

1. Go to **Recruiters** page
2. Click on recruiter card
3. View all associated applications
4. Click application to see email history

## Configuration

### Environment Variables

Create `frontend/.env` file (optional):

```env
# Override API URL (default: /api/v1 with proxy)
VITE_API_URL=http://localhost:8000/api/v1
```

**When to use:**
- Custom API port
- Production deployment
- Different backend server

### Proxy Configuration

The default setup uses Vite proxy (no env var needed):

```typescript
// vite.config.ts (already configured)
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

This allows the frontend to make API calls to `/api/v1/*` which proxies to the backend.

### Customization

#### Change Theme Colors

Edit `frontend/src/index.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Blue */
  --secondary: 210 40% 96.1%;     /* Gray */
  /* ... other colors */
}
```

#### Modify Navigation

Edit `frontend/src/components/Layout.tsx`:

```typescript
const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Applications', href: '/applications', icon: Briefcase },
  { name: 'Recruiters', href: '/recruiters', icon: Users },
  // Add more items here
];
```

## Deployment

### Option 1: Static Hosting (Vercel, Netlify)

```bash
# Build production bundle
npm run build

# Deploy 'dist' folder to:
# - Vercel: vercel --prod
# - Netlify: netlify deploy --prod
# - GitHub Pages: See docs
```

**Environment Setup:**
- Add `VITE_API_URL` pointing to your production API
- Ensure CORS is configured on API server

### Option 2: Docker

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

Build and run:

```bash
docker build -t cv-mailer-dashboard .
docker run -p 3000:80 cv-mailer-dashboard
```

### Option 3: Serve from FastAPI

Build frontend and configure FastAPI to serve static files:

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Files are in frontend/dist/
```

Update `src/cv_mailer/api/app.py`:

```python
from fastapi.staticfiles import StaticFiles

# After router includes
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

Now API and frontend run on same server!

## Troubleshooting

### Cannot Connect to API

**Problem:** Dashboard shows "Error loading data"

**Solutions:**
1. Ensure API is running: `curl http://localhost:8000/health`
2. Check browser console for errors (F12)
3. Verify proxy config in `vite.config.ts`
4. Check CORS settings in API

### Build Errors

**Problem:** `npm run build` fails

**Solutions:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Run type checker
npm run type-check
```

### Styling Issues

**Problem:** UI looks broken or unstyled

**Solutions:**
1. Check Tailwind CSS is working: inspect element (F12)
2. Rebuild: `npm run dev` (restart server)
3. Clear browser cache: Ctrl+Shift+R
4. Verify `index.css` imports Tailwind

### Data Not Updating

**Problem:** Changes in database not reflected in UI

**Solutions:**
1. Refresh page (Ctrl+R)
2. Check React Query cache: Components use 30s stale time
3. Restart development server: `npm run dev`
4. Check browser console for API errors

### Port Already in Use

**Problem:** Port 3000 is already taken

**Solutions:**
```bash
# Use different port
npm run dev -- --port 3001

# Or kill process on port 3000
lsof -ti:3000 | xargs kill
```

## Performance Tips

### Development

- Use React DevTools for profiling
- Keep components small and focused
- Leverage React Query caching
- Use pagination for large lists

### Production

- Enable gzip compression on server
- Use CDN for static assets
- Enable HTTP/2
- Monitor bundle size: `npm run build` shows sizes
- Consider lazy loading routes

## Browser Support

**Supported Browsers:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

**Features Used:**
- ES2020+ JavaScript
- CSS Grid and Flexbox
- Fetch API
- Local Storage

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Type checking
npm run type-check
```

## File Structure

```
frontend/
├── src/
│   ├── api/              # API client
│   ├── components/       # React components
│   │   ├── ui/          # Base UI components
│   │   └── ...          # Feature components
│   ├── pages/           # Route pages
│   ├── lib/             # Utilities
│   ├── types/           # TypeScript types
│   └── App.tsx          # Root component
├── public/              # Static assets
├── index.html           # HTML template
└── package.json         # Dependencies
```

## Best Practices

### For Users

1. Keep API running while using dashboard
2. Refresh data periodically
3. Use search/filters for large datasets
4. Update statuses regularly for accuracy

### For Developers

1. Follow TypeScript strictly
2. Use provided UI components
3. Keep API client updated with backend
4. Write responsive designs
5. Test on mobile devices

## Security Notes

**Current State:**
- No authentication implemented
- Designed for local/personal use
- API should not be exposed publicly

**Future Enhancements:**
- JWT authentication
- Role-based access control
- API key management

## Support

- **Documentation**: See other docs in `docs/` folder
- **API Reference**: http://localhost:8000/docs
- **Issues**: Report bugs on GitHub
- **Frontend README**: `frontend/README.md`

## Related Documentation

- [API Guide](API_GUIDE.md) - REST API reference
- [Setup Guide](SETUP_GUIDE.md) - Initial setup
- [Quick Start](QUICK_START.md) - Getting started
- [Architecture](design/ARCHITECTURE.md) - System design

---

**Last Updated**: December 2025  
**Version**: 1.0.0

Built with modern web technologies for the best user experience! 🚀

