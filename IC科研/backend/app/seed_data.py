from .schemas import ConceptSummary, Evidence, EvidenceLevel


EVIDENCE_CATALOG: list[Evidence] = [
    Evidence(
        source_id="IND-AMD-UG949-CDC-2026",
        title="UltraFast Design Methodology Guide: Clock Domain Crossing",
        source="AMD",
        document_type="Design Methodology",
        url="https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Clock-Domain-Crossing",
        year=2026,
        excerpt=(
            "CDC circuits directly affect design reliability. AMD recommends recognized CDC "
            "structures or XPMs, correct ASYNC_REG attributes, structural CDC checks, and MTBF review."
        ),
        domains=["CDC", "STA", "SYNTHESIS", "VERIFICATION"],
        authority_score=0.98,
        engineering_applicability=0.98,
        evidence_level=EvidenceLevel.INDUSTRY_ESTABLISHED,
    ),
    Evidence(
        source_id="IND-INTEL-TA-METASTABILITY-2024",
        title="Quartus Prime Timing Analyzer: Metastability Analysis",
        source="Intel",
        document_type="User Guide",
        url="https://www.intel.com/content/www/us/en/docs/programmable/683068/18-1/metastability-analysis.html",
        year=2024,
        excerpt=(
            "Asynchronous transfers can violate setup and hold requirements. A destination-domain "
            "synchronization register chain reduces risk, and Timing Analyzer can estimate MTBF."
        ),
        domains=["CDC", "STA", "PHYSICAL_DESIGN"],
        authority_score=0.98,
        engineering_applicability=0.96,
        evidence_level=EvidenceLevel.INDUSTRY_ESTABLISHED,
    ),
    Evidence(
        source_id="IND-SIEMENS-QUESTA-CDCFX",
        title="Questa CDC-FX: Metastability Effects Delay Modeling",
        source="Siemens EDA",
        document_type="White Paper",
        url="https://resources.sw.siemens.com/cs-CZ/white-paper-questa-cdc-fx-metastability-effects-delay-modeling/",
        excerpt=(
            "A complete CDC verification flow combines structural analysis with metastability-effects "
            "modeling to check whether functional behavior remains resilient."
        ),
        domains=["CDC", "VERIFICATION"],
        authority_score=0.92,
        engineering_applicability=0.94,
        evidence_level=EvidenceLevel.INDUSTRY_ESTABLISHED,
    ),
    Evidence(
        source_id="IND-AMD-UG949-SYNC-CDC-2026",
        title="UltraFast Design Methodology Guide: Synchronous CDC",
        source="AMD",
        document_type="Design Methodology",
        url="https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Synchronous-CDC",
        year=2026,
        excerpt=(
            "Clock crossings originating from different MMCMs or PLLs are harder to control and "
            "should be treated as asynchronous crossings."
        ),
        domains=["CDC", "STA", "ARCHITECTURE"],
        authority_score=0.98,
        engineering_applicability=0.92,
        evidence_level=EvidenceLevel.INDUSTRY_ESTABLISHED,
    ),
]


CONCEPTS: list[ConceptSummary] = [
    ConceptSummary(
        id="metastability",
        name="Metastability",
        chinese_name="亚稳态",
        definition="触发器在建立/保持时间不满足时，输出暂时无法在规定时间内稳定到确定逻辑值的状态。",
        definition_en="A temporary state in which a flip-flop output cannot settle to a defined logic value within the required time after setup or hold is violated.",
        category="CDC",
        related=["setup-hold", "synchronizer", "mtbf", "cdc"],
    ),
    ConceptSummary(
        id="synchronizer",
        name="Synchronizer",
        chinese_name="同步器",
        definition="在目标时钟域中为异步输入提供解析时间、降低亚稳态传播概率的寄存器结构。",
        definition_en="A register structure in the destination clock domain that gives an asynchronous input time to resolve and reduces the probability of metastability propagation.",
        category="CDC",
        related=["metastability", "2ff-synchronizer", "mtbf"],
    ),
    ConceptSummary(
        id="cdc",
        name="Clock Domain Crossing",
        abbreviation="CDC",
        chinese_name="跨时钟域",
        definition="信号在具有不同或无法证明固定相位关系的时钟域之间传输。",
        definition_en="The transfer of a signal between clock domains that differ in frequency or lack a provable fixed phase relationship.",
        category="CDC",
        related=["synchronizer", "async-fifo", "handshake", "reconvergence"],
    ),
    ConceptSummary(
        id="static-timing-analysis",
        name="Static Timing Analysis",
        abbreviation="STA",
        chinese_name="静态时序分析",
        definition="不依赖输入向量，基于时序图与约束检查所有相关路径时序裕量的方法。",
        definition_en="A vectorless method that checks timing margin across relevant paths using a timing graph and design constraints.",
        category="STA",
        related=["setup-hold", "timing-exception", "clock-uncertainty"],
    ),
    ConceptSummary(
        id="systemverilog-assertion",
        name="SystemVerilog Assertion",
        abbreviation="SVA",
        chinese_name="SystemVerilog 断言",
        definition="用时序属性描述并自动检查设计行为约束的 SystemVerilog 子语言。",
        definition_en="A SystemVerilog sublanguage for expressing temporal properties and automatically checking behavioral constraints.",
        category="VERIFICATION",
        related=["formal-verification", "coverage", "protocol-checker"],
    ),
    ConceptSummary(
        id="clock-gating",
        name="Clock Gating",
        chinese_name="时钟门控",
        definition="在功能空闲时阻断局部时钟翻转，以降低动态功耗的低功耗设计技术。",
        definition_en="A low-power technique that suppresses local clock switching while logic is idle to reduce dynamic power.",
        category="LOW_POWER",
        related=["integrated-clock-gating", "clock-enable", "power-intent"],
    ),
]
