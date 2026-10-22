"""FastAPI application: AI support-ticket classifier API.

Run with:
    uvicorn app.main:app --reload

Endpoints:
    GET  /health          Service health and model status
    POST /classify        Classify one ticket (stored in the database)
    POST /classify/batch  Classify a list of tickets (each stored)
    GET  /tickets         Classification history (most recent first)
    GET  /stats           Count of classified tickets per label
"""

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .classifier import ClassifierNotReadyError, classifier
from .database import Base, engine, get_db
from .models import Ticket
from .schemas import (
    BatchClassifyRequest,
    BatchClassifyResponse,
    ClassifyRequest,
    HealthResponse,
    StatsResponse,
    TicketOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Ticket Classifier",
    description="Classifies customer support tickets into categories using a "
    "scikit-learn model (TF-IDF + logistic regression).",
    version="1.0.0",
)

# The React dev server runs on a different port; allow it during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ClassifierNotReadyError)
async def classifier_not_ready_handler(_: Request, exc: ClassifierNotReadyError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


def _store_prediction(db: Session, text: str, label: str, confidence: float) -> Ticket:
    ticket = Ticket(text=text, label=label, confidence=confidence)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "model_loaded": classifier.is_loaded}


@app.post("/classify", response_model=TicketOut, status_code=201)
def classify_ticket(payload: ClassifyRequest, db: Session = Depends(get_db)):
    label, confidence = classifier.predict(payload.text)
    return _store_prediction(db, payload.text, label, confidence)


@app.post("/classify/batch", response_model=BatchClassifyResponse, status_code=201)
def classify_batch(payload: BatchClassifyRequest, db: Session = Depends(get_db)):
    try:
        texts = payload.cleaned_texts()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    predictions = classifier.predict_batch(texts)
    stored = [
        _store_prediction(db, text, label, confidence)
        for text, (label, confidence) in zip(texts, predictions)
    ]
    return {"results": stored}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Ticket)
        .order_by(Ticket.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@app.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    rows = db.query(Ticket.label, func.count(Ticket.id)).group_by(Ticket.label).all()
    counts = {label: 0 for label in classifier.labels}
    for label, count in rows:
        counts[label] = count
    return {"total": sum(counts.values()), "counts": counts}
