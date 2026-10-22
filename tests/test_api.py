"""End-to-end tests for the FastAPI endpoints (via TestClient)."""

BILLING_TEXT = "I was charged twice for my subscription and would like a refund for the duplicate charge."
ACCESS_TEXT = "I cannot log in to my account because the two-factor authentication codes are not accepted."


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_classify_single_ticket(client):
    response = client.post("/classify", json={"text": BILLING_TEXT})
    assert response.status_code == 201
    body = response.json()
    assert body["label"] == "billing"
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["text"] == BILLING_TEXT
    assert body["id"] >= 1
    assert body["created_at"]


def test_classify_empty_text_is_rejected(client):
    response = client.post("/classify", json={"text": ""})
    assert response.status_code == 422


def test_classify_missing_text_is_rejected(client):
    response = client.post("/classify", json={})
    assert response.status_code == 422


def test_classify_batch(client):
    response = client.post(
        "/classify/batch", json={"texts": [BILLING_TEXT, ACCESS_TEXT]}
    )
    assert response.status_code == 201
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["label"] == "billing"
    assert results[1]["label"] == "account_access"


def test_classify_batch_rejects_empty_list(client):
    response = client.post("/classify/batch", json={"texts": []})
    assert response.status_code == 422


def test_classify_batch_rejects_blank_items(client):
    response = client.post("/classify/batch", json={"texts": ["hello", "   "]})
    assert response.status_code == 422


def test_tickets_history_and_stats(client):
    client.post("/classify", json={"text": BILLING_TEXT})
    client.post("/classify", json={"text": ACCESS_TEXT})

    history = client.get("/tickets")
    assert history.status_code == 200
    tickets = history.json()
    assert len(tickets) == 2
    # Most recent first.
    assert tickets[0]["label"] == "account_access"
    assert tickets[1]["label"] == "billing"

    stats = client.get("/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert body["total"] == 2
    assert body["counts"]["billing"] == 1
    assert body["counts"]["account_access"] == 1
    assert body["counts"]["shipping"] == 0
