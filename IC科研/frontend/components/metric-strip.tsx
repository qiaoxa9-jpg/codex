"use client";

import { useLanguage, type TranslationKey } from "@/lib/i18n";

const metrics: Array<[string, TranslationKey]> = [
  ["14", "metric.questionClasses"],
  ["5", "metric.evidenceSignals"],
  ["3", "metric.answerModes"],
  ["0", "metric.unboundCitations"],
];

export function MetricStrip() {
  const { t } = useLanguage();
  return (
    <div className="grid overflow-hidden rounded-2xl border border-line bg-panel sm:grid-cols-4">
      {metrics.map(([value, label], index) => (
        <div
          key={label}
          className={`p-5 ${index ? "border-t border-line sm:border-l sm:border-t-0" : ""}`}
        >
          <div className="font-mono text-2xl font-semibold tracking-tight">{value}</div>
          <div className="mt-1 text-xs text-muted">{t(label)}</div>
        </div>
      ))}
    </div>
  );
}
