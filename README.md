# 🚀 FinIntel: Smart Finance Intelligence

FinIntel is a premium, AI-driven financial platform designed to bridge the gap between complex market data and actionable investment strategies. Built with a modern full-stack architecture, it leverages high-performance optimization engines and generative AI to provide personalized wealth management experiences.

---

## ✨ Key Features

### 📊 AI-Optimized Portfolio Builder
- **Convex Optimizer**: Uses `cvxpy` to generate mathematically optimal asset allocations based on your unique risk profile.
- **Constraints Management**: Automatically handles diversification limits (e.g., max 30% per asset) and regulatory constraints (e.g., "No Crypto").
- **What-If Engine**: Simulate alternative scenarios instantly by overriding risk levels or capital amounts to compare performance side-by-side.

### 🤖 Intelligent Financial Assistant
- **Gemini Integration**: A context-aware chatbot that understands your current portfolio and investor profile.
- **Intent Detection**: Automatically detects when you're asking about simulations and triggers the What-If engine.
- **Financial Guardrails**: Specialized in financial advice while maintaining professional boundaries.

### 🔍 Research & Insights
- **Sentiment Analysis**: Real-time news aggregation and AI-powered sentiment scoring for top assets.
- **Behavioral Bias Detection**: Identifies cognitive biases like Recency Bias or Concentration Risk in your investment patterns.
- **Company Deep-Dives**: Detailed summaries and filing analysis powered by the AI research pipeline.

### 🎯 Goal Tracking & Collaboration
- **Milestone Snapshots**: Automatically records progress snapshots of your financial goals over time.
- **Collab Mode**: Share portfolios with partners or advisors, manage permissions (view/edit), and leave contextual comments.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, Shadcn UI, Recharts |
| **Backend** | FastAPI (Python 3.12+), SQLAlchemy, JWT Authentication |
| **Database** | PostgreSQL (NeonDB / Local) |
| **AI/ML** | Google Gemini Pro, cvxpy (Advanced Optimizer) |
| **Data** | NewsAPI, Alpha Vantage |

---

## 🚀 Getting Started

### 1. Backend Setup (api-service/data-service)
1. Navigate to `api-service` and `data-service`.
2. Create a `.env` file based on `.env.example`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
5. Start the Data Scheduler:
   ```bash
   python main.py
   ```

### 2. Frontend Setup (Front/Frontend)
1. Navigate to `Front/Frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```

---

## 🔒 Security & Best Practices
- **JWT-based Auth**: Secure session management.
- **Environment Isolation**: Sensitive keys are managed via `.env` (never pushed to Git).
- **Type Safety**: Full TypeScript implementation on the frontend for robust data handling.

---

## 👥 Contributors
- **Subaru1337** & Team

---
*Built for the Advanced Agentic Coding Workspace.*
