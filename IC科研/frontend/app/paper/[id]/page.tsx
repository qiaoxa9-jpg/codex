"use client";

import { useParams, useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowUpRight, BookOpen, LoaderCircle, Quote } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getPaper } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import type { Paper } from "@/lib/types";

export default function PaperDetailPage() {
  const { t } = useLanguage();
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const source = searchParams.get("source") ?? "Semantic Scholar";
  const [paper, setPaper] = useState<Paper | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getPaper(source, decodeURIComponent(params.id))
      .then(setPaper)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Paper not found"));
  }, [params.id, source]);

  if (error) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-16">
        <Button asChild variant="ghost" className="px-0"><Link href="/papers"><ArrowLeft className="h-4 w-4" />{t("paper.back")}</Link></Button>
        <Card className="mt-8 p-6 text-sm text-amber-600">{t("paper.notFound")} · {source}：{error}</Card>
      </main>
    );
  }

  if (!paper) {
    return <main className="grid min-h-[70vh] place-items-center"><LoaderCircle className="h-7 w-7 animate-spin text-accent" /></main>;
  }

  return (
    <main className="mx-auto max-w-[1120px] px-5 py-12 lg:px-8">
      <Button asChild variant="ghost" className="px-0"><Link href="/papers"><ArrowLeft className="h-4 w-4" />{t("paper.back")}</Link></Button>
      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_300px]">
        <article>
          <div className="flex flex-wrap gap-2"><Badge>{paper.source}</Badge>{paper.open_access ? <Badge className="border-signal/25 text-signal">{t("papers.openAccess")}</Badge> : null}</div>
          <h1 className="mt-5 text-balance text-4xl font-semibold leading-[1.1] tracking-[-0.05em]">{paper.title}</h1>
          <p className="mt-5 text-sm leading-7 text-muted">{paper.authors.join(", ") || t("paper.authorUnavailable")}</p>
          <div className="mt-8 border-t border-line pt-8">
            <div className="flex items-center gap-2"><Quote className="h-4 w-4 text-accent" /><p className="lab-label">{t("paper.abstract")}</p></div>
            <p className="mt-4 whitespace-pre-line text-sm leading-8 text-muted">{paper.abstract || t("paper.abstractUnavailable")}</p>
          </div>
        </article>
        <aside>
          <Card className="sticky top-24 p-5 shadow-none">
            <p className="lab-label">{t("paper.metadata")}</p>
            <dl className="mt-5 space-y-4 text-sm">
              {[ [t("paper.year"), paper.year ?? "N/A"], [t("paper.venue"), paper.venue ?? "N/A"], [t("paper.citations"), paper.citation_count], ["DOI", paper.doi ?? "N/A"] ].map(([term, value]) => (
                <div key={String(term)} className="border-b border-line pb-3 last:border-0"><dt className="text-xs text-muted">{term}</dt><dd className="mt-1 break-all font-medium">{value}</dd></div>
              ))}
            </dl>
            <Button asChild variant="accent" className="mt-5 w-full"><a href={paper.url} target="_blank" rel="noreferrer"><BookOpen className="h-4 w-4" />{t("paper.openOriginal")}<ArrowUpRight className="h-3.5 w-3.5" /></a></Button>
          </Card>
        </aside>
      </div>
    </main>
  );
}
