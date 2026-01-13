# Subscription Detection - Hackathon Demo

> **Status:** 🚧 Work in Progress (Prototype)

## About the Project
A FinTech solution designed to help users detect and manage hidden or forgotten subscriptions.
This project uses algorithmic pattern recognition to parse bank statements (CSV) and identify recurring payments.

**Key Features (Demo):**
- 📂 **CSV Upload**: Parse bank statements locally.
- ⚡ **Recurring Payment Detection**: Identifies monthly/yearly subscriptions.
- 📊 **Dashboard**: Visualizes spending and potential savings.
- 📧 **Gmail Integration (Mock)**: Demonstrates the vision of email-based detection.

## 👥 Team Members
*   **Tamizharasan R** - Team Lead & Backend Developer
*   **Kaleeswaran M** - NLP Engineer & Algorithm Optimization
*   **Raga Sravya K** - Frontend Lead & UI/UX Designer
*   **Kubendiran M** - Data Engineer & Backend Developer

## 🛠️ Tech Stack
- **Frontend**: React (Vite), Tailwind CSS v4, Lucide React
- **Backend**: Python (FastAPI), Pandas, NumPy
- **ML/AI**: 
  - Isolation Forest (scikit-learn) - Unsupervised pattern detection
  - DBSCAN (scikit-learn) - Merchant name clustering
  - Sentence Transformers (all-MiniLM-L6-v2) - Text embeddings
- **Data**: CSV Processing (Local Analysis)

## 🚀 How to Run

### Backend
```bash
cd backend
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---
*Trial Project for HACKCELERATE - FinTech Track*
