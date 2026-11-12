export interface LegalSource {
  id: string;
  title: string;
  source_type: string;
  citation: string;
  url_or_ref?: string;
  excerpt: string;
  relevance_score: number;
  is_verified: boolean;
}

export interface LegalRisk {
  risk_area: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  probability: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
  mitigation: string;
}

export interface LegalAnalysisResult {
  id: string;
  question: string;
  jurisdiction: string;
  facts_identified: string[];
  assumptions: string[];
  missing_info: string[];
  relevant_provisions: string[];
  analysis?: string;
  possible_issues: string[];
  risks_uncertainties: LegalRisk[];
  explanation?: string;
  limitations: string[];
  disclaimer: string;
  status: string;
  created_at: string;
  completed_at?: string;
  sources: LegalSource[];
}
