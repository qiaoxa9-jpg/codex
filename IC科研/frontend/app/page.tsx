"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpenText,
  Braces,
  FileSearch,
  GitMerge,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { MetricStrip } from "@/components/metric-strip";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

const capabilities = [
  {
    icon: GitMerge,
    index: "01",
    title: "home.engineeringDiagnosis",
    copy: "home.engineeringCopy",
  },
  {
    icon: FileSearch,
    index: "02",
    title: "home.literatureIntelligence",
    copy: "home.literatureCopy",
  },
  {
    icon: ShieldCheck,
    index: "03",
    title: "home.citationFirewall",
    copy: "home.citationCopy",
  },
] satisfies Array<{ icon: typeof GitMerge; index: string; title: TranslationKey; copy: TranslationKey }>;

export default function HomePage() {
  const { t } = useLanguage();
  return (
    <main className="relative overflow-hidden">
      <div className="page-grid pointer-events-none absolute inset-x-0 top-0 h-[620px] bg-grid" />
      <section className="relative mx-auto max-w-[1320px] px-5 pb-16 pt-20 lg:px-8 lg:pb-24 lg:pt-28">
        <div className="grid items-end gap-12 lg:grid-cols-[1.2fr_.8fr]">
          <div>
            <Badge className="border-accent/30 bg-accent/5 text-accent">
              {t("home.badge")}
            </Badge>
            <h1 className="text-balance mt-7 max-w-4xl text-[clamp(3.15rem,7vw,6.7rem)] font-semibold leading-[0.92] tracking-[-0.07em]">
              {t("home.titlePrimary")}
              <span className="block text-muted">{t("home.titleSecondary")}</span>
            </h1>
            <p className="mt-8 max-w-2xl text-balance text-base leading-8 text-muted lg:text-lg">
              {t("home.description")}
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Button asChild variant="accent" size="lg">
                <Link href="/research">
                  {t("home.start")} <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="/papers">{t("home.searchPapers")}</Link>
              </Button>
            </div>
          </div>

          <Card className="relative overflow-hidden p-5 lg:p-6">
            <div className="absolute right-0 top-0 h-36 w-36 bg-accent/10 blur-3xl" />
            <div className="flex items-center justify-between border-b border-line pb-4">
              <div>
                <p className="lab-label">{t("home.trace")}</p>
                <p className="mt-1 text-sm font-medium">{t("home.sample")}</p>
              </div>
              <span className="rounded-full bg-signal/10 px-2.5 py-1 font-mono text-[10px] text-signal">
                {t("home.grounded")}
              </span>
            </div>
            <div className="space-y-5 py-5">
              {[
                [t("home.classify"), t("home.classifyValue"), "01"],
                [t("home.retrieve"), t("home.retrieveValue"), "02"],
                [t("home.rerank"), t("home.rerankValue"), "03"],
                [t("home.validate"), t("home.validateValue"), "04"],
              ].map(([label, value, number]) => (
                <div key={label} className="grid grid-cols-[34px_92px_1fr] items-center gap-3">
                  <span className="font-mono text-[10px] text-muted">{number}</span>
                  <span className="font-mono text-[10px] tracking-wider text-accent">{label}</span>
                  <span className="text-xs text-ink">{value}</span>
                </div>
              ))}
            </div>
            <div className="rounded-xl border border-line bg-canvas p-4 font-mono text-[11px] leading-6 text-muted">
              <span className="text-signal">{t("home.recommendation")}</span> → {t("home.recommendationValue")}
              <br />
              <span className="text-accent">{t("home.evidence")}</span> → [AMD-UG949, INTEL-TA]
            </div>
          </Card>
        </div>

        <div className="mt-16">
          <MetricStrip />
        </div>
      </section>

      <section className="border-y border-line bg-panel/50">
        <div className="mx-auto max-w-[1320px] px-5 py-20 lg:px-8">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div>
              <p className="lab-label">{t("home.architecture")}</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] md:text-4xl">{t("home.designedForProof")}</h2>
            </div>
            <p className="max-w-lg text-sm leading-7 text-muted">
              {t("home.accuracy")}
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {capabilities.map(({ icon: Icon, index, title, copy }) => (
              <Card key={title} className="group p-6 shadow-none transition hover:-translate-y-1 hover:shadow-panel">
                <div className="flex items-center justify-between">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-accent/8 text-accent">
                    <Icon className="h-5 w-5" />
                  </span>
                  <span className="font-mono text-[11px] text-muted">/{index}</span>
                </div>
                <h3 className="mt-8 text-lg font-semibold">{t(title)}</h3>
                <p className="mt-3 text-sm leading-7 text-muted">{t(copy)}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1320px] gap-8 px-5 py-20 lg:grid-cols-2 lg:px-8">
        <Card className="p-7 shadow-none">
          <BookOpenText className="h-5 w-5 text-accent" />
          <p className="lab-label mt-8">{t("home.knowledgeModel")}</p>
          <h3 className="mt-3 text-2xl font-semibold tracking-tight">{t("home.conceptsSystem")}</h3>
          <p className="mt-4 text-sm leading-7 text-muted">
            {t("home.conceptsCopy")}
          </p>
          <Button asChild variant="ghost" className="mt-5 px-0 text-accent">
            <Link href="/encyclopedia">{t("home.enterEncyclopedia")} <ArrowRight className="h-4 w-4" /></Link>
          </Button>
        </Card>
        <Card className="p-7 shadow-none">
          <Braces className="h-5 w-5 text-signal" />
          <p className="lab-label mt-8">{t("home.structuredAnswers")}</p>
          <h3 className="mt-3 text-2xl font-semibold tracking-tight">{t("home.rtlEvidence")}</h3>
          <p className="mt-4 text-sm leading-7 text-muted">
            {t("home.rtlCopy")}
          </p>
          <div className="mt-6 flex items-center gap-2 text-xs text-muted">
            <Sparkles className="h-4 w-4 text-signal" /> {t("home.evidenceFirst")}
          </div>
        </Card>
      </section>
    </main>
  );
}
