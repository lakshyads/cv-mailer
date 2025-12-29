# CV Mailer Dashboard

Modern web interface for the CV Mailer application. Built with React, TypeScript, and Tailwind CSS.

## Features

- 📊 **Statistics Dashboard** - Visual overview with charts and metrics
- 📝 **Applications Management** - View, search, filter, and update job applications
- 👥 **Recruiter Contacts** - Manage recruiter information and relationships
- 📧 **Email History** - Track all email communications per application
- 🎨 **Modern UI** - Clean, professional design with responsive layout
- ⚡ **Fast & Efficient** - Built with Vite for optimal performance

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS with custom design system
- **Data Fetching**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: Sonner

## Getting Started

### Prerequisites

- Node.js 18+ or npm/yarn
- CV Mailer API running on port 8000 (see backend setup)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file (optional)
cp .env.example .env
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000 in your browser
```

The dev server includes a proxy to the backend API, so make sure your API is running on port 8000.

### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

### Type Checking

```bash
# Run TypeScript type checker
npm run type-check
```

### Linting

```bash
# Run ESLint
npm run lint
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── api/            # API client and endpoint definitions
│   │   └── client.ts   # Axios instance and API methods
│   ├── components/     # Reusable React components
│   │   ├── ui/         # Base UI components (Button, Card, etc.)
│   │   ├── Layout.tsx  # Main layout with navigation
│   │   └── ...
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   │   └── utils.ts    # Common utilities (cn, formatDate, etc.)
│   ├── pages/          # Page components (routes)
│   │   ├── DashboardPage.tsx
│   │   ├── ApplicationsPage.tsx
│   │   ├── ApplicationDetailPage.tsx
│   │   ├── RecruitersPage.tsx
│   │   └── RecruiterDetailPage.tsx
│   ├── types/          # TypeScript type definitions
│   │   └── index.ts    # API response types
│   ├── App.tsx         # Root component
│   ├── main.tsx        # Application entry point
│   └── index.css       # Global styles and Tailwind imports
├── index.html          # HTML template
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
├── vite.config.ts      # Vite configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## API Integration

The frontend communicates with the CV Mailer REST API. Key endpoints:

- `GET /api/v1/applications` - List applications
- `GET /api/v1/applications/:id` - Get application details
- `PUT /api/v1/applications/:id/status` - Update application status
- `GET /api/v1/applications/:id/emails` - Get email history
- `GET /api/v1/recruiters` - List recruiters
- `GET /api/v1/statistics` - Get statistics

See `src/api/client.ts` for full API implementation.

## Environment Variables

Create a `.env` file in the frontend directory:

```env
# Optional: Override API URL (defaults to proxy)
VITE_API_URL=http://localhost:8000/api/v1
```

## Design System

### Colors

The application uses a custom color palette based on HSL values:

- **Primary**: Blue (`#3b82f6`) - CTAs and highlights
- **Secondary**: Gray tones - Backgrounds and borders
- **Success**: Green - Positive actions
- **Destructive**: Red - Warnings and errors
- **Muted**: Light gray - Secondary text

### Components

All UI components follow a consistent design language:

- **Buttons**: Variants (default, outline, ghost, destructive)
- **Cards**: Elevated containers for content
- **Badges**: Status indicators with color coding
- **Tables**: Responsive data tables
- **Forms**: Consistent input styles

### Status Colors

Application statuses use color coding:

- **Draft**: Gray
- **Applied**: Blue
- **Interviewing**: Purple
- **Offer**: Green
- **Rejected**: Red
- **Accepted**: Emerald
- **Withdrawn**: Orange

## Features in Detail

### Dashboard

- Overview cards with key metrics
- Bar chart showing applications by status
- Pie chart for status distribution
- Recent applications list

### Applications

- Searchable and filterable table
- Pagination support
- Quick status updates
- Link to detailed view

### Application Details

- Complete application information
- Timeline of events
- Email communication history
- Associated recruiters
- Status update form

### Recruiters

- Grid view of all recruiters
- Application count per recruiter
- Detailed recruiter view with applications

## Development Guidelines

### Code Style

- Use TypeScript for type safety
- Follow React best practices and hooks patterns
- Use Tailwind CSS utility classes for styling
- Keep components focused and reusable
- Use TanStack Query for data fetching

### Component Creation

```tsx
// Example component structure
import { ComponentProps } from '@/types';
import { cn } from '@/lib/utils';

export function MyComponent({ className, ...props }: ComponentProps) {
  return (
    <div className={cn('default-classes', className)} {...props}>
      {/* Component content */}
    </div>
  );
}
```

### Data Fetching

```tsx
// Use React Query for API calls
import { useQuery } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';

const { data, isLoading, error } = useQuery({
  queryKey: ['applications'],
  queryFn: () => applicationsApi.list(),
});
```

## Troubleshooting

### API Connection Issues

- Ensure the backend API is running on port 8000
- Check CORS settings in the backend
- Verify proxy configuration in `vite.config.ts`

### Build Errors

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Run type checker: `npm run type-check`

### Styling Issues

- Ensure Tailwind CSS is properly configured
- Check `tailwind.config.js` for custom theme
- Verify CSS imports in `index.css`

## Contributing

1. Create a feature branch
2. Make your changes following the code style
3. Test thoroughly
4. Update types and documentation
5. Submit a pull request

## Production Deployment

### Option 1: Static Hosting (Vercel, Netlify)

```bash
npm run build
# Deploy the 'dist' folder
```

### Option 2: Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Option 3: Serve with Backend

Build the frontend and serve the `dist` folder from your FastAPI backend.

## License

Part of the CV Mailer project. See main project README for license information.

## Support

- **Documentation**: See `docs/` in the main project
- **Issues**: Report on GitHub
- **API Docs**: http://localhost:8000/docs (when running)

---

Built with ❤️ using modern web technologies

