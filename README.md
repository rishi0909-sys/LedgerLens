# LedgerLens: Financial Forensics Intelligence

LedgerLens is an enterprise-grade AI investigation platform designed to solve the "Investigation Bottleneck" in modern financial institutions. It leverages **Multimodal Evidence Fusion** and **Reinforcement Learning (RL)** to optimally prioritize suspicious financial transactions for human review under strict budget constraints.

![LedgerLens Demo UI](https://via.placeholder.com/1200x600.png?text=LedgerLens+Dashboard) *(Replace with actual screenshot)*

## 🚀 The Core Problem

Fraud detection systems flag thousands of suspicious cases daily, but human investigation teams have limited bandwidth (a constrained budget). Traditional heuristic sorting (e.g., sorting by a single "risk score") ignores complex, cross-modal evidence and results in high false-positive rates, wasting valuable investigation time.

LedgerLens solves this by treating case prioritization as a sequential decision-making problem governed by Reinforcement Learning.

## 🧠 ML Systems Architecture

LedgerLens is not a simple "AI wrapper." It implements a complex, defensible machine learning architecture:

### 1. Multimodal Evidence Fusion
The platform doesn't just look at tabular data. It brings together distinct ML modalities into a single fused anomaly score:
*   **Transaction Baseline (XGBoost):** Evaluates standard tabular metadata.
*   **Sequential Deep Learning (LSTMs):** Analyzes the time-series behavior and velocity of account activity.
*   **Financial Graph ML (GNNs):** Maps topological network connections to detect laundering rings.
*   **Document Intelligence (FinBERT & OCR):** Extracts unstructured data from supporting documents (invoices, receipts) and computes semantic reconciliation conflicts.

### 2. Budget-Constrained RL Agent (`MaskablePPO`)
Given a queue of 20 suspicious cases and a budget of only 5 investigations, an RL Agent (trained via `Stable-Baselines3` in a custom `Gymnasium` environment) selects the optimal sequence of cases. The agent evaluates the observable state (fused risk scores, evidence conflicts, modality availability) to maximize true positive discoveries.

### 3. Human-in-the-Loop Offline Training (RLHF)
To prevent policy drift in production, LedgerLens implements a human-in-the-loop feedback layer. The **RL Copilot Chat** explicitly explains the agent's prioritization reasoning to the investigator. The investigator can agree or disagree, and these preferences are stored as structured events for subsequent offline policy retraining.

## 💻 Frontend Implementation

This repository currently contains the **Frontend Workbench**, built to demonstrate the platform's capabilities and UX. 

*   **Framework:** React 18 + Vite
*   **Styling:** Tailwind CSS + custom glassmorphic design system
*   **Icons:** Lucide React
*   **Responsiveness:** Fully mobile-responsive dashboard layouts
*   **State Management:** Complex local state machines simulating backend ML latency and RL processing pipelines (`api.ts`).

## 🛠️ Getting Started (Local Development)

The frontend is designed with robust mock data and graceful fallbacks, allowing you to run the entire demonstration locally without needing the Python/FastAPI ML backend running.

### Prerequisites
*   Node.js (v18+)
*   npm

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:5173`

## 🌍 Deployment

Because the application utilizes a simulated backend for demonstration purposes, it can be easily deployed as a static site.

We recommend deploying to **Vercel** or **Netlify**:
1. Connect your GitHub repository to Vercel/Netlify.
2. Set the Root Directory to `frontend`.
3. The Build Command will automatically be detected as `npm run build`.
4. Click Deploy!

Alternatively, a `Dockerfile.frontend` is provided for containerized deployments on AWS, DigitalOcean, or Fly.io.

## 🤝 Roadmap & Backend Integration

The current milestone demonstrates the UI, UX, and architectural theory via simulated API delays. 
**Next Steps for True Production:**
- [ ] Connect the `FastAPI` backend.
- [ ] Wire up the PostgreSQL / Supabase database to persist case states.
- [ ] Deploy the `MaskablePPO` inference server for real-time RL evaluations.
- [ ] Integrate the `FinBERT` pipeline for live OCR document processing.

## License
MIT License
