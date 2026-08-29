from app.query_analyzer import QueryAnalyzer
from app.retriever import HybridRetriever
from app.schemas import QuestionCategory


def test_classifies_core_digital_ic_domains() -> None:
    analyzer = QueryAnalyzer()
    cases = {
        "单比特异步信号如何跨时钟域？": QuestionCategory.CDC,
        "clock domain crossing verification flow": QuestionCategory.CDC,
        "setup violation 如何修复？": QuestionCategory.STA,
        "UVM scoreboard 应如何设计？": QuestionCategory.VERIFICATION,
        "UPF isolation 如何验证？": QuestionCategory.LOW_POWER,
        "ATPG coverage 低怎么办？": QuestionCategory.DFT,
    }
    for question, expected in cases.items():
        assert analyzer.analyze(question).category == expected


def test_hybrid_retrieval_returns_grounded_cdc_sources() -> None:
    retriever = HybridRetriever()
    results = retriever.retrieve(
        ["单比特异步 CDC 亚稳态", "clock domain crossing synchronizer MTBF"],
        QuestionCategory.CDC,
        limit=4,
    )
    assert results
    assert all(result.source_id.startswith("IND-") for result in results)
    assert results == sorted(results, key=lambda result: result.score, reverse=True)
    assert all(0 <= result.score <= 1 for result in results)


def test_unrelated_domain_does_not_receive_a_confident_answer() -> None:
    retriever = HybridRetriever()
    results = retriever.retrieve(
        ["scan compression ATPG diagnosis"], QuestionCategory.DFT, limit=4
    )
    assert not results
