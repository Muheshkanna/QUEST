"""FastAPI Endpoint Integration Tests for Math Quest."""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.index import app, set_llm_client
from api._lib.llm import MockClient


@pytest.fixture(autouse=True)
def reset_llm_client():
    """Reset the LLM client override after each test."""
    yield
    set_llm_client(None)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Happy Path Endpoint Tests
# ---------------------------------------------------------------------------

def test_api_health_happy_path(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert "engine" in data


def test_api_topics_happy_path(client):
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert isinstance(topics, list)
    assert len(topics) == 20
    # Check that playable and content_source are present
    playable_count = sum(1 for t in topics if t["playable"])
    assert playable_count == 12
    for t in topics:
        assert "playable" in t
        assert "content_source" in t


def test_api_topics_filtered_by_grade(client):
    response = client.get("/api/topics?grade=5")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) == 10
    assert all(t["grade"] == 5 for t in topics)


def test_api_lesson_happy_path(client):
    response = client.get("/api/lesson/g5-fractions-add")
    assert response.status_code == 200
    data = response.json()
    assert data["title"]
    assert data["big_idea"]
    assert len(data["worked_example"]) >= 1
    assert data["source"] == "offline"


def test_api_questions_happy_path(client):
    response = client.get("/api/questions/g5-fractions-add?difficulty=easy&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "g5-fractions-add"
    assert len(data["questions"]) == 3
    assert data["source"] == "offline"
    for q in data["questions"]:
        assert q["difficulty"] == "easy"
        assert len(q["options"]) == 4


def test_api_answer_happy_path_correct(client):
    # Fetch a question from g5-fractions-add
    q_resp = client.get("/api/questions/g5-fractions-add?difficulty=easy&limit=1")
    q = q_resp.json()["questions"][0]
    
    payload = {
        "topic_id": "g5-fractions-add",
        "question_id": q["id"],
        "chosen_index": q["correct_index"],
        "attempt": 1,
        "state": {"combo": 2, "p_known": 0.3, "consecutive_correct": 1},
    }
    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["correct_index"] == q["correct_index"]
    assert data["xp_awarded"] > 0
    assert data["combo"] == 3
    assert data["p_known_updated"] > 0.3
    assert data["diagnosis"] is None


def test_api_answer_happy_path_wrong_with_diagnosis(client):
    q_resp = client.get("/api/questions/g5-fractions-add?difficulty=easy&limit=1")
    q = q_resp.json()["questions"][0]
    
    wrong_idx = (q["correct_index"] + 1) % 4
    payload = {
        "topic_id": "g5-fractions-add",
        "question_id": q["id"],
        "chosen_index": wrong_idx,
        "attempt": 1,
        "state": {"combo": 4, "p_known": 0.5, "consecutive_correct": 2},
    }
    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["correct_index"] == q["correct_index"]
    assert data["xp_awarded"] == 0
    assert data["combo"] == 0
    assert data["p_known_updated"] < 0.5
    assert data["diagnosis"] is not None
    assert "kid_label" in data["diagnosis"]
    assert "diagnosis" in data["diagnosis"]


def test_api_infographic_happy_path(client):
    response = client.get("/api/infographic/g5-fractions-add")
    assert response.status_code == 200
    data = response.json()
    assert data["title"]
    assert "image_url" in data
    assert "pollinations.ai" in data["image_url"]
    assert "fallback_image" in data
    assert data["source"] == "offline"


def test_api_explainer_happy_path(client):
    response = client.get("/api/explainer/g5-fractions-add")
    assert response.status_code == 200
    data = response.json()
    assert "slides" in data
    assert len(data["slides"]) >= 1
    assert data["source"] == "offline"


def test_api_eval_happy_path(client):
    response = client.get("/api/eval")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "offline"


# ---------------------------------------------------------------------------
# 2. Unknown Topic 404 Tests
# ---------------------------------------------------------------------------

def test_api_unknown_topic_404(client):
    # Lesson 404
    r1 = client.get("/api/lesson/non-existent-topic")
    assert r1.status_code == 404
    assert r1.json()["error"]["code"] == "NOT_FOUND"

    # Questions 404
    r2 = client.get("/api/questions/non-existent-topic")
    assert r2.status_code == 404
    assert r2.json()["error"]["code"] == "NOT_FOUND"

    # Infographic 404
    r3 = client.get("/api/infographic/non-existent-topic")
    assert r3.status_code == 404
    assert r3.json()["error"]["code"] == "NOT_FOUND"

    # Explainer 404
    r4 = client.get("/api/explainer/non-existent-topic")
    assert r4.status_code == 404
    assert r4.json()["error"]["code"] == "NOT_FOUND"

    # Refresh 404
    r5 = client.post("/api/lesson/non-existent-topic/refresh")
    assert r5.status_code == 404
    assert r5.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# 3. Bad Payload 422 Tests
# ---------------------------------------------------------------------------

def test_api_bad_payload_422(client):
    # Empty payload
    r1 = client.post("/api/answer", json={})
    assert r1.status_code == 422
    assert r1.json()["error"]["code"] == "VALIDATION_ERROR"

    # Missing question_id
    r2 = client.post("/api/answer", json={"topic_id": "g5-fractions-add", "chosen_index": 1})
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "VALIDATION_ERROR"

    # Chosen index out of bounds
    r3 = client.post("/api/answer", json={
        "topic_id": "g5-fractions-add",
        "question_id": "g5-fractions-add-easy-1",
        "chosen_index": 99,
    })
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 4. Refresh Falls Back on Timeout, Bad JSON, or Wrong Math
# ---------------------------------------------------------------------------

def test_api_refresh_fallback_on_timeout(client):
    mock = MockClient(should_timeout=True)
    set_llm_client(mock)

    response = client.post("/api/lesson/g5-fractions-add/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "offline"
    assert data["reason_code"] == "TIMEOUT"
    assert data["title"]  # returns stored lesson


def test_api_refresh_fallback_on_bad_json(client):
    mock = MockClient(invalid_json=True)
    set_llm_client(mock)

    response = client.post("/api/lesson/g5-fractions-add/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "offline"
    assert data["reason_code"] == "INVALID_JSON"
    assert data["title"]


def test_api_refresh_fallback_on_wrong_math(client):
    # Valid schema structure, but mathematically invalid worked step: 1/2 + 1/3 = 5/7
    broken_math_lesson = {
        "title": "Adding Fractions",
        "big_idea": "Combine parts of wholes",
        "explanation": "Find common denominators.",
        "worked_example": [
            {"step": 1, "text": "Add fractions", "math": "1/2 + 1/3 = 5/7"}
        ],
        "key_vocab": ["denominator"],
        "real_world_example": "Sharing pies",
        "common_mistakes": ["Adding bottoms"]
    }
    mock = MockClient(default_response=broken_math_lesson)
    set_llm_client(mock)

    response = client.post("/api/lesson/g5-fractions-add/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "offline"
    assert data["reason_code"] == "WRONG_MATH"
    assert data["title"]


def test_api_refresh_success_with_valid_lesson(client):
    valid_lesson = {
        "title": "Adding Fractions",
        "big_idea": "Combine parts of wholes",
        "explanation": "Find common denominators.",
        "worked_example": [
            {"step": 1, "text": "Rewrite with common denominator", "math": "1/2 + 1/3 = 3/6 + 2/6"},
            {"step": 2, "text": "Add numerators", "math": "3/6 + 2/6 = 5/6"}
        ],
        "key_vocab": ["denominator", "numerator"],
        "real_world_example": "Sharing pies in a bakery",
        "common_mistakes": ["Adding denominators together"]
    }
    mock = MockClient(default_response=valid_lesson)
    set_llm_client(mock)

    response = client.post("/api/lesson/g5-volume/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "ai-live"
    assert data["title"] == "Adding Fractions"


# ---------------------------------------------------------------------------
# 5. /answer Overrides a Deliberately Corrupted Stored correct_index
# ---------------------------------------------------------------------------

def test_api_answer_overrides_corrupted_stored_correct_index(client, monkeypatch):
    """If question has a deliberately corrupted stored correct_index (e.g. set to 0),

    recomputation from `expression` dynamically recalculates the true option index.
    """
    bank_path = Path("data/bank/g5-fractions-add.json")
    with open(bank_path, "r", encoding="utf-8") as f:
        bank_data = json.load(f)

    original_q = bank_data["questions"][0]
    corrupted_q = dict(original_q)
    # The true correct option is at original_q["correct_index"] (e.g. 3)
    true_index = original_q["correct_index"]
    # Corrupt stored index to an intentional falsehood (e.g. index 0)
    corrupted_stored_index = 0 if true_index != 0 else 1
    corrupted_q["correct_index"] = corrupted_stored_index

    # Mock bank reading to return corrupted question
    corrupted_bank = {"topic_id": "g5-fractions-add", "questions": [corrupted_q]}
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: (
            monkeypatch.undo() or None
        ),  # We'll use monkeypatch on json.load instead
    )
    # Safer patch: patch the bank reading in api.index
    orig_open = open
    def mock_open(file, *args, **kwargs):
        if str(file).endswith("g5-fractions-add.json"):
            import io
            return io.StringIO(json.dumps(corrupted_bank))
        return orig_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    # Student chooses the mathematically TRUE answer
    payload = {
        "topic_id": "g5-fractions-add",
        "question_id": corrupted_q["id"],
        "chosen_index": true_index,
        "attempt": 1,
    }
    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    # The API MUST override corrupted_stored_index and correctly identify true_index
    assert data["correct_index"] == true_index
    assert data["correct"] is True
