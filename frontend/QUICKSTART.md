# Web Dashboard Quick Start

Get the CV Mailer Dashboard running in 3 minutes!

## Prerequisites Check

```bash
# Check Node.js (need 18+)
node --version

# Check npm
npm --version
```

Don't have Node.js? [Download here](https://nodejs.org/)

## Step 1: Setup (First Time Only)

```bash
cd frontend
./setup.sh
```

**Or manually:**
```bash
npm install
```

## Step 2: Start API

```bash
# In project root, new terminal
source venv/bin/activate
cv-mailer-api
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Start Dashboard

```bash
# In frontend directory, new terminal
npm run dev
```

You should see:
```
  VITE ready in 500 ms
  ➜  Local:   http://localhost:3000/
```

## Step 4: Open Browser

Navigate to: **http://localhost:3000**

## What You'll See

1. **Dashboard** - Statistics and charts
2. **Applications** - All your job applications
3. **Recruiters** - Contact management

## Common Issues

### API Connection Error
- ✅ Ensure API is running on port 8000
- ✅ Check: `curl http://localhost:8000/health`

### Port 3000 Already in Use
```bash
npm run dev -- --port 3001
```

### Dependencies Won't Install
```bash
rm -rf node_modules package-lock.json
npm install
```

## Build for Production

```bash
npm run build
# Output in 'dist' folder
```

## Full Documentation

- **Complete Guide**: `docs/WEB_DASHBOARD_GUIDE.md`
- **Frontend README**: `README.md`
- **Main Project**: `../README.md`

## Commands Cheat Sheet

```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production
npm run lint     # Check code quality
```

---

Need help? See `docs/WEB_DASHBOARD_GUIDE.md` for troubleshooting!

