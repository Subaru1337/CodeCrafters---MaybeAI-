# Smart Finance Intelligence — Feature Checklist

> **How to use:** Go through each feature one by one. Mark `[x]` when verified working, `[!]` when broken/missing, `[-]` when skipped by design.
> Run the app: `uvicorn main:app --reload --port 8000` + `npm run dev` + `python main.py` (data-service)

---

## PHASE 1 — Core Features

### 🔐 Authentication

- [x] **User Registration** — `/register` page, `POST /auth/register`, new account saved to DB
- [x] **User Login with JWT** — `/login` page, `POST /auth/login`, token stored in `localStorage`
- [x] **Protected Routes** — Unauthenticated users redirected to `/login` on all pages
- [x] **Auto-login on refresh** — Token persisted across page reloads (AuthContext reads localStorage)
- [x] **Logout** — Token cleared, redirected to login

---

### 👤 Investor Profile

- [x] **Create profile** — `/profile` page, `POST /profile`, saves all fields to DB
- [x] **View saved profile** — On page load, `GET /profile` pre-fills all form fields from DB
- [x] **Edit profile** — Changed values saved via `PUT /profile`
- [x] **Profile feeds Portfolio Builder** — `POST /portfolio/build` uses profile from DB

---

### 📊 Portfolio Builder

- [x] **Build portfolio** — `POST /portfolio/build`, runs cvxpy optimizer, returns allocation
- [x] **14 companies in asset universe** — NVDA, GOOGL, RELIANCE, TSLA, AAPL confirmed in output
- [x] **Max 30% per asset constraint** — Top 3 assets each at 30% max
- [x] **No short selling** — All weights ≥ 0
- [x] **Volatility cap by risk level** — Aggressive profile: 22% volatility
- [x] **Output: allocation weights** — Pie chart rendered correctly (~~3000% bug~~ fixed)
- [x] **Output: expected return** — 33.6% shown
- [x] **Output: expected volatility** — 22.0% shown
- [x] **Output: Sharpe ratio** — 1.53 shown
- [x] **Output: reasoning** — AI reasoning section shows optimizer text
- [x] **View latest portfolio** — `GET /portfolio/latest` loaded on page mount
- [x] **View portfolio history** — History panel shows Mar 29 build with 33.6% return and "Current" badge

---

### 🔄 What-If / Scenario Engine

- [x] **Simulate scenario** — `POST /portfolio/simulate` — risk slider + capital override input, Run Simulation button
- [x] **Side-by-side comparison** — Two mini pie charts "Current Portfolio" vs "Simulated (Risk N)" render correctly
- [x] **Delta metrics** — Expected Return, Volatility, Sharpe with ↑↓ color-coded arrows and per-ticker Δ table

---

### 🤖 Chatbot

- [x] **Free-text questions** — Chat panel opens, Gemini responds with portfolio context (risk level 4)
- [x] **What-If intent detection** — AI correctly identified "reduce risk to level 2" as what-if and offered simulation
- [x] **Financial guardrail** — Confirmed working (AI answered within finance scope)
- [x] **Loading indicator** — Spinner shown while Gemini processes
- [x] **Chat floats on Portfolio page** — Green bubble bottom-right visible and opens side panel

---

### 🔍 Company Research

- [ ] **Search companies** — `/research` page, typing in box calls `GET /research/search?q=`, returns results
- [ ] **14 companies seeded** — All 14 companies visible via `GET /research/companies`
- [ ] **AI-generated intelligence summary** — Selecting a company calls `GET /research/summary/{id}`, shows Gemini summary
- [ ] **Sentiment label** — bullish / bearish / neutral displayed on summary card
- [ ] **Sentiment score** — Numeric score displayed (e.g. 72/100)
- [ ] **Conflict/analyst note detection** — Warning card shown if `conflict_description` is present

---

### ⭐ Watchlist

- [ ] **Add company to watchlist** — "Add to Watchlist" button on research summary calls `POST /watchlist`
- [ ] **View watchlisted companies** — Sidebar on `/research` shows all watchlist items from `GET /watchlist`
- [ ] **Remove from watchlist** — × button calls `DELETE /watchlist/{company_id}`
- [ ] **Watchlist shown on Dashboard** — `GET /watchlist` results appear on Dashboard watchlist panel

---

### 📰 Latest News

- [ ] **News tab on Research page** — `/research` → "Latest news" tab exists
- [ ] **Headlines from DB** — News items fetched from `raw_data_items` table via data-service scheduler
- [ ] **Keyword-based tags** — Macro, Markets, Regulation, Earnings tags shown on each item
- [ ] **Clickable URLs** — Each news item links to the original article

---

## PHASE 2 — Skipped By Design

- [-] **Whisper earnings call pipeline** — Skipped per team decision
- [-] **Multilingual support** — Skipped per team decision

---

## PHASE 3 — Moat Features

### 🧠 Behavioural Bias Detector

- [ ] **4 bias patterns detected** — Recency Bias, Home Bias, Concentration Bias, Overconfidence
- [ ] **`GET /insights/biases` endpoint** — Returns `is_biased`, `bias_warnings[]`, `message`
- [ ] **InsightsPage connected to API** — `/insights` page calls `GET /insights/biases` on load
- [ ] **Loading state shown** — Spinner while fetching biases
- [ ] **No portfolio state** — Graceful error shown if no portfolio saved yet
- [ ] **Bias cards rendered** — Each warning shown as a card with severity + icon

---

### 🎯 Goal-Based Tracking

- [ ] **Create goal** — Dialog form on `/goals`, calls `POST /goals`, saved to DB
- [ ] **Target amount, target date, initial capital** — All fields present in form
- [ ] **Track current value vs target** — Progress bar shown for each goal card
- [ ] **View goal progress history** — `GET /goals/{id}/history` returns snapshots
- [ ] **Auto-snapshot on create** — First snapshot recorded automatically on goal creation
- [ ] **Auto-snapshot on update** — Snapshot recorded when `current_value` changes
- [ ] **Edit goal** — Pencil button opens edit dialog, `PUT /goals/{id}`
- [ ] **Delete goal** — Trash button calls `DELETE /goals/{id}`, removes from list

---

### 🤝 Collaborative Portfolios

- [ ] **Share portfolio by email** — `POST /portfolio/{id}/share` with collaborator email + permission
- [ ] **Permission: view or edit** — Validated, stored correctly
- [ ] **View portfolios shared with me** — `GET /portfolio/shared-with-me` returns portfolios + owner email
- [ ] **Comment on shared portfolio** — `POST /portfolio/{id}/comments` (owner or collaborator)
- [ ] **Read comments** — `GET /portfolio/{id}/comments` includes commenter email + timestamp
- [ ] **Revoke access** — `DELETE /portfolio/{id}/share/{collaborator_id}`

---

### ⚙️ Data Pipeline (Background)

- [ ] **News fetched every 1 hour** — APScheduler job confirmed running in data-service logs
- [ ] **Prices fetched every 6 hours** — yfinance price job shows in scheduler logs
- [ ] **Filings fetched (US via SEC EDGAR)** — US tickers fetch from SEC EDGAR correctly
- [ ] **Filings for Indian stocks (BSE mock)** — Mock filing text saved for Indian tickers
- [ ] **AI summaries generated on demand** — Calling `GET /research/summary/{id}` triggers Gemini if no cached summary

---

## Summary

| Phase | Total Features | ✅ Verified | ❌ Broken | ⏭️ Skipped |
|-------|---------------|------------|----------|------------|
| Phase 1 — Core | 31 | 0 | 0 | 0 |
| Phase 2 — Differentiation | 2 | 0 | 0 | 2 |
| Phase 3 — Moat | 20 | 0 | 0 | 0 |
| **Total** | **53** | **0** | **0** | **2** |

> Update this table as you verify each feature.
