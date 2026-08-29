"use client";

import { BookMarked, ChevronRight, LoaderCircle, Search, Waypoints } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { getConcepts } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import type { Concept } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ConceptBrowser() {
  const { language, t } = useLanguage();
  const [query, setQuery] = useState("");
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getConcepts()
      .then((items) => {
        setConcepts(items);
        setSelected(items[0]?.id ?? "");
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "API unavailable"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    return concepts.filter((concept) =>
      [concept.name, concept.chinese_name, concept.abbreviation ?? "", concept.definition, concept.definition_en ?? ""]
        .join(" ")
        .toLowerCase()
        .includes(normalized),
    );
  }, [concepts, query]);
  const active = concepts.find((concept) => concept.id === selected) ?? filtered[0];

  return (
    <main className="mx-auto max-w-[1320px] px-5 py-12 lg:px-8">
      <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
        <div><p className="lab-label">{t("concept.eyebrow")}</p><h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] md:text-5xl">{t("concept.title")}</h1><p className="mt-4 max-w-2xl text-sm leading-7 text-muted">{t("concept.description")}</p></div>
        <div className="relative w-full md:max-w-sm"><Search className="absolute left-3.5 top-3.5 h-4 w-4 text-muted" /><input value={query} onChange={(event) => setQuery(event.target.value)} className="h-11 w-full rounded-xl border border-line bg-panel pl-10 pr-4 text-sm outline-none focus:border-accent" placeholder={t("concept.placeholder")} /></div>
      </div>

      {loading ? <div className="grid min-h-[420px] place-items-center"><LoaderCircle className="h-7 w-7 animate-spin text-accent" /></div> : error ? <Card className="mt-10 p-5 text-amber-600">{t("concept.backendError")}：{error}</Card> : (
        <div className="mt-10 grid min-h-[560px] overflow-hidden rounded-2xl border border-line bg-panel shadow-panel lg:grid-cols-[340px_1fr]">
          <div className="border-b border-line lg:border-b-0 lg:border-r">
            <div className="border-b border-line px-5 py-4"><p className="lab-label">{t("concept.index")} · {filtered.length}</p></div>
            <div className="scrollbar-thin max-h-[620px] overflow-y-auto p-2">
              {filtered.map((concept) => (
                <button key={concept.id} onClick={() => setSelected(concept.id)} className={cn("flex w-full items-center justify-between rounded-xl px-4 py-3 text-left transition", active?.id === concept.id ? "bg-accent/8 text-accent" : "hover:bg-ink/5")}>
                  <span><span className="block text-sm font-medium">{concept.name}</span><span className="mt-1 block text-xs text-muted">{concept.chinese_name} · {concept.category}</span></span><ChevronRight className="h-4 w-4" />
                </button>
              ))}
            </div>
          </div>
          <article className="p-7 lg:p-10">
            {active ? <>
              <div className="flex flex-wrap items-center gap-2"><Badge className="border-accent/25 bg-accent/5 text-accent">{active.category}</Badge>{active.abbreviation ? <Badge>{active.abbreviation}</Badge> : null}</div>
              <h2 className="mt-6 text-4xl font-semibold tracking-[-0.04em]">{active.name}</h2><p className="mt-2 text-lg text-muted">{active.chinese_name}</p>
              <div className="mt-10 border-t border-line pt-8"><div className="flex items-center gap-2"><BookMarked className="h-4 w-4 text-accent" /><p className="lab-label">{t("concept.definition")}</p></div><p className="mt-4 max-w-3xl text-base leading-8 text-muted">{language === "en" ? active.definition_en || active.definition : active.definition}</p></div>
              <div className="mt-10"><div className="flex items-center gap-2"><Waypoints className="h-4 w-4 text-signal" /><p className="lab-label">{t("concept.related")}</p></div><div className="mt-4 flex flex-wrap gap-2">{active.related.map((relation) => <span key={relation} className="rounded-xl border border-line bg-canvas px-3 py-2 font-mono text-xs text-muted">{active.id} <span className="mx-1 text-signal">→ related →</span> {relation}</span>)}</div></div>
            </> : <p className="text-sm text-muted">{t("concept.none")}</p>}
          </article>
        </div>
      )}
    </main>
  );
}
