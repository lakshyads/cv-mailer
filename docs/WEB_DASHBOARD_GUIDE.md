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

1. **Node.js 18+** installed (`node --version`)
2. **CV Mailer API running** on port 8000 (see [Setup Guide](SETUP_GUIDE.md))
3. **Existing data** in database (run CLI at least once)

### Quick Start

```bash
cd frontend
npm install  # First time only
npm run dev
```

Open **<http://localhost:3000>**

**For complete setup:** See [Setup Guide](SETUP_GUIDE.md) | [Command Reference](COMMANDS.md)

## Features

### Dashboard

- Overview statistics (applications, emails, follow-ups)
- Visual charts (bar chart, pie chart)
- Recent applications list
- Real-time data updates

### Applications Page

- **Search** by company name or position
- **Filter** by status
- **Pagination** for large lists
- **Quick actions** - click to view details
- **Status updates** with notes
- **Progress tracker** visualization

**Application cards show:**

- Company name and position
- Location and status (color-coded)
- Dates and email count

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

See [Setup Guide](SETUP_GUIDE.md) for complete setup instructions.

**Quick setup:**

```bash
cd frontend
npm install  # First time only
npm run dev
```

**Prerequisites:**

- API must be running (see [Command Reference](COMMANDS.md))
- Node.js 18+ required

## Usage

### Starting the Dashboard

1. **Start API** (Terminal 1):

   ```bash
   cv-mailer-api
   ```

2. **Start Frontend** (Terminal 2):

   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**: <http://localhost:3000>

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

### Environment Variables (Optional)

Create `frontend/.env` to override API URL:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Default:** Uses Vite proxy (no configuration needed for development)

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

See [Troubleshooting Guide](TROUBLESHOOTING.md) for complete troubleshooting reference.

**Frontend-specific issues:**

- **Cannot connect to API** → Ensure API is running on port 8000
- **Build errors** → Clear `node_modules` and reinstall
- **Styling issues** → Check Tailwind CSS configuration
- **Data not updating** → Refresh page or check React Query cache
- **Port already in use** → Use `npm run dev -- --port 3001` or kill process on port 3000

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

## Development

See [frontend/README.md](../frontend/README.md) for complete development documentation including:

- Development commands
- File structure
- Code style guidelines
- Component patterns

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

## Related Documentation

- **[Command Reference](COMMANDS.md)** - All CLI and API commands
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Guide](API_GUIDE.md)** - Complete API documentation
- **[Setup Guide](SETUP_GUIDE.md)** - Complete setup instructions
- **[Frontend README](../frontend/README.md)** - Development documentation

---

**Need help?** Check [Troubleshooting Guide](TROUBLESHOOTING.md) or [Setup Guide](SETUP_GUIDE.md).
