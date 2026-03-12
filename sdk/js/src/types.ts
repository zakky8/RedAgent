export interface ScanStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  target_id: string;
  attack_categories: string[];
  total_attacks: number;
  completed_attacks: number;
  attack_success_rate: number;
  risk_score: number;
  created_at: string;
  completed_at?: string;
}

export interface AttackResult {
  id: string;
  scan_id: string;
  attack_id: string;
  attack_name: string;
  attack_category: string;
  success: boolean;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  payload: string;
  response: string;
  evidence: string;
  remediation: string;
  cvss_score: number;
  created_at: string;
}

export interface Target {
  id: string;
  name: string;
  description?: string;
  adapter_type: string;
  config: Record<string, string>;
  org_id: string;
  created_at: string;
}

export interface CreateScanRequest {
  target_id: string;
  attack_categories?: string[];
  attack_ids?: string[];
  max_attacks?: number;
  stop_on_critical?: boolean;
}

export interface CreateTargetRequest {
  name: string;
  description?: string;
  adapter_type: string;
  config: Record<string, string>;
}

export interface Report {
  id: string;
  scan_id: string;
  report_type: string;
  status: 'generating' | 'ready' | 'failed';
  download_url?: string;
  created_at: string;
}

export interface ComplianceAssessment {
  id: string;
  framework: string;
  score: number;
  max_score: number;
  percentage: number;
  controls: ComplianceControl[];
  gaps: string[];
  created_at: string;
}

export interface ComplianceControl {
  id: string;
  name: string;
  passed: boolean;
  score: number;
  max_score: number;
  evidence: string[];
}

export interface AgentRedClientConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
