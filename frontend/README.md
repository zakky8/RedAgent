# AgentRed Frontend

The official frontend for AgentRed AI Red Teaming Platform built with Next.js 16.1, TypeScript, and Tailwind CSS.

## Features

- **Modern UI**: Beautiful dark-themed interface with red accent colors
- **Real-time Updates**: Live scan progress tracking and WebSocket support
- **Dashboard**: Comprehensive overview of all scans, targets, and compliance status
- **Security Testing**: Create and manage AI security scans against 456 attack techniques
- **Compliance Tracking**: Monitor compliance against 6 major AI frameworks
- **Monitoring**: Real-time monitoring and alerting for production AI systems
- **Reports**: Generate executive, technical, and compliance-focused reports
- **Agents**: Manage monitoring and scanning agents with API keys

## Tech Stack

- **Framework**: Next.js 16.1
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS + custom dark theme
- **State Management**: Zustand
- **Data Fetching**: SWR with 30s auto-refresh
- **Forms**: React Hook Form + Zod validation
- **UI Components**: Custom components + Radix UI primitives
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ (recommended: 20 LTS)
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create `.env.local` from the example:

```bash
cp .env.local.example .env.local
```

3. Configure environment variables in `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Create a production build:

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                      # Next.js app directory
│   ├── (auth)/              # Authentication layout
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (dashboard)/         # Dashboard layout
│   │   ├── dashboard/
│   │   ├── scans/
│   │   ├── targets/
│   │   ├── compliance/
│   │   ├── reports/
│   │   ├── agents/
│   │   ├── monitor/
│   │   ├── settings/
│   │   └── layout.tsx
│   ├── page.tsx             # Landing page
│   ├── layout.tsx           # Root layout
│   └── globals.css          # Global styles
├── components/              # Reusable components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Badge.tsx
│   ├── Skeleton.tsx
│   ├── LoadingSpinner.tsx
│   ├── Sidebar.tsx
│   ├── Navbar.tsx
│   ├── StatsGrid.tsx
│   ├── RiskGauge.tsx
│   └── ...
├── lib/                     # Utilities
│   ├── api.ts              # API client
│   ├── auth.ts             # Auth utilities
│   ├── utils.ts            # Helper functions
├── types/                   # TypeScript types
│   └── index.ts
└── hooks/                   # Custom React hooks
```

## Key Features

### Authentication

- Email/password login and registration
- JWT-based authentication with localStorage
- Automatic redirect to login for protected routes
- User profile display in navbar

### Dashboard

- **Stats Grid**: Total scans, average risk score, open findings, compliance score
- **Risk Gauge**: Visual arc gauge for risk assessment
- **Trend Chart**: 30-day risk score trends
- **Recent Scans**: Table of latest scans with status badges
- **Compliance Widgets**: Score cards for 6 compliance frameworks
- **Quick Actions**: Buttons to start scans, add targets, generate reports

### Scans

- **List View**: Filter and search scans by status and target
- **New Scan Wizard**: 4-step process (target selection, mode, options, review)
- **Live Results**: Stream attack results in real-time with WebSocket
- **Result Details**: Severity-based colors, payload/response inspection, remediation guidance

### Targets

- Create and manage AI endpoints
- Support for multiple model types (GPT-4, Claude, Mistral, etc.)
- Status indicators (active/inactive)
- Quick actions (test, edit)

### Compliance

- 6 framework cards with score and status
- Detailed control view with evidence and remediation
- Gap analysis and requirement tracking

### Monitoring

- Real-time alert dashboard
- Session management with active/paused/completed states
- Critical alert highlighting
- Metrics tracking and visualization

### Reports

- Multiple report types (executive, detailed, compliance)
- Auto-generation with configurable options
- Download and view functionality
- Report templates

## API Integration

All API calls go through `/lib/api.ts` with automatic:

- JWT bearer token injection
- Error handling
- Content-type headers

Example:

```typescript
import { api } from "@/lib/api";

// Get data
const scans = await api.get<Scan[]>("/api/v1/scans");

// Create/update
await api.post("/api/v1/scans", { target_id, scan_mode });

// Patch
await api.patch("/api/v1/scans/{id}", { status: "running" });

// Delete
await api.delete("/api/v1/scans/{id}");
```

## Data Fetching

Uses SWR for efficient data fetching with caching and auto-refresh:

```typescript
import useSWR from "swr";
import { api } from "@/lib/api";

const { data: scans, isLoading } = useSWR<Scan[]>(
  "/api/v1/scans",
  (url) => api.get(url),
  { revalidateOnFocus: false, dedupingInterval: 30000 }
);
```

## Styling

### Dark Theme Colors

- Background: `#0f0f0f` (near black)
- Surface: `#1a1a1a` (dark gray)
- Accent: `#dc2626` (red-600)
- Border: `#1f2937` (gray-800)
- Text: `#f3f4f6` (gray-100)

### Custom Components

All UI components use Tailwind CSS with dark mode support:

- `Button`: primary, secondary, outline, ghost, danger variants
- `Input`: with label, error, and helper text
- `Card`: sections with header and footer
- `Badge`: colored badges for status and tags
- `Skeleton`: loading placeholders

## Performance

- Static generation where possible
- Image optimization with Next.js
- CSS-in-JS with Tailwind (purged in production)
- SWR deduplication and caching
- Lazy loading of routes and components

## Environment Variables

Required in `.env.local`:

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_WS_URL`: WebSocket URL (default: `ws://localhost:8000`)

Public vars (accessible in browser) must have `NEXT_PUBLIC_` prefix.

## Type Safety

Comprehensive TypeScript types in `/src/types/index.ts`:

- `Scan`: Scan data model
- `Target`: AI endpoint configuration
- `AttackResult`: Individual attack finding
- `ComplianceFramework`: Framework assessment
- `User`: User profile
- `DashboardStats`: Dashboard data

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

© 2024 AgentRed. All rights reserved.
