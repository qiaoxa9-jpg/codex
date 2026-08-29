import json
from collections import Counter
from pathlib import Path


def test_evaluation_dataset_has_100_balanced_questions() -> None:
    path = Path(__file__).parent / "evaluation" / "ic_questions.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    assert len(records) >= 100
    counts = Counter(record["category"] for record in records)
    assert counts == {
        "RTL": 10,
        "CDC": 10,
        "RDC": 10,
        "STA": 10,
        "SYNTHESIS": 10,
        "VERIFICATION": 10,
        "LOW_POWER": 10,
        "DFT": 10,
        "PHYSICAL_DESIGN": 10,
        "ARCHITECTURE": 10,
    }
    required = {
        "question",
        "category",
        "expected_key_points",
        "forbidden_errors",
        "recommended_sources",
    }
    assert all(required <= record.keys() for record in records)

