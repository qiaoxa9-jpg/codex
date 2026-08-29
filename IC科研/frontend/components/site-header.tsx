"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CircuitBoard, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { useLanguage } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const navigation = [
  ["header.research", "/research"],
  ["header.papers", "/papers"],
  ["header.encyclopedia", "/encyclopedia"],
] as const;

export function SiteHeader() {
  const pathname = usePathname();
  const [dark, setDark] = useState(false);
  const { language, setLanguage, t } = useLanguage();

  useEffect(() => {
    const stored = window.localStorage.getItem("ic-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const nextDark = stored ? stored === "dark" : prefersDark;
    setDark(nextDark);
    document.documentElement.classList.toggle("dark", nextDark);
  }, []);

  function toggleTheme() {
    const nextDark = !dark;
    setDark(nextDark);
    document.documentElement.classList.toggle("dark", nextDark);
    window.localStorage.setItem("ic-theme", nextDark ? "dark" : "light");
  }

  return (
    <header className="sticky top-0 z-50 border-b border-line/80 bg-canvas/88 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1480px] items-center justify-between px-5 lg:px-8">
        <Link href="/" className="group flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-xl border border-line bg-ink text-canvas transition group-hover:rotate-3">
            <CircuitBoard className="h-4 w-4" />
          </span>
          <span>
            <span className="block text-sm font-semibold leading-none tracking-tight">IC Research Copilot</span>
            <span className="mt-1 block font-mono text-[9px] uppercase tracking-[0.17em] text-muted">
              Evidence-bound engineering
            </span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 rounded-xl border border-line bg-panel/70 p-1 md:flex">
          {navigation.map(([label, href]) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "rounded-lg px-3.5 py-2 text-xs font-medium text-muted transition hover:text-ink",
                pathname.startsWith(href) && "bg-ink text-canvas hover:text-canvas",
              )}
            >
              {t(label)}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <span className="hidden items-center gap-2 font-mono text-[10px] text-muted sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-signal shadow-[0_0_0_4px_rgb(var(--signal)/.12)]" />
            {t("header.traceable")}
          </span>
          <div
            className="flex items-center rounded-lg border border-line bg-panel p-0.5"
            role="group"
            aria-label={t("header.language")}
          >
            <button
              type="button"
              onClick={() => setLanguage("zh")}
              className={cn(
                "rounded-md px-2 py-1.5 font-mono text-[10px] transition",
                language === "zh" ? "bg-ink text-canvas" : "text-muted hover:text-ink",
              )}
              aria-pressed={language === "zh"}
            >
              中
            </button>
            <button
              type="button"
              onClick={() => setLanguage("en")}
              className={cn(
                "rounded-md px-2 py-1.5 font-mono text-[10px] transition",
                language === "en" ? "bg-ink text-canvas" : "text-muted hover:text-ink",
              )}
              aria-pressed={language === "en"}
            >
              EN
            </button>
          </div>
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label={t("header.theme")}>
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </header>
  );
}
