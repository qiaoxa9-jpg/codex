"use client";

import {
  AlertTriangle,
  ArrowUpRight,
  BookMarked,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Copy,
  LoaderCircle,
  Network,
  Search,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { askResearch } from "@/lib/api";
import { useLanguage, type Language, type TranslationKey } from "@/lib/i18n";
import type { AnswerMode, Evidence, ResearchResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

const modes: Array<{ value: AnswerMode; label: TranslationKey; hint: string }> = [
  { value: "engineering", label: "research.modeEngineering", hint: "Root cause · RTL · verification" },
  { value: "research", label: "research.modeResearch", hint: "Literature · methods · gaps" },
  { value: "learning", label: "research.modeLearning", hint: "Principle · example · path" },
];

const exampleQuestionKeys: TranslationKey[] = [
  "research.example1",
  "research.example2",
  "research.example3",
];

function CitationLinks({ ids, result }: { ids: string[]; result: ResearchResponse }) {
  if (!ids.length) return null;
  return (
    <span className="ml-1 inline-flex gap-1 align-super">
      {ids.map((id) => {
        const citation = result.citations.find((item) => item.source_id === id);
        return citation ? (
          <a
            key={id}
            href={`#evidence-${id}`}
            className="font-mono text-[10px] font-semibold text-accent hover:underline"
          >
            [{citation.number}]
          </a>
        ) : null;
      })}
    </span>
  );
}

function EvidenceCard({ evidence, number }: { evidence: Evidence; number?: number }) {
  const { t } = useLanguage();
  return (
    <article id={`evidence-${evidence.source_id}`} className="scroll-mt-24 border-b border-line p-5 last:border-b-0">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          {number ? (
            <span className="grid h-6 w-6 place-items-center rounded-md bg-accent/10 font-mono text-[10px] font-semibold text-accent">
              {number}
            </span>
          ) : null}
          <Badge className="border-signal/20 bg-signal/5 text-signal">{evidence.evidence_level}</Badge>
        </div>
        <span className="font-mono text-[10px] text-muted">{Math.round(evidence.score * 100)} {t("research.score")}</span>
      </div>
      <h3 className="mt-4 text-sm font-semibold leading-6">{evidence.title}</h3>
      <p className="mt-1 text-xs text-muted">
        {evidence.source} · {evidence.document_type} {evidence.year ? `· ${evidence.year}` : ""}
      </p>
      <p className="mt-3 text-xs leading-6 text-muted">{evidence.excerpt}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="font-mono text-[9px] text-muted">{evidence.source_id}</span>
        <a
          href={evidence.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-xs font-medium text-accent hover:underline"
        >
          {t("research.openSource")} <ArrowUpRight className="h-3 w-3" />
        </a>
      </div>
    </article>
  );
}

export function ResearchWorkbench() {
  const { language, t } = useLanguage();
  const [question, setQuestion] = useState("单比特异步信号如何安全跨时钟域？");
  const [mode, setMode] = useState<AnswerMode>("engineering");
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const previousLanguage = useRef<Language>(language);
  const questionEdited = useRef(false);

  const exampleQuestions = useMemo(
    () => exampleQuestionKeys.map((key) => t(key)),
    [t],
  );

  const evidenceNumber = useMemo(
    () => new Map(result?.citations.map((item) => [item.source_id, item.number]) ?? []),
    [result],
  );

  async function submit(requestLanguage: Language = language) {
    if (question.trim().length < 4 || loading) return;
    setLoading(true);
    setError("");
    try {
      setResult(await askResearch(question.trim(), mode, requestLanguage));
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `${t("research.backendError")}：${caught.message}`
          : `${t("research.backendError")}。`,
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (previousLanguage.current === language) return;
    previousLanguage.current = language;
    if (result) void submit(language);
    else if (!questionEdited.current) setQuestion(t("research.example1"));
    // Re-run an existing answer so generated sections match the selected language.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  return (
    <main className="mx-auto max-w-[1600px] px-4 py-5 lg:px-6">
      <div className="mb-4 grid gap-4 rounded-2xl border border-line bg-panel p-4 shadow-panel lg:grid-cols-[1fr_auto] lg:items-center">
        <div className="relative">
          <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-muted" />
          <textarea
            value={question}
            onChange={(event) => {
              questionEdited.current = true;
              setQuestion(event.target.value);
            }}
            onKeyDown={(event) => {
              if ((event.metaKey || event.ctrlKey) && event.key === "Enter") submit();
            }}
            className="min-h-[72px] w-full resize-none rounded-xl border border-line bg-canvas py-3 pl-10 pr-4 text-sm leading-6 outline-none transition placeholder:text-muted/70 focus:border-accent focus:ring-4 focus:ring-accent/8"
            placeholder={t("research.placeholder")}
          />
        </div>
        <div className="flex flex-wrap items-center gap-2 lg:justify-end">
          {modes.map((item) => (
            <button
              key={item.value}
              type="button"
              onClick={() => setMode(item.value)}
              title={item.hint}
              className={cn(
                "rounded-lg border px-3 py-2 text-xs font-medium transition",
                mode === item.value
                  ? "border-accent bg-accent/8 text-accent"
                  : "border-line text-muted hover:text-ink",
              )}
            >
              {t(item.label)}
            </button>
          ))}
          <Button variant="accent" onClick={() => submit()} disabled={loading}>
            {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <CircleDot className="h-4 w-4" />}
            {t("research.analyze")}
          </Button>
        </div>
      </div>

      {error ? (
        <div className="mb-4 flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-700 dark:text-amber-300">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="grid min-h-[calc(100vh-190px)] overflow-hidden rounded-2xl border border-line bg-panel shadow-panel lg:grid-cols-[230px_minmax(0,1fr)_360px]">
        <aside className="border-b border-line bg-canvas/40 p-5 lg:border-b-0 lg:border-r">
          <p className="lab-label">{t("research.queryAnalyzer")}</p>
          {result ? (
            <div className="mt-5 space-y-6">
              <div>
                <span className="font-mono text-2xl font-semibold tracking-tight">
                  {Math.round(result.classification.confidence * 100)}%
                </span>
                <Badge className="ml-2 border-accent/25 bg-accent/5 text-accent">
                  {result.classification.category}
                </Badge>
              </div>
              <div>
                <p className="lab-label">{t("research.signals")}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {result.classification.signals.map((signal) => (
                    <span key={signal} className="rounded-md bg-ink/5 px-2 py-1 text-[11px] text-muted">
                      {signal}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <p className="lab-label">{t("research.channels")}</p>
                <ol className="mt-3 space-y-3">
                  {result.trace.channels.map((channel, index) => (
                    <li key={channel} className="flex items-center gap-2 text-xs text-muted">
                      <span className="font-mono text-[9px]">0{index + 1}</span>
                      <ChevronRight className="h-3 w-3 text-line" />
                      {channel}
                    </li>
                  ))}
                </ol>
              </div>
              <div className="rounded-xl border border-line bg-panel p-3">
                <div className="flex items-center gap-2 text-xs font-medium">
                  <CheckCircle2 className="h-3.5 w-3.5 text-signal" /> {t("research.firewall")}
                </div>
                <p className="mt-2 text-[11px] leading-5 text-muted">
                  {result.citations.length} {t("research.idsPassed")}
                </p>
              </div>
            </div>
          ) : (
            <div className="mt-6 space-y-3">
              {exampleQuestions.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => {
                    questionEdited.current = false;
                    setQuestion(example);
                  }}
                  className="w-full rounded-xl border border-line bg-panel p-3 text-left text-xs leading-5 text-muted transition hover:border-accent/40 hover:text-ink"
                >
                  {example}
                </button>
              ))}
            </div>
          )}
        </aside>

        <section className="min-w-0 border-b border-line lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between border-b border-line px-6 py-4">
            <div>
              <p className="lab-label">{t("research.output")}</p>
              <h1 className="mt-1 text-base font-semibold">{t("research.answer")}</h1>
            </div>
            {result ? (
              <Badge className={result.answer_status === "grounded" ? "border-signal/25 text-signal" : "border-amber-500/30 text-amber-600"}>
                {result.answer_status}
              </Badge>
            ) : null}
          </div>

          <div className="scrollbar-thin max-h-[calc(100vh-250px)] overflow-y-auto p-6 lg:p-8">
            {loading ? (
              <div className="grid min-h-[420px] place-items-center text-center">
                <div>
                  <Network className="mx-auto h-8 w-8 animate-pulse text-accent" />
                  <p className="mt-4 text-sm font-medium">{t("research.building")}</p>
                  <p className="mt-2 font-mono text-[10px] text-muted">CLASSIFY → RETRIEVE → RERANK → VALIDATE</p>
                </div>
              </div>
            ) : result ? (
              <div className="answer-copy mx-auto max-w-3xl">
                <div className="mb-8 border-b border-line pb-6">
                  <p className="lab-label">{t("research.question")}</p>
                  <h2 className="mt-3 text-2xl font-semibold leading-tight tracking-[-0.03em]">{result.question}</h2>
                  {result.warnings.map((warning) => (
                    <p key={warning} className="mt-3 text-xs text-amber-600 dark:text-amber-300">{warning}</p>
                  ))}
                </div>
                <div className="space-y-10">
                  {result.sections.map((section, index) => (
                    <article key={section.key}>
                      <div className="flex items-baseline gap-3">
                        <span className="font-mono text-[10px] text-muted">{String(index + 1).padStart(2, "0")}</span>
                        <h3 className="text-lg font-semibold tracking-tight">{section.title}</h3>
                      </div>
                      <p className="mt-3 text-sm text-muted">
                        {section.content}
                        <CitationLinks ids={section.source_ids} result={result} />
                      </p>
                      {section.code ? (
                        <div className="relative mt-4 overflow-hidden rounded-xl border border-line bg-[#0b1020] text-slate-200">
                          <div className="flex items-center justify-between border-b border-white/10 px-4 py-2 font-mono text-[10px] text-slate-400">
                            <span>{t("research.codeCondition")}</span>
                            <Copy className="h-3 w-3" />
                          </div>
                          <pre className="overflow-x-auto p-4 text-xs leading-6"><code>{section.code}</code></pre>
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              </div>
            ) : (
              <div className="grid min-h-[460px] place-items-center">
                <div className="max-w-md text-center">
                  <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl border border-line bg-canvas">
                    <BookMarked className="h-6 w-6 text-accent" />
                  </span>
                  <h2 className="mt-5 text-xl font-semibold tracking-tight">{t("research.classifyFirst")}</h2>
                  <p className="mt-3 text-sm leading-7 text-muted">
                    {t("research.emptyHelp")}
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        <aside className="bg-canvas/30">
          <div className="flex items-center justify-between border-b border-line px-5 py-4">
            <div>
              <p className="lab-label">{t("research.evidenceContext")}</p>
              <p className="mt-1 text-sm font-semibold">{t("research.sources")}</p>
            </div>
            <span className="font-mono text-[10px] text-muted">{result?.evidences.length ?? 0} {t("research.selected")}</span>
          </div>
          <div className="scrollbar-thin max-h-[calc(100vh-250px)] overflow-y-auto">
            {result?.evidences.length ? (
              result.evidences.map((evidence) => (
                <EvidenceCard key={evidence.source_id} evidence={evidence} number={evidenceNumber.get(evidence.source_id)} />
              ))
            ) : (
              <div className="p-6 text-xs leading-6 text-muted">
                {t("research.emptyEvidence")}
              </div>
            )}
          </div>
        </aside>
      </div>
    </main>
  );
}
