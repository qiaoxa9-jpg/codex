export type AnswerMode = "engineering" | "research" | "learning";

export interface Evidence {
  source_id: string;
  title: string;
  source: string;
  document_type: string;
  url: string;
  year?: number;
  authors: string[];
  venue?: string;
  doi?: string;
  citation_count: number;
  open_access: boolean;
  excerpt: string;
  domains: string[];
  authority_score: number;
  engineering_applicability: number;
  evidence_level: string;
  relevance: number;
  score: number;
}

export interface ResearchResponse {
  question: string;
  mode: AnswerMode;
  classification: {
    category: string;
    confidence: number;
    signals: string[];
  };
  answer_status: string;
  sections: Array<{
    key: string;
    title: string;
    content: string;
    source_ids: string[];
    code?: string;
  }>;
  evidences: Evidence[];
  citations: Array<{
    number: number;
    source_id: string;
    title: string;
    url: string;
  }>;
  warnings: string[];
  trace: {
    query_expansions: string[];
    channels: string[];
    candidates: number;
    selected: number;
    external_status: Record<string, string>;
  };
}

export interface Paper {
  paper_id: string;
  title: string;
  abstract?: string;
  authors: string[];
  year?: number;
  venue?: string;
  doi?: string;
  citation_count: number;
  url: string;
  source: string;
  open_access: boolean;
}

export interface Concept {
  id: string;
  name: string;
  abbreviation?: string;
  chinese_name: string;
  definition: string;
  definition_en?: string;
  category: string;
  related: string[];
}
