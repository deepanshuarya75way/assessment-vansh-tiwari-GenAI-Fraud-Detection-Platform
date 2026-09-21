# GenAI-Powered Financial Fraud Detection & Analytics Platform

Enterprise-style frontend scaffold for an IBM Generative AI internship project.

## What is included

- Requested end-to-end project folder structure
- Production-style React 19 + Vite + TypeScript frontend in `app/frontend`
- Dataset upload, processing flow, dashboard, fraud details, explainability, chatbot, report, and settings screens
- Theme switching, reusable UI components, charts, mock dataset services, and export helpers

## Frontend stack

- React 19
- Vite
- TypeScript
- Tailwind CSS
- React Router
- Framer Motion
- React Hook Form
- Zod
- Recharts
- Lucide Icons

## Run frontend

```bash
cd app/frontend
npm install
npm run dev
```

## Build frontend

```bash
cd app/frontend
npm run build
```

## Notes

- The frontend is fully mocked and ready for backend/API integration.
- Upload preview works on client-side using local file parsing.
- Fraud scores, insights, chatbot responses, and reports are simulated from realistic mock data until backend services are connected.
- To point the backend at Supabase Postgres, set `DATABASE_URL` to the Supabase connection string from the dashboard and keep `DATABASE_POOL_PRE_PING=true`.
- The provided Supabase project URL and publishable key can be used for frontend/client integration, but the backend database connection still needs the Postgres connection string or password from Supabase.


