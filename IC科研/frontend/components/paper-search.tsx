"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  ExternalLink,
  LoaderCircle,
  Search,
  ShieldAlert,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { searchPapers } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import type { Paper } from "@/lib/types";

export function PaperSearch() {
  const { t } = useLanguage();
  const [query, setQuery] = useState("clock domain crossing verification");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [statuses, setStatuses] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (query.trim().length < 2 || loading) return;
    setLoading(true);
    setError("");
    try {
      const response = await searchPapers(query.trim());
      setPapers(response.results);
      setStatuses(response.provider_status);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t("papers.error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-[1280px] px-5 py-12 lg:px-8">
      <div className="grid gap-8 lg:grid-cols-[.72fr_1.28fr] lg:items-end">
        <div>
          <p className="lab-label">{t("papers.eyebrow")}</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] md:text-5xl">{t("papers.titleA")}<br />{t("papers.titleB")}</h1>
          <p className="mt-5 max-w-xl text-sm leading-7 text-muted">
            {t("papers.description")}
          </p>
        </div>
        <Card className="p-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-muted" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && submit()}
                className="h-11 w-full rounded-xl border border-line bg-canvas pl-10 pr-4 text-sm outline-none focus:border-accent focus:ring-4 focus:ring-accent/8"
                placeholder={t("papers.placeholder")}
              />
            </div>
            <Button variant="accent" className="h-11" onClick={submit} disabled={loading}>
              {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              {t("papers.search")}
            </Button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(statuses).map(([provider, status]) => (
              <Badge key={provider} className={status === "ok" ? "border-signal/20 text-signal" : "border-amber-500/30 text-amber-600"}>
                {provider}: {status}
              </Badge>
            ))}
          </div>
        </Card>
      </div>

      {error ? (
        <div className="mt-8 flex gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-700 dark:text-amber-300">
          <ShieldAlert className="h-4 w-4 shrink-0" /> {error}
        </div>
      ) : null}

      <div className="mt-12 border-t border-line">
        {papers.length ? (
          papers.map((paper, index) => (
            <article key={`${paper.source}-${paper.paper_id}`} className="group grid gap-5 border-b border-line py-7 md:grid-cols-[44px_1fr_auto] md:items-start">
              <span className="font-mono text-xs text-muted">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge>{paper.source}</Badge>
                  {paper.open_access ? <Badge className="border-signal/25 text-signal">{t("papers.openAccess")}</Badge> : null}
                </div>
                <h2 className="mt-3 max-w-3xl text-lg font-semibold leading-7 tracking-tight group-hover:text-accent">{paper.title}</h2>
                <p className="mt-2 text-xs text-muted">
                  {paper.authors.slice(0, 4).join(", ") || t("papers.authorUnavailable")}
                  {paper.authors.length > 4 ? " et al." : ""}
                </p>
                <div className="mt-4 flex flex-wrap gap-4 text-xs text-muted">
                  <span className="inline-flex items-center gap-1.5"><CalendarDays className="h-3.5 w-3.5" />{paper.year ?? "N/A"}</span>
                  <span className="inline-flex items-center gap-1.5"><BookOpen className="h-3.5 w-3.5" />{paper.venue || t("papers.venueUnavailable")}</span>
                  <span>{t("papers.citedBy")} {paper.citation_count}</span>
                  {paper.doi ? <span className="font-mono">DOI {paper.doi}</span> : null}
                </div>
              </div>
              <div className="flex gap-2 md:justify-end">
                <Button asChild variant="outline" size="sm">
                  <Link href={`/paper/${encodeURIComponent(paper.paper_id)}?source=${encodeURIComponent(paper.source)}`}>
                    {t("papers.detail")} <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
                <Button asChild variant="ghost" size="icon">
                  <a href={paper.url} target="_blank" rel="noreferrer" aria-label={t("papers.openOriginal")}>
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            </article>
          ))
        ) : (
          <div className="grid min-h-[340px] place-items-center text-center">
            <div>
              <BookOpen className="mx-auto h-7 w-7 text-accent" />
              <p className="mt-4 text-sm font-medium">{t("papers.emptyTitle")}</p>
              <p className="mt-2 text-xs text-muted">{t("papers.emptyCopy")}</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
