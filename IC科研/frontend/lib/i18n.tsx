"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

export type Language = "zh" | "en";

const zh = {
  "header.research": "研究",
  "header.papers": "论文",
  "header.encyclopedia": "百科",
  "header.traceable": "可追溯",
  "header.theme": "切换深浅色",
  "header.language": "切换语言",
  "home.badge": "数字 IC · ASIC · SoC · 验证",
  "home.titlePrimary": "研究深度。",
  "home.titleSecondary": "工程证据。",
  "home.description": "面向微电子研究生与数字 IC 工程师的专业知识引擎。不是聊天框，而是一套可检查检索过程、证据等级、适用条件与引用边界的研究工作台。",
  "home.start": "开始工程研究",
  "home.searchPapers": "检索真实论文",
  "home.trace": "实时推理轨迹",
  "home.sample": "单比特异步 CDC",
  "home.grounded": "证据充分",
  "home.classify": "分类",
  "home.classifyValue": "CDC · 96%",
  "home.retrieve": "检索",
  "home.retrieveValue": "BM25 + 向量 + 工业资料",
  "home.rerank": "重排",
  "home.rerankValue": "权威性 ≠ 新近性",
  "home.validate": "校验",
  "home.validateValue": "3 个 source_id 已接受",
  "home.recommendation": "建议",
  "home.recommendationValue": "仅当信号为单比特电平时使用 2FF",
  "home.evidence": "证据",
  "metric.questionClasses": "问题类别",
  "metric.evidenceSignals": "证据信号",
  "metric.answerModes": "回答模式",
  "metric.unboundCitations": "越界引用",
  "home.architecture": "系统架构",
  "home.designedForProof": "为可验证结论而设计",
  "home.accuracy": "准确性 > 外观。每个主要建议都保留来源、等级、打分与适用边界。",
  "home.engineeringDiagnosis": "工程诊断",
  "home.engineeringCopy": "从症状追到根因，再把适用条件、RTL、验证方法和工程权衡放在同一条证据链上。",
  "home.literatureIntelligence": "文献智能",
  "home.literatureCopy": "联合 Semantic Scholar 与 Crossref 检索真实论文元数据；来源不可用时显式降级。",
  "home.citationFirewall": "引用防火墙",
  "home.citationCopy": "生成器只能引用 Evidence Context 中已存在的 source_id，越界引用会被验证器拒绝。",
  "home.knowledgeModel": "知识模型",
  "home.conceptsSystem": "让概念形成系统",
  "home.conceptsCopy": "prerequisite、causes、solved_by、used_in 与 part_of 把定义转成可导航的工程关系。",
  "home.enterEncyclopedia": "进入 IC 百科",
  "home.structuredAnswers": "结构化回答",
  "home.rtlEvidence": "RTL 与证据处在同一视图",
  "home.rtlCopy": "代码示例不会脱离适用条件；验证方法、EDA flow 与 trade-off 均可独立引用。",
  "home.evidenceFirst": "证据优先，生成在后。",
  "research.placeholder": "输入 Digital IC / ASIC / SoC 工程或研究问题…",
  "research.modeEngineering": "工程",
  "research.modeResearch": "研究",
  "research.modeLearning": "学习",
  "research.analyze": "分析",
  "research.backendError": "后端尚未连接",
  "research.queryAnalyzer": "问题分析器",
  "research.signals": "识别信号",
  "research.channels": "检索通道",
  "research.firewall": "引用防火墙",
  "research.idsPassed": "个 source_id 已通过上下文校验",
  "research.output": "综合输出",
  "research.answer": "证据约束回答",
  "research.question": "问题",
  "research.building": "正在构建证据链",
  "research.classifyFirst": "先分类，再回答",
  "research.emptyHelp": "系统会展示问题分类、检索通道、证据分数和引用验证结果。按 Ctrl/⌘ + Enter 也可运行。",
  "research.evidenceContext": "证据上下文",
  "research.sources": "来源",
  "research.selected": "已选择",
  "research.emptyEvidence": "运行问题后，这里会显示可点击的 Evidence Card。来源不会在生成阶段凭空增加。",
  "research.score": "分",
  "research.openSource": "打开来源",
  "research.codeCondition": "systemverilog · 有条件适用的示例",
  "research.example1": "单比特异步信号如何安全跨时钟域？",
  "research.example2": "异步复位释放为什么会导致 RDC 风险？",
  "research.example3": "STA 中 hold violation 应该如何定位？",
  "papers.eyebrow": "论文智能",
  "papers.titleA": "检索元数据。",
  "papers.titleB": "保留来源链。",
  "papers.description": "联合检索 Semantic Scholar 与 Crossref。结果只展示上游返回的论文、DOI、作者和链接；某个提供方失败时不会用虚构结果补位。",
  "papers.placeholder": "CDC 验证、低功耗、时序收敛…",
  "papers.search": "检索",
  "papers.error": "论文检索服务不可用",
  "papers.openAccess": "开放获取",
  "papers.authorUnavailable": "作者元数据不可用",
  "papers.venueUnavailable": "Venue 不可用",
  "papers.citedBy": "被引",
  "papers.detail": "详情",
  "papers.openOriginal": "打开原始来源",
  "papers.emptyTitle": "检索真实论文元数据",
  "papers.emptyCopy": "输入关键词并运行搜索；外部 API 需要网络连接。",
  "paper.back": "返回论文检索",
  "paper.notFound": "无法从所选提供方获取论文详情",
  "paper.authorUnavailable": "作者元数据不可用",
  "paper.abstract": "提供方返回的摘要",
  "paper.abstractUnavailable": "上游元数据未提供摘要。系统不会根据标题补写摘要。",
  "paper.metadata": "元数据",
  "paper.year": "年份",
  "paper.venue": "Venue",
  "paper.citations": "引用数",
  "paper.openOriginal": "打开原始来源",
  "concept.eyebrow": "IC 百科",
  "concept.title": "让概念形成系统。",
  "concept.description": "从术语定义进入 prerequisite、causes、solved_by 与 used_in。MVP 先提供可检索概念与关系入口。",
  "concept.placeholder": "搜索 CDC、STA、亚稳态…",
  "concept.backendError": "后端尚未连接",
  "concept.index": "概念索引",
  "concept.definition": "定义",
  "concept.related": "相关概念",
  "concept.none": "没有匹配的概念。",
} as const;

export type TranslationKey = keyof typeof zh;

const en = {
  "header.research": "Research",
  "header.papers": "Papers",
  "header.encyclopedia": "Encyclopedia",
  "header.traceable": "TRACEABLE",
  "header.theme": "Toggle color theme",
  "header.language": "Switch language",
  "home.badge": "DIGITAL IC · ASIC · SOC · VERIFICATION",
  "home.titlePrimary": "Research depth.",
  "home.titleSecondary": "Engineering proof.",
  "home.description": "A professional knowledge engine for microelectronics researchers and Digital IC engineers—not a chat box, but a research workbench with inspectable retrieval, evidence levels, applicability conditions, and citation boundaries.",
  "home.start": "Start engineering research",
  "home.searchPapers": "Search verified papers",
  "home.trace": "Live reasoning trace",
  "home.sample": "Single-bit asynchronous CDC",
  "home.grounded": "GROUNDED",
  "home.classify": "CLASSIFY",
  "home.classifyValue": "CDC · 96%",
  "home.retrieve": "RETRIEVE",
  "home.retrieveValue": "BM25 + vector + industry",
  "home.rerank": "RERANK",
  "home.rerankValue": "Authority ≠ recency",
  "home.validate": "VALIDATE",
  "home.validateValue": "3 source_ids accepted",
  "home.recommendation": "recommendation",
  "home.recommendationValue": "use 2FF only for a single-bit level",
  "home.evidence": "evidence",
  "metric.questionClasses": "Question classes",
  "metric.evidenceSignals": "Evidence signals",
  "metric.answerModes": "Answer modes",
  "metric.unboundCitations": "Unbound citations",
  "home.architecture": "System architecture",
  "home.designedForProof": "Designed for defensible conclusions",
  "home.accuracy": "Accuracy > appearance. Every major recommendation preserves its source, level, score, and applicability boundary.",
  "home.engineeringDiagnosis": "Engineering diagnosis",
  "home.engineeringCopy": "Trace symptoms to root cause, then keep conditions, RTL, verification, and trade-offs on one evidence chain.",
  "home.literatureIntelligence": "Literature intelligence",
  "home.literatureCopy": "Search real metadata across Semantic Scholar and Crossref, with explicit degradation when a provider is unavailable.",
  "home.citationFirewall": "Citation firewall",
  "home.citationCopy": "The generator may cite only source_ids present in Evidence Context; out-of-context citations are rejected.",
  "home.knowledgeModel": "Knowledge model",
  "home.conceptsSystem": "Concepts become systems",
  "home.conceptsCopy": "prerequisite, causes, solved_by, used_in, and part_of turn definitions into navigable engineering relationships.",
  "home.enterEncyclopedia": "Open IC Encyclopedia",
  "home.structuredAnswers": "Structured answers",
  "home.rtlEvidence": "RTL and evidence share one view",
  "home.rtlCopy": "Code examples remain bound to applicability conditions; verification, EDA flow, and trade-offs stay independently citable.",
  "home.evidenceFirst": "Evidence first, generation second.",
  "research.placeholder": "Ask a Digital IC / ASIC / SoC engineering or research question…",
  "research.modeEngineering": "Engineering",
  "research.modeResearch": "Research",
  "research.modeLearning": "Learning",
  "research.analyze": "Analyze",
  "research.backendError": "Backend is not connected",
  "research.queryAnalyzer": "Query analyzer",
  "research.signals": "Signals",
  "research.channels": "Retrieval channels",
  "research.firewall": "Citation firewall",
  "research.idsPassed": "source_ids passed context validation",
  "research.output": "Synthesis output",
  "research.answer": "Evidence-grounded answer",
  "research.question": "Question",
  "research.building": "Building the evidence chain",
  "research.classifyFirst": "Classify first, then answer",
  "research.emptyHelp": "The system exposes classification, retrieval channels, evidence scores, and citation validation. Press Ctrl/⌘ + Enter to run.",
  "research.evidenceContext": "Evidence context",
  "research.sources": "Sources",
  "research.selected": "SELECTED",
  "research.emptyEvidence": "Run a question to inspect clickable Evidence Cards. Sources cannot be added during generation.",
  "research.score": "SCORE",
  "research.openSource": "Open source",
  "research.codeCondition": "systemverilog · conditional example",
  "research.example1": "How should a single-bit asynchronous signal cross clock domains safely?",
  "research.example2": "Why can asynchronous reset deassertion create RDC risk?",
  "research.example3": "How should a hold violation be diagnosed in STA?",
  "papers.eyebrow": "Paper intelligence",
  "papers.titleA": "Search metadata.",
  "papers.titleB": "Keep provenance.",
  "papers.description": "Search Semantic Scholar and Crossref together. Results show only papers, DOIs, authors, and links returned upstream; failed providers are never replaced with invented records.",
  "papers.placeholder": "CDC verification, low power, timing closure…",
  "papers.search": "Search",
  "papers.error": "Paper search service is unavailable",
  "papers.openAccess": "Open access",
  "papers.authorUnavailable": "Author metadata unavailable",
  "papers.venueUnavailable": "Venue unavailable",
  "papers.citedBy": "Cited by",
  "papers.detail": "Detail",
  "papers.openOriginal": "Open original source",
  "papers.emptyTitle": "Search verified paper metadata",
  "papers.emptyCopy": "Enter keywords and run a search. External APIs require network access.",
  "paper.back": "Back to paper search",
  "paper.notFound": "Could not retrieve paper details from the selected provider",
  "paper.authorUnavailable": "Author metadata unavailable",
  "paper.abstract": "Abstract from provider",
  "paper.abstractUnavailable": "The upstream metadata contains no abstract. The system will not invent one from the title.",
  "paper.metadata": "Metadata",
  "paper.year": "Year",
  "paper.venue": "Venue",
  "paper.citations": "Citations",
  "paper.openOriginal": "Open original source",
  "concept.eyebrow": "IC Encyclopedia",
  "concept.title": "Concepts become systems.",
  "concept.description": "Move from definitions into prerequisite, causes, solved_by, and used_in relationships. The MVP starts with searchable concepts and relation entry points.",
  "concept.placeholder": "Search CDC, STA, metastability…",
  "concept.backendError": "Backend is not connected",
  "concept.index": "Concept index",
  "concept.definition": "Definition",
  "concept.related": "Related concepts",
  "concept.none": "No matching concepts.",
} satisfies Record<TranslationKey, string>;

const dictionaries = { zh, en };

type LanguageContextValue = {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: TranslationKey) => string;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("zh");

  useEffect(() => {
    const stored = window.localStorage.getItem("ic-language");
    const queryLanguage = new URL(window.location.href).searchParams.get("lang");
    const initial: Language = queryLanguage === "en" || (queryLanguage !== "zh" && stored === "en") ? "en" : "zh";
    setLanguageState(initial);
    document.documentElement.lang = initial === "zh" ? "zh-CN" : "en";
  }, []);

  function setLanguage(nextLanguage: Language) {
    setLanguageState(nextLanguage);
    window.localStorage.setItem("ic-language", nextLanguage);
    document.documentElement.lang = nextLanguage === "zh" ? "zh-CN" : "en";
    const url = new URL(window.location.href);
    url.searchParams.set("lang", nextLanguage);
    window.history.replaceState(null, "", url);
  }

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      setLanguage,
      t: (key) => dictionaries[language][key],
    }),
    [language],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
  return context;
}
