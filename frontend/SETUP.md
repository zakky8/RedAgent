# AgentRed Frontend - Setup & Deployment Guide

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
npm install
```

2. **Setup environment:**
```bash
cp .env.local.example .env.local
# Edit .env.local with your backend API URL
```

3. **Run development server:**
```bash
npm run dev
```

4. **Open browser:**
Visit `http://localhost:3000`

### First Login

Use demo credentials during beta:
- Email: `demo@agentred.ai`
- Password: `password123`

Or register a new account at `/register`

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

ENV NODE_ENV production
EXPOSE 3000

CMD ["npm", "start"]
```

Build and run:

```bash
docker build -t agentred-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.agentred.com \
  -e NEXT_PUBLIC_WS_URL=wss://api.agentred.com \
  agentred-frontend
```

### Vercel Deployment

1. Push code to GitHub
2. Import repo at [vercel.com/new](https://vercel.com/new)
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_WS_URL`
4. Deploy

### Environment Variables

**Development (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

**Production:**
```
NEXT_PUBLIC_API_URL=https://api.agentred.com
NEXT_PUBLIC_WS_URL=wss://api.agentred.com
```

## Build & Optimization

### Production Build

```bash
npm run build
npm start
```

### Performance Tips

1. **Caching**: Update `dedupingInterval` in SWR configs for your needs
2. **Images**: Use Next.js Image component for optimization
3. **Code splitting**: Already handled by Next.js
4. **CSS**: Tailwind is purged automatically in production

### Bundle Analysis

```bash
npm install --save-dev @next/bundle-analyzer

# In next.config.ts, add:
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
export default withBundleAnalyzer(nextConfig)

# Run:
ANALYZE=true npm run build
```

## Configuration

### Tailwind CSS

Edit `tailwind.config.ts` for:
- Custom colors
- Typography
- Animations
- Plugins

### Next.js

Edit `next.config.ts` for:
- API rewrites
- Image domains
- Experimental features

## Development Workflow

### Adding a New Page

1. Create file in `src/app/` with folder structure
2. Export default component
3. Page auto-routes based on file path

Example:
```
src/app/(dashboard)/new-feature/page.tsx → /new-feature
```

### Adding a Component

1. Create file in `src/components/`
2. Use TypeScript for type safety
3. Export default component
4. Use Tailwind for styling

Example:
```typescript
interface MyComponentProps {
  title: string;
  variant?: "primary" | "secondary";
}

export default function MyComponent({
  title,
  variant = "primary",
}: MyComponentProps) {
  return <div className="...">{title}</div>;
}
```

### Adding a Hook

1. Create file in `src/hooks/`
2. Export named hook function
3. Use with `useEffect`, `useState`, etc.

Example:
```typescript
export function useMyHook() {
  const [state, setState] = useState(null);
  return { state, setState };
}
```

## Testing

### Unit Tests

Add Jest + React Testing Library:

```bash
npm install --save-dev jest @testing-library/react
```

Create `jest.config.js`:

```javascript
const nextJest = require('next/jest')
const createJestConfig = nextJest({
  dir: './',
})
module.exports = createJestConfig({
  testEnvironment: 'jest-environment-jsdom',
})
```

### E2E Tests

Add Playwright:

```bash
npm install --save-dev @playwright/test
```

## Troubleshooting

### Build Errors

1. Clear cache:
```bash
rm -rf .next node_modules
npm install
npm run build
```

2. Check Node version:
```bash
node --version  # Should be 18+
```

### API Connection Issues

1. Verify `NEXT_PUBLIC_API_URL`
2. Check CORS on backend
3. Test API directly:
```bash
curl http://localhost:8000/api/v1/health
```

### Performance Issues

1. Check Network tab in DevTools
2. Profile with Chrome DevTools
3. Check SWR cache settings
4. Reduce `dedupingInterval` if data is stale

## Monitoring

### Sentry Integration

Add error tracking:

```bash
npm install @sentry/nextjs
```

Initialize in `src/app/layout.tsx`:

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

### Analytics

Add Google Analytics:

```typescript
import { useEffect } from 'react';
import Script from 'next/script';

export function GoogleAnalytics() {
  return (
    <Script
      src="https://www.googletagmanager.com/gtag/js?id=GA_ID"
      strategy="afterInteractive"
    />
  );
}
```

## Security

### CORS

Ensure backend allows requests from frontend origin:

```
Access-Control-Allow-Origin: https://agentred.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
```

### CSP

Add Content Security Policy headers in `next.config.ts`:

```typescript
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        {
          key: 'Content-Security-Policy',
          value: "default-src 'self'"
        }
      ]
    }
  ]
}
```

### HTTPS

Always use HTTPS in production. Configure in deployment platform.

## Performance Benchmarks

Target metrics:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3.5s

Check with:
- [PageSpeed Insights](https://pagespeed.web.dev)
- [WebPageTest](https://www.webpagetest.org)
- Chrome DevTools Lighthouse

## Scaling

### For 10k+ concurrent users:

1. Enable static generation where possible
2. Use CDN for static assets
3. Implement database caching on backend
4. Consider Redis for session storage
5. Load balance across multiple instances

### Infrastructure:

- Kubernetes or Docker Compose
- Nginx reverse proxy
- PostgreSQL with connection pooling
- Redis cache
- S3 for reports/exports

## Support

For issues:
1. Check console errors (F12 DevTools)
2. Review browser network requests
3. Check backend API logs
4. Enable debug logging in SWR

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)
- [React Hook Form](https://react-hook-form.com)
- [SWR](https://swr.vercel.app)
