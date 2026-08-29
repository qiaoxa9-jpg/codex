import type { AnswerMode, Concept, Paper, ResearchResponse } from "./types";
import type { Language } from "./i18n";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function askResearch(question: string, mode: AnswerMode, language: Language) {
  return apiFetch<ResearchResponse>("/research/ask", {
    method: "POST",
    body: JSON.stringify({ question, mode, language, max_evidence: 6 }),
  });
}

export function searchPapers(query: string) {
  return apiFetch<{
    query: string;
    results: Paper[];
    provider_status: Record<string, string>;
  }>(`/papers/search?q=${encodeURIComponent(query)}&limit=12`);
}

export function getPaper(source: string, paperId: string) {
  return apiFetch<Paper>(
    `/papers/detail?source=${encodeURIComponent(source)}&paper_id=${encodeURIComponent(paperId)}`,
  );
}

export function getConcepts(query = "") {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return apiFetch<Concept[]>(`/concepts${suffix}`);
}
