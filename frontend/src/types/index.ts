export interface Scan {
  id: string;
  target_id: string;
  status: "pending" | "running" | "completed" | "failed";
  scan_mode: "quick" | "standard" | "deep" | "custom";
  attack_count: number;
  completed_count: number;
  risk_score: number | null;
  asr: number | null;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  target?: Target;
}

export interface Target {
  id: string;
  name: string;
  endpoint_url: string;
  model_type: string;
  provider: string;
  is_active: boolean;
  created_at: string;
  scan_count?: number;
  last_scan_date?: string;
}

export interface AttackResult {
  id: string;
  attack_id: string;
  attack_name: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low";
  success: boolean;
  confidence: number;
  evidence: string;
  payload: string;
  response_snippet: string;
  remediation: string;
  framework_mapping: Record<string, string>;
  created_at: string;
}

export interface ComplianceAssessment {
  id: string;
  framework: string;
  score: number;
  status: string;
  control_results: Record<string, unknown>;
  gap_analysis: unknown[];
  created_at: string;
}

export interface ComplianceFramework {
  id: string;
  name: string;
  description: string;
  framework_type: string;
  score: number;
  status: "compliant" | "partial" | "non_compliant";
  control_count: number;
  passed_controls: number;
  failed_controls: number;
  controls: ComplianceControl[];
}

export interface ComplianceControl {
  id: string;
  name: string;
  description: string;
  requirement: string;
  status: "pass" | "fail" | "partial";
  evidence: string[];
  remediation: string;
}

export interface Report {
  id: string;
  name: string;
  report_type: string;
  scan_ids: string[];
  created_at: string;
  created_by: string;
  status: string;
  download_url?: string;
}

export interface DashboardStats {
  total_scans: number;
  avg_risk_score: number;
  open_findings: number;
  compliance_score: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  last_scan_date: string | null;
  trends: TrendPoint[];
  framework_scores: Record<string, number>;
}

export interface TrendPoint {
  date: string;
  risk_score: number;
  scan_count: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "owner" | "admin" | "member" | "viewer";
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  plan: string;
  subscription_status: string;
  scans_used: number;
  scans_limit: number | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface ScanResultSummary {
  total_attacks: number;
  successful_attacks: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  categories_affected: string[];
  avg_confidence: number;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: "active" | "inactive";
  api_key: string;
  created_at: string;
  last_seen_at: string | null;
  organization_id: string;
}

export interface MonitoringSession {
  id: string;
  name: string;
  agent_id: string;
  status: "active" | "paused" | "completed";
  start_time: string;
  end_time: string | null;
  metrics: Record<string, unknown>;
  alerts: MonitoringAlert[];
}

export interface MonitoringAlert {
  id: string;
  type: string;
  severity: "critical" | "high" | "medium" | "low";
  message: string;
  timestamp: string;
  resolved: boolean;
}
