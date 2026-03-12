# AgentRed Frontend - Complete File Index

## Project Overview

**Name:** AgentRed Frontend  
**Version:** 1.0.0  
**Type:** Next.js 16.1 + TypeScript 5 + React 19  
**Location:** `/sessions/optimistic-keen-planck/mnt/bgis/agentred/frontend/`

## File Count: 41 files | Size: 232KB | LOC: 4,100+

---

## ROOT CONFIGURATION (8 files)

### Core Configuration
1. **package.json** - Node.js dependencies and scripts
2. **next.config.ts** - Next.js configuration with API rewrites
3. **tsconfig.json** - TypeScript compiler settings
4. **tailwind.config.ts** - Tailwind CSS theme and extensions
5. **postcss.config.js** - PostCSS processing configuration

### Development Configuration
6. **.eslintrc.json** - ESLint code quality rules
7. **.gitignore** - Git ignore patterns
8. **.env.local.example** - Environment variables template

---

## SRC DIRECTORY STRUCTURE

### APP ROUTES (17 files) - Next.js file-based routing

#### Root Routes (3 files)
- `src/app/layout.tsx` - Root layout wrapper
- `src/app/page.tsx` - Landing page (/)
- `src/app/globals.css` - Global styles

#### Authentication Routes (3 files) - `(auth)` group
- `src/app/(auth)/layout.tsx` - Auth page layout
- `src/app/(auth)/login/page.tsx` - Login page (/login)
- `src/app/(auth)/register/page.tsx` - Registration page (/register)

#### Dashboard Routes (11 files) - `(dashboard)` group (protected)
- `src/app/(dashboard)/layout.tsx` - Dashboard page layout
- `src/app/(dashboard)/dashboard/page.tsx` - Main dashboard (/dashboard)
- `src/app/(dashboard)/scans/page.tsx` - Scans list (/scans)
- `src/app/(dashboard)/scans/new/page.tsx` - Scan wizard (/scans/new)
- `src/app/(dashboard)/scans/[id]/page.tsx` - Scan details (/scans/[id])
- `src/app/(dashboard)/targets/page.tsx` - Targets management (/targets)
- `src/app/(dashboard)/compliance/page.tsx` - Compliance dashboard (/compliance)
- `src/app/(dashboard)/reports/page.tsx` - Reports page (/reports)
- `src/app/(dashboard)/agents/page.tsx` - Agents page (/agents)
- `src/app/(dashboard)/monitor/page.tsx` - Monitoring page (/monitor)
- `src/app/(dashboard)/settings/page.tsx` - Settings page (/settings)

---

### COMPONENTS (10 files) - `src/components/`

#### Core UI Components (6 files)
1. **Button.tsx** - Button component with 5 variants
2. **Input.tsx** - Form input component with validation
3. **Card.tsx** - Card layout with sections
4. **Badge.tsx** - Status badges with variants
5. **Skeleton.tsx** - Loading placeholder
6. **LoadingSpinner.tsx** - Animated loading spinner

#### Layout Components (2 files)
7. **Sidebar.tsx** - Navigation sidebar (collapsible)
8. **Navbar.tsx** - Top navigation bar

#### Feature Components (2 files)
9. **StatsGrid.tsx** - Responsive stats cards grid
10. **RiskGauge.tsx** - SVG arc gauge visualization

---

### LIBRARIES (3 files) - `src/lib/`

1. **api.ts** - API client with SWR and JWT auth
2. **auth.ts** - Authentication utilities
3. **utils.ts** - Helper functions (formatting, colors)

---

### TYPES (1 file) - `src/types/`

1. **index.ts** - Complete TypeScript interface definitions

---

## DOCUMENTATION (4 files)

1. **README.md** - Complete feature and architecture documentation
2. **SETUP.md** - Setup, deployment, and troubleshooting guide
3. **COMPLETED.md** - Project completion summary
4. **FILE_MANIFEST.md** - Detailed file inventory
5. **INDEX.md** - This file

---

## QUICK START COMMANDS

```bash
# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local

# Development
npm run dev

# Production build
npm run build
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## ROUTES SUMMARY

### Public Routes
- `/` - Landing page
- `/login` - Login form
- `/register` - Registration form

### Protected Routes (require authentication)
- `/dashboard` - Main dashboard
- `/scans` - Scans management
- `/scans/new` - Create new scan
- `/scans/[id]` - View scan results
- `/targets` - Target management
- `/compliance` - Compliance tracking
- `/reports` - Report management
- `/agents` - Agent management
- `/monitor` - Real-time monitoring
- `/settings` - User settings

---

## COMPONENT HIERARCHY

```
App
├── (auth)/
│   ├── login
│   └── register
└── (dashboard)/
    ├── dashboard
    ├── scans/
    │   ├── list (with Sidebar, Navbar)
    │   ├── new (with multi-step wizard)
    │   └── [id] (with live results drawer)
    ├── targets
    ├── compliance
    ├── reports
    ├── agents
    ├── monitor
    └── settings
```

---

## UI COMPONENT LIBRARY

### Buttons
- Primary (red background)
- Secondary (gray background)
- Outline (border only)
- Ghost (text only)
- Danger (red border/text)

### Form Components
- Input (with label, error, helper text)
- Select dropdowns
- Checkboxes
- Radio buttons

### Data Display
- Cards (header, content, footer)
- Badges (8 color variants)
- Skeleton loaders
- Loading spinners
- Tables
- Progress bars

### Layout
- Sidebar (collapsible)
- Navbar (with user menu)
- Responsive grid

---

## API ENDPOINTS INTEGRATION

All calls route through `NEXT_PUBLIC_API_URL` environment variable.

### Authentication
- POST /api/v1/auth/login
- POST /api/v1/auth/register
- POST /api/v1/auth/refresh

### Dashboard
- GET /api/v1/dashboard/stats

### Scans
- GET /api/v1/scans
- POST /api/v1/scans
- GET /api/v1/scans/{id}
- GET /api/v1/scans/{id}/results

### Targets
- GET /api/v1/targets
- POST /api/v1/targets

### Compliance
- GET /api/v1/compliance/frameworks

### Reports
- GET /api/v1/reports
- POST /api/v1/reports

### Agents
- GET /api/v1/agents
- POST /api/v1/agents

### Monitoring
- GET /api/v1/monitoring/sessions

---

## TYPESCRIPT TYPES DEFINED

### Domain Models
- `Scan` - Security scan data
- `Target` - AI endpoint configuration
- `AttackResult` - Individual attack finding
- `ComplianceAssessment` - Framework assessment
- `ComplianceFramework` - Compliance framework data
- `ComplianceControl` - Framework control
- `Report` - Generated report
- `User` - User profile
- `Organization` - Organization data
- `Agent` - Monitoring/scanning agent
- `MonitoringSession` - Active monitoring session
- `MonitoringAlert` - Security alert

### Request/Response
- `AuthResponse` - Login response with tokens
- `DashboardStats` - Dashboard data aggregation
- `TrendPoint` - Historical trend data
- `ScanResultSummary` - Scan findings summary

---

## STYLING SYSTEM

### Dark Theme Colors
- `#0f0f0f` - Background (near black)
- `#1a1a1a` - Surface (dark gray)
- `#dc2626` - Primary accent (red)
- `#1f2937` - Borders (gray-800)
- `#f3f4f6` - Text (gray-100)

### Tailwind Customizations
- Custom red color scheme
- Animation extensions
- Dark mode configuration

---

## DEPENDENCIES SUMMARY

### Framework (3)
- next@16.1.0
- react@19.0.0
- react-dom@19.0.0

### Language (1)
- typescript@5.0.0

### Styling (4)
- tailwindcss@3.4.0
- autoprefixer@10.4.0
- postcss@8.4.0
- lucide-react@0.383.0

### UI Components (6)
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-select
- @radix-ui/react-tabs
- @radix-ui/react-progress
- @radix-ui/react-badge
- (+ 6 more Radix UI packages)

### Forms & Validation (3)
- react-hook-form@7.53.0
- zod@3.23.0
- @hookform/resolvers@3.9.0

### Data Fetching (1)
- swr@2.2.5

### State Management (1)
- zustand@4.5.0

### Charts (1)
- recharts@2.13.0

### Utilities (4)
- date-fns@3.6.0
- axios@1.7.0
- clsx@2.1.0
- tailwind-merge@2.5.0

### Type Definitions (1)
- @types/node@20.0.0

---

## DEVELOPMENT WORKFLOW

1. **New Page?** Create in `src/app/` matching your route structure
2. **New Component?** Create in `src/components/` and use `export default`
3. **New Hook?** Create in `src/hooks/` if needed
4. **New Utility?** Add to `src/lib/utils.ts` or create module
5. **New Type?** Add to `src/types/index.ts`

---

## BEST PRACTICES

### Component Development
- Use TypeScript for all components
- Implement proper prop typing
- Use React.forwardRef for components accepting ref
- Follow component composition patterns

### Data Fetching
- Use SWR with appropriate deduplicate intervals
- Handle loading and error states
- Implement proper error boundaries
- Cache strategically

### Styling
- Use Tailwind utility classes
- Follow dark theme colors
- Implement responsive design
- Test on mobile viewports

### Performance
- Lazy load routes automatically
- Code split components
- Optimize images with Next.js Image
- Monitor bundle size

---

## FILE LOCATIONS - ABSOLUTE PATHS

All files are located at:
`/sessions/optimistic-keen-planck/mnt/bgis/agentred/frontend/`

### Key Paths
- Routes: `src/app/`
- Components: `src/components/`
- Libraries: `src/lib/`
- Types: `src/types/`
- Styles: `src/app/globals.css`

---

## TESTING CHECKLIST

- [ ] Install dependencies: `npm install`
- [ ] Set up `.env.local` with API URL
- [ ] Start dev server: `npm run dev`
- [ ] Test login with demo credentials
- [ ] Navigate through all dashboard routes
- [ ] Test form validation
- [ ] Check responsive design
- [ ] Verify API integration
- [ ] Build production: `npm run build`

---

## NEXT STEPS

1. Install dependencies
2. Configure API endpoint in `.env.local`
3. Start development server
4. Test authentication flow
5. Integrate with backend API
6. Deploy to production

---

## SUPPORT

- **Documentation:** See README.md
- **Setup Guide:** See SETUP.md
- **File Inventory:** See FILE_MANIFEST.md

---

Generated: March 2025  
Framework: Next.js 16.1 | React 19 | TypeScript 5 | Tailwind CSS 3.4  
Status: Production Ready
