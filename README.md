# AI Ticket Classifier

A full-stack web application that classifies customer support tickets into
categories using a machine-learning model. Paste in a ticket like
*"I was charged twice for my subscription"* and the API predicts a label
(**billing**) with a confidence score, stores the result, and keeps a
history you can browse and aggregate.

**Labels:** `billing`, `technical_support`, `account_access`, `shipping`,
`general`

## Demo flow

1. The React frontend sends ticket text to the FastAPI backend.
2. The backend runs the text through a trained scikit-learn pipeline
   (TF-IDF features + logistic regression) and returns the predicted label
   and confidence.
3. Every prediction is stored in a database, so the UI can show recent
   classifications and per-category statistics.

## Architecture

```
frontend/ (Vite + React)  --HTTP/JSON-->  app/ (FastAPI)
                                              |
                                    app/classifier.py
                                    loads models/ticket_classifier.joblib
                                    (scikit-learn Pipeline)
                                              |
                                    app/models.py (SQLAlchemy)
                                    SQLite by default, PostgreSQL
                                    via DATABASE_URL
```

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI application and endpoints |
| `app/classifier.py` | Loads the trained model, returns label + confidence |
| `app/models.py` / `app/database.py` | SQLAlchemy model and session setup |
| `app/schemas.py` | Pydantic request/response validation |
| `train_model.py` | Trains and evaluates the model, saves it with joblib |
| `data/tickets.csv` | Sample training dataset (see "Model" below) |
| `scripts/generate_dataset.py` | Regenerates the sample dataset |
| `tests/` | pytest suite for the API and the classifier |
| `frontend/` | Vite + React user interface |

## Tech stack

- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, uvicorn
- **ML:** scikit-learn (TfidfVectorizer + LogisticRegression), pandas, joblib
- **Database:** SQLite by default; PostgreSQL supported via `DATABASE_URL`
- **Frontend:** React, Vite
- **Tests:** pytest (FastAPI TestClient)
- **Packaging:** Docker + docker-compose (API + PostgreSQL)

## Setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python train_model.py            # trains the model into models/
uvicorn app.main:app --reload    # http://localhost:8000  (docs at /docs)
```

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

The frontend expects the API at `http://localhost:8000`. To change it,
set `VITE_API_URL` before running Vite.

### Docker (optional)

```bash
docker compose up --build        # API on :8000 backed by PostgreSQL
```

The API image trains the model during the build, so no separate training
step is needed in Docker.

## Model

- **Pipeline:** `TfidfVectorizer` (unigrams + bigrams, sublinear TF) feeding
  a `LogisticRegression` classifier, trained by `train_model.py`.
- **Dataset:** `data/tickets.csv` — a curated sample dataset of 450 labeled
  support tickets (90 per category) written for this project. Real-world
  use would train on a company's actual historical tickets; the code and
  evaluation flow are identical either way.
- **Evaluation:** stratified 80/20 train/test split (360 train / 90 test),
  measured by running `python train_model.py` in this repo:

| Metric | Value |
| --- | --- |
| **Test accuracy** | **0.9667** |
| Macro F1 | 0.97 |

Per-label results on the test split:

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| account_access | 1.00 | 0.89 | 0.94 |
| billing | 0.95 | 1.00 | 0.97 |
| general | 1.00 | 1.00 | 1.00 |
| shipping | 1.00 | 0.94 | 0.97 |
| technical_support | 0.90 | 1.00 | 0.95 |

Re-running `python train_model.py` reproduces these numbers and writes the
full metrics to `models/metrics.json`. Confidence scores returned by the
API come from the model's `predict_proba` output for the predicted class.

To retrain on different data, replace `data/tickets.csv` (columns:
`text,label`) and run `python train_model.py` again.

## API reference

### `GET /health`

```json
{ "status": "ok", "model_loaded": true }
```

### `POST /classify` — classify one ticket (stored)

Request:

```json
{ "text": "I was charged $79 twice for my subscription this month and I need a refund for the duplicate payment on my invoice." }
```

Response (`201`):

```json
{
  "id": 1,
  "text": "I was charged $79 twice for my subscription this month and I need a refund for the duplicate payment on my invoice.",
  "label": "billing",
  "confidence": 0.7661,
  "created_at": "2026-10-22T15:36:31.596121"
}
```

### `POST /classify/batch` — classify several tickets at once

Request: `{ "texts": ["...", "..."] }` (1–100 items, blanks rejected with
`422`). Response: `{ "results": [ ... ] }` with one stored record per text.

### `GET /tickets?limit=50&offset=0` — classification history

Returns stored classifications, most recent first.

### `GET /stats` — counts per label

```json
{
  "total": 4,
  "counts": {
    "account_access": 1,
    "billing": 1,
    "general": 0,
    "shipping": 1,
    "technical_support": 1
  }
}
```

Interactive documentation is available at `http://localhost:8000/docs`
when the API is running.

## Running the tests

```bash
pytest
```

The suite covers the classifier (label predictions, confidence range,
batch predictions) and every API endpoint, including validation errors and
the history/stats flow. Tests run against a temporary SQLite database; if
the model artifact is missing, the test setup trains it first.

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./tickets.db` | SQLAlchemy database URL (e.g. `postgresql+psycopg2://user:pass@host:5432/db`) |
| `MODEL_PATH` | `models/ticket_classifier.joblib` | Path to the trained model |
| `VITE_API_URL` (frontend) | `http://localhost:8000` | API base URL used by the React app |
