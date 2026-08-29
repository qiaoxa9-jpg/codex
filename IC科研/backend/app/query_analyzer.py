import re

from .schemas import Classification, QuestionCategory


_RULES: list[tuple[QuestionCategory, tuple[str, ...]]] = [
    (
        QuestionCategory.CDC,
        (
            "cdc",
            "clock domain crossing",
            "metastability",
            "synchronizer",
            "跨时钟",
            "异步时钟",
            "亚稳态",
            "同步器",
            "async fifo",
        ),
    ),
    (QuestionCategory.RDC, ("rdc", "跨复位", "异步复位", "reset domain")),
    (QuestionCategory.STA, ("sta", "时序收敛", "setup", "hold", "slack", "时序约束")),
    (QuestionCategory.DFT, ("dft", "scan", "atpg", "mbist", "测试覆盖率")),
    (QuestionCategory.LOW_POWER, ("低功耗", "upf", "power gating", "clock gating", "isolation")),
    (QuestionCategory.PHYSICAL_DESIGN, ("布局布线", "floorplan", "placement", "route", "ir drop")),
    (QuestionCategory.SYNTHESIS, ("综合", "synthesis", "latch", "timing inference")),
    (QuestionCategory.VERIFICATION, ("uvm", "sva", "断言", "scoreboard", "coverage", "验证")),
    (QuestionCategory.RTL_QUESTION, ("rtl", "verilog", "systemverilog", "always_ff", "代码")),
    (QuestionCategory.ARCHITECTURE, ("架构", "soc", "noc", "cache", "pipeline")),
    (QuestionCategory.PAPER_SEARCH, ("找论文", "paper", "文献检索", "doi")),
    (QuestionCategory.RESEARCH_QUESTION, ("研究趋势", "state of the art", "research gap", "综述")),
]


class QueryAnalyzer:
    def analyze(self, question: str) -> Classification:
        normalized = re.sub(r"\s+", " ", question.lower()).strip()
        for category, keywords in _RULES:
            hits = [term for term in keywords if term in normalized]
            if hits:
                confidence = min(0.98, 0.72 + 0.08 * len(hits))
                return Classification(category=category, confidence=confidence, signals=hits)
        if any(token in normalized for token in ("是什么", "定义", "区别", "原理")):
            return Classification(category=QuestionCategory.TERM, confidence=0.72, signals=["definition-intent"])
        return Classification(
            category=QuestionCategory.ENGINEERING_PROBLEM,
            confidence=0.56,
            signals=["fallback-engineering-intent"],
        )

    def expand(self, question: str, category: QuestionCategory) -> list[str]:
        expansions = [question]
        domain_terms = {
            QuestionCategory.CDC: "clock domain crossing metastability synchronizer MTBF",
            QuestionCategory.RDC: "reset domain crossing reset synchronizer recovery removal",
            QuestionCategory.STA: "static timing analysis setup hold constraints",
            QuestionCategory.VERIFICATION: "SystemVerilog UVM assertion coverage",
            QuestionCategory.SYNTHESIS: "RTL synthesis inference optimization",
            QuestionCategory.LOW_POWER: "UPF clock gating power gating isolation",
            QuestionCategory.DFT: "scan ATPG MBIST test coverage",
            QuestionCategory.PHYSICAL_DESIGN: "place route timing closure physical design",
        }
        if category in domain_terms:
            expansions.append(domain_terms[category])
        return expansions
