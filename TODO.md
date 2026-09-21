# TODO - Enterprise Frontend Upgrade (GenAI Fraud Platform)

## Step 1: Audit existing UI/state
- [ ] Review Dashboard + Charts + Filters
- [ ] Review Fraud Details table behavior (sort/filter/search/pagination)
- [ ] Review Explainability UI fields mapping to required schema
- [ ] Review Chatbot UI layout, suggested questions, dataset-restricted behavior
- [ ] Review Reports screen sections + export buttons (PDF/Word/Excel)
- [ ] Review Settings screen sections (theme/profile/notifications/about)

## Step 2: Design system consistency
- [ ] Normalize colors/typography/shadows/glassmorphism across pages
- [ ] Replace any ad-hoc styling with reusable components

## Step 3: Responsiveness & polish
- [ ] Ensure tables/charts/filters behave on mobile/tablet
- [ ] Make framer-motion transitions subtle and consistent
- [ ] Add/adjust empty/loading states to be enterprise-grade

## Step 4: Feature mapping verification
- [ ] Processing pipeline steps match required list/order
- [ ] Explainability record includes: why detected, risk factors, confidence, affected features, AI explanation

## Step 5: Production readiness
- [ ] Run `npm run build` and fix TS/lint issues if any
- [ ] Smoke-test navigation across full flow

