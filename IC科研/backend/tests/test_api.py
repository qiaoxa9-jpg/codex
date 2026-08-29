from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_engineering_answer_is_grounded_and_citations_resolve() -> None:
    response = client.post(
        "/api/v1/research/ask",
        json={
            "question": "单比特异步信号如何安全跨时钟域？",
            "mode": "engineering",
            "max_evidence": 6,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["classification"]["category"] == "CDC"
    assert body["answer_status"] == "grounded"
    evidence_ids = {item["source_id"] for item in body["evidences"]}
    assert evidence_ids
    assert all(citation["source_id"] in evidence_ids for citation in body["citations"])


def test_uncovered_domain_returns_insufficient_evidence() -> None:
    response = client.post(
        "/api/v1/research/ask",
        json={"question": "ATPG compression 的 aliasing 如何量化？", "mode": "engineering"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer_status"] == "insufficient_evidence"
    assert "没有足够可靠证据" in body["sections"][0]["content"]


def test_english_language_returns_english_answer_sections() -> None:
    response = client.post(
        "/api/v1/research/ask",
        json={
            "question": "How should a single-bit clock domain crossing be handled?",
            "mode": "engineering",
            "language": "en",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["classification"]["category"] == "CDC"
    assert body["sections"][0]["title"] == "Problem understanding"
    assert "clock-domain-crossing reliability" in body["sections"][0]["content"]


def test_concepts_endpoint() -> None:
    response = client.get("/api/v1/concepts?q=metastability")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "metastability"
