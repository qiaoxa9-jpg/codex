import json

import httpx

from .citation_validator import CitationValidationError, validate_and_build_citations
from .config import Settings
from .schemas import (
    AnswerMode,
    AnswerSection,
    Classification,
    Evidence,
    QuestionCategory,
    UILanguage,
)


INSUFFICIENT_EVIDENCE = {
    UILanguage.ZH: "当前知识库中没有足够可靠证据支持这一结论。",
    UILanguage.EN: "The current knowledge base does not contain enough reliable evidence to support this conclusion.",
}


class AnswerGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(
        self,
        question: str,
        mode: AnswerMode,
        classification: Classification,
        evidences: list[Evidence],
        language: UILanguage = UILanguage.ZH,
    ) -> tuple[list[AnswerSection], str, list[str]]:
        if not evidences or max((item.relevance for item in evidences), default=0) < 0.18:
            return (
                [
                    AnswerSection(
                        key="evidence_gap",
                        title="证据不足" if language == UILanguage.ZH else "Insufficient evidence",
                        content=INSUFFICIENT_EVIDENCE[language],
                    )
                ],
                "insufficient_evidence",
                [
                    "没有满足相关性阈值的证据，系统未尝试补全结论。"
                    if language == UILanguage.ZH
                    else "No evidence met the relevance threshold; the system did not complete the conclusion from memory."
                ],
            )

        if self.settings.llm_api_key:
            try:
                sections = await self._generate_with_llm(
                    question, mode, classification, evidences, language
                )
                validate_and_build_citations(sections, evidences)
                return sections, "grounded", []
            except (httpx.HTTPError, ValueError, KeyError, CitationValidationError) as exc:
                warnings = [
                    f"LLM 输出未通过验证，已使用确定性安全答案：{type(exc).__name__}"
                    if language == UILanguage.ZH
                    else f"LLM output failed validation; a deterministic safe answer was used: {type(exc).__name__}"
                ]
            else:
                warnings = []
        else:
            warnings = [
                "未配置 LLM_API_KEY，当前显示可审计的本地证据模板答案。"
                if language == UILanguage.ZH
                else "LLM_API_KEY is not configured; an auditable local evidence template is shown."
            ]

        if classification.category == QuestionCategory.CDC:
            return self._cdc_answer(evidences, language), "grounded", warnings
        return (
            [
                AnswerSection(
                    key="evidence_summary",
                    title="证据结论" if language == UILanguage.ZH else "Evidence conclusion",
                    content=(
                        (
                            "检索到了相关证据，但本地模板尚未覆盖此问题类型。为避免越过证据边界，"
                            "系统不生成具体工程结论。"
                        )
                        if language == UILanguage.ZH
                        else (
                            "Relevant evidence was retrieved, but the local template does not yet cover this question type. "
                            "The system will not generate a specific engineering conclusion beyond the evidence boundary. "
                        )
                    )
                    + INSUFFICIENT_EVIDENCE[language],
                    source_ids=[evidences[0].source_id],
                )
            ],
            "partial_evidence",
            warnings,
        )

    async def _generate_with_llm(
        self,
        question: str,
        mode: AnswerMode,
        classification: Classification,
        evidences: list[Evidence],
        language: UILanguage,
    ) -> list[AnswerSection]:
        context = [
            {
                "source_id": item.source_id,
                "title": item.title,
                "excerpt": item.excerpt,
                "url": str(item.url),
            }
            for item in evidences
        ]
        system = (
            "You are an evidence-bounded Digital IC engineering assistant. Return JSON only with "
            "a top-level sections array. Each section has key, title, content, source_ids and optional "
            "code. source_ids must be selected verbatim from Evidence Context. Never invent a paper, "
            "DOI, author, EDA command, standard, URL, or source_id. If evidence is insufficient, say "
            f"'{INSUFFICIENT_EVIDENCE[language]}'. Write the answer in "
            f"{'Simplified Chinese' if language == UILanguage.ZH else 'English'}."
        )
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": question,
                            "mode": mode.value,
                            "category": classification.category.value,
                            "output_language": language.value,
                            "evidence_context": context,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                json=payload,
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return [AnswerSection.model_validate(section) for section in parsed["sections"]]

    def _cdc_answer(
        self, evidences: list[Evidence], language: UILanguage
    ) -> list[AnswerSection]:
        ids = {item.source_id for item in evidences}

        def sources(*candidates: str) -> list[str]:
            return [candidate for candidate in candidates if candidate in ids]

        if language == UILanguage.EN:
            return self._cdc_answer_en(evidences)

        return [
            AnswerSection(
                key="problem_understanding",
                title="问题理解",
                content=(
                    "这是一个跨时钟域可靠性问题。先区分信号是单比特电平、脉冲、多比特数据总线，"
                    "还是带控制/数据一致性要求的事务；结构选择取决于这一条件。"
                ),
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
            AnswerSection(
                key="root_cause",
                title="可能 Root Cause",
                content=(
                    "异步采样可能破坏目标触发器的 setup/hold 条件并产生亚稳态。若源端组合逻辑"
                    "存在毛刺、跨域总线逐位同步、同步后信号重新汇聚，风险会进一步扩大。"
                ),
                source_ids=sources(
                    "IND-INTEL-TA-METASTABILITY-2024", "IND-AMD-UG949-CDC-2026"
                ),
            ),
            AnswerSection(
                key="solution",
                title="推荐解决方案",
                content=(
                    "仅针对单比特、变化速度足够慢的电平信号：先在源端寄存以消除组合毛刺，"
                    "再在目标域使用至少两级同步寄存器。脉冲需脉冲展宽、toggle 或握手；"
                    "多比特连续数据使用异步 FIFO，配置/状态总线使用握手或保持稳定协议。"
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-INTEL-TA-METASTABILITY-2024"
                ),
            ),
            AnswerSection(
                key="tradeoffs",
                title="方案权衡",
                content=(
                    "2FF 成本低但增加约两拍延迟，且不保证窄脉冲被捕获，也不能保证多比特相干性。"
                    "握手可保证事务但吞吐受往返延迟限制；异步 FIFO 吞吐高，但需要 Gray 指针、"
                    "满空判断、复位与形式/动态验证。"
                ),
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
            AnswerSection(
                key="rtl",
                title="RTL / Circuit Example",
                content="下面的结构仅适用于单比特电平信号；不要直接用于多比特总线或窄脉冲。",
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-INTEL-TA-METASTABILITY-2024"
                ),
                code="""module cdc_bit_sync (
  input  logic clk_dst,
  input  logic rst_n,
  input  logic async_level,
  output logic sync_level
);
  (* ASYNC_REG = \"TRUE\" *) logic sync_ff1, sync_ff2;

  always_ff @(posedge clk_dst or negedge rst_n) begin
    if (!rst_n) begin
      sync_ff1 <= 1'b0;
      sync_ff2 <= 1'b0;
    end else begin
      sync_ff1 <= async_level;
      sync_ff2 <= sync_ff1;
    end
  end
  assign sync_level = sync_ff2;
endmodule""",
            ),
            AnswerSection(
                key="verification",
                title="Verification Method",
                content=(
                    "执行结构化 CDC 分析，检查缺失同步器、组合逻辑进入首级、跨域重汇聚和错误时序例外；"
                    "用独立异步时钟与随机相位动态仿真检查协议级数据完整性；对关键结构增加 SVA/形式检查；"
                    "最后复核实现后的同步链识别与 MTBF，而不是只看 RTL 仿真。"
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026",
                    "IND-INTEL-TA-METASTABILITY-2024",
                    "IND-SIEMENS-QUESTA-CDCFX",
                ),
            ),
            AnswerSection(
                key="eda_flow",
                title="推荐 EDA Flow",
                content=(
                    "lint/RTL review → static CDC → asynchronous-clock simulation → assertion/formal protocol checks "
                    "→ synthesis/implementation → post-implementation CDC and MTBF review。Vivado 场景可用"
                    "已被官方文档列出的 report_cdc 与 report_synchronizer_mtbf；其他工具使用各自已安装版本文档"
                    "中的等价流程，不猜测命令。"
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026",
                    "IND-INTEL-TA-METASTABILITY-2024",
                    "IND-SIEMENS-QUESTA-CDCFX",
                ),
            ),
            AnswerSection(
                key="best_practice",
                title="Industry Best Practice",
                content=(
                    "将 CDC 作为独立签核项；同步链加可识别属性并保持紧邻放置；同步器首级输出只进入下一同步级；"
                    "每个 waiver 记录结构、理由、适用模式与复核人；不同 PLL/MMCM 来源在不能证明固定关系时按异步处理。"
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-AMD-UG949-SYNC-CDC-2026"
                ),
            ),
            AnswerSection(
                key="related",
                title="Related Concepts",
                content="metastability、MTBF、setup/hold、pulse synchronizer、handshake、Gray code、asynchronous FIFO、CDC reconvergence。",
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
        ]

    def _cdc_answer_en(self, evidences: list[Evidence]) -> list[AnswerSection]:
        ids = {item.source_id for item in evidences}

        def sources(*candidates: str) -> list[str]:
            return [candidate for candidate in candidates if candidate in ids]

        return [
            AnswerSection(
                key="problem_understanding",
                title="Problem understanding",
                content=(
                    "This is a clock-domain-crossing reliability problem. First distinguish a "
                    "single-bit level, a pulse, a multi-bit data bus, or a transaction with control/data "
                    "coherency requirements; the correct structure depends on that condition."
                ),
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
            AnswerSection(
                key="root_cause",
                title="Possible root causes",
                content=(
                    "Asynchronous sampling can violate the destination flip-flop's setup/hold requirements "
                    "and produce metastability. Source-side combinational glitches, bitwise synchronization "
                    "of a bus, and reconvergence after synchronization can increase the risk."
                ),
                source_ids=sources(
                    "IND-INTEL-TA-METASTABILITY-2024", "IND-AMD-UG949-CDC-2026"
                ),
            ),
            AnswerSection(
                key="solution",
                title="Recommended solution",
                content=(
                    "For a single-bit level that changes slowly enough, register it in the source domain to "
                    "remove combinational glitches, then use at least a two-stage synchronizer in the destination "
                    "domain. Use pulse stretching, a toggle, or a handshake for pulses; use an asynchronous FIFO "
                    "for streaming multi-bit data and a handshake or stability protocol for configuration/status buses."
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-INTEL-TA-METASTABILITY-2024"
                ),
            ),
            AnswerSection(
                key="tradeoffs",
                title="Trade-offs",
                content=(
                    "A 2FF synchronizer is inexpensive but adds roughly two destination cycles of latency; it "
                    "does not guarantee capture of a narrow pulse or coherency of a multi-bit bus. A handshake "
                    "preserves transactions at round-trip latency cost. An asynchronous FIFO sustains throughput "
                    "but requires Gray pointers, full/empty logic, reset handling, and formal or dynamic verification."
                ),
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
            AnswerSection(
                key="rtl",
                title="RTL / circuit example",
                content=(
                    "The structure below applies only to a single-bit level. Do not use it directly for a "
                    "multi-bit bus or a narrow pulse."
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-INTEL-TA-METASTABILITY-2024"
                ),
                code="""module cdc_bit_sync (
  input  logic clk_dst,
  input  logic rst_n,
  input  logic async_level,
  output logic sync_level
);
  (* ASYNC_REG = \"TRUE\" *) logic sync_ff1, sync_ff2;

  always_ff @(posedge clk_dst or negedge rst_n) begin
    if (!rst_n) begin
      sync_ff1 <= 1'b0;
      sync_ff2 <= 1'b0;
    end else begin
      sync_ff1 <= async_level;
      sync_ff2 <= sync_ff1;
    end
  end
  assign sync_level = sync_ff2;
endmodule""",
            ),
            AnswerSection(
                key="verification",
                title="Verification method",
                content=(
                    "Run structural CDC analysis for missing synchronizers, combinational logic before the first "
                    "stage, reconvergence, and incorrect timing exceptions. Simulate independent asynchronous clocks "
                    "with randomized phase for protocol-level integrity, add SVA or formal checks for critical "
                    "structures, and review post-implementation synchronizer recognition and MTBF rather than relying on RTL simulation alone."
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026",
                    "IND-INTEL-TA-METASTABILITY-2024",
                    "IND-SIEMENS-QUESTA-CDCFX",
                ),
            ),
            AnswerSection(
                key="eda_flow",
                title="Recommended EDA flow",
                content=(
                    "lint/RTL review → static CDC → asynchronous-clock simulation → assertion/formal protocol checks "
                    "→ synthesis/implementation → post-implementation CDC and MTBF review. In Vivado, the official "
                    "documentation identifies report_cdc and report_synchronizer_mtbf. For other tools, use the "
                    "equivalent flow documented for the installed release instead of guessing command names."
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026",
                    "IND-INTEL-TA-METASTABILITY-2024",
                    "IND-SIEMENS-QUESTA-CDCFX",
                ),
            ),
            AnswerSection(
                key="best_practice",
                title="Industry best practice",
                content=(
                    "Treat CDC as an independent signoff item; apply recognizable attributes and keep synchronizer "
                    "stages physically close; allow the first stage to fan out only to the next synchronizer stage; "
                    "record topology, rationale, applicable modes, and reviewer for every waiver; treat different "
                    "PLL/MMCM sources as asynchronous when a fixed relationship cannot be proven."
                ),
                source_ids=sources(
                    "IND-AMD-UG949-CDC-2026", "IND-AMD-UG949-SYNC-CDC-2026"
                ),
            ),
            AnswerSection(
                key="related",
                title="Related concepts",
                content=(
                    "metastability, MTBF, setup/hold, pulse synchronizer, handshake, Gray code, "
                    "asynchronous FIFO, and CDC reconvergence."
                ),
                source_ids=sources("IND-AMD-UG949-CDC-2026"),
            ),
        ]
