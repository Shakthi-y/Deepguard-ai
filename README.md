# DeepGuard AI

**An Agentic AI System for Intelligent Image Authenticity Verification**

DeepGuard AI is a full-stack, agent-orchestrated web application that analyzes an
uploaded image through seven specialist AI agents and returns an honest,
confidence-scored verdict: **LIKELY REAL**, **LIKELY FAKE**, or **UNCERTAIN**.

Built for an AI & Data Science college project — demonstrates an agentic
architecture, a real Keras/TensorFlow model in production, forensic
cross-verification, and responsible-AI verdict design.

---

## Architecture

```
USER
 │  upload image
 ▼
AI ORCHESTRATOR  ───────────────────────────────────────────────
 │
 ├─► 1. Image Validation Agent      (MIME / size / integrity checks)
 ├─► 2. Deepfake Detection Agent    (model2_skincare.h5, 224×224 CNN)
 ├─► 3. Forensic Analysis Agent     (metadata, compression, dimensions)
 ├─► 4. Verification Agent         (cross-checks model vs forensic evidence)
 ├─► 5. Confidence Agent           (model confidence vs system confidence)
 ├─► 6. Explanation Agent          (Gemini-backed, grounded explanation)
 └─► 7. Report Agent               (PDF report generation, on demand)
 │
 ▼
FINAL VERDICT → FRONTEND DASHBOARD
```

Every agent has one job and only passes forward what it actually found —
the Explanation Agent is instructed never to invent evidence, and the
Forensic Agent only reports what it can measure.

## Project structure

```
deepguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 FastAPI app + routes
│   │   ├── config.py                Settings (paths, thresholds, CORS)
│   │   ├── schemas.py               Pydantic response models
│   │   ├── storage.py               JSON-file history store
│   │   ├── agents/
│   │   │   ├── orchestrator.py
│   │   │   ├── intake_agent.py
│   │   │   ├── detection_agent.py
│   │   │   ├── forensic_agent.py
│   │   │   ├── verification_agent.py
│   │   │   ├── confidence_agent.py
│   │   │   ├── explanation_agent.py
│   │   │   └── report_agent.py
│   │   ├── models/
│   │   │   └── deepfake_detector.py   Loads & runs model2_skincare.h5
│   │   └── services/
│   │       ├── gemini_service.py
│   │       └── image_service.py
│   ├── ml_models/                    ← put model2_skincare.h5 here
│   ├── uploads/                      (runtime, gitignored)
│   ├── reports/                      (runtime, gitignored)
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── run.sh
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## Setup

1. **Add your model file**

   Copy `model2_skincare.h5` into `backend/ml_models/`.

   If it's missing, DeepGuard AI still runs end-to-end in a clearly
   labeled **simulation mode** (deterministic pseudo-inference), so the
   rest of the pipeline stays demoable while you wire up the real model.

2. **Configure environment variables**

   ```bash
   cd backend
   cp .env.example .env
   # optionally add your GEMINI_API_KEY for richer explanations & chat
   ```

3. **Run the backend**

   ```bash
   ./run.sh
   ```

   This creates a virtualenv, installs `requirements.txt`, and starts
   uvicorn on `http://localhost:8000`. The frontend is served
   automatically from `backend/app/main.py` at `http://localhost:8000/`.

   Manual equivalent:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## API

| Method | Endpoint                    | Description                          |
|--------|------------------------------|---------------------------------------|
| POST   | `/api/analyze`               | Upload an image, run the full pipeline |
| GET    | `/api/analysis/{id}`         | Fetch a past analysis by ID           |
| GET    | `/api/history`                | List recent analyses                  |
| GET    | `/api/report/{id}`           | Download the PDF report               |
| POST   | `/api/chat`                   | Ask DeepGuard about a result          |
| GET    | `/api/health`                 | Backend + model status                |

## Frontend features

- Dark, glassmorphism, "forensic scan" visual identity
- Landing page with animated agent-pipeline visualization
- Drag-and-drop upload with client-side validation
- Live investigation screen — agents light up in sequence as they run
- Result dashboard with circular confidence gauges (model vs system)
- Interactive image viewer — zoom, pan, fullscreen
- Analysis history stored in the browser's local storage
- One-click PDF report download
- "Ask DeepGuard" chat, grounded in the current analysis
- Responsible-AI disclaimer shown on every result

## Responsible AI

DeepGuard AI never reports 100% certainty. Every result is one of three
verdicts — **LIKELY REAL**, **LIKELY FAKE**, or **UNCERTAIN** — each
paired with a model confidence score and a separate system confidence
score reflecting agreement between the model and forensic evidence.
Every screen carries the disclaimer:

> This is an AI-based authenticity assessment. This result is not
> absolute proof.

## Model notes

- Input: 224×224×3, pixels normalized to `[0, 1]`
- Classes: `0 = fake`, `1 = real`
- Reported training accuracy: 73.89%
- Decision threshold: `0.5` (configurable in `app/config.py`)

Because 73.89% accuracy leaves real room for error, the Verification
and Confidence agents exist specifically to avoid presenting a single
model score as gospel — conflicting forensic evidence downgrades a
confident model prediction to **UNCERTAIN**.
