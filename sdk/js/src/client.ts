import axios, { AxiosInstance, AxiosError } from 'axios';
import { AgentRedClientConfig, LoginResponse } from './types';
import { ScansResource } from './resources/scans';
import { TargetsResource } from './resources/targets';
import { ReportsResource } from './resources/reports';
import { ComplianceResource } from './resources/compliance';
import { AttacksResource } from './resources/attacks';

export class AgentRedClient {
  private http: AxiosInstance;
  public scans: ScansResource;
  public targets: TargetsResource;
  public reports: ReportsResource;
  public compliance: ComplianceResource;
  public attacks: AttacksResource;

  constructor(private config: AgentRedClientConfig) {
    this.http = axios.create({
      baseURL: (config.baseUrl || 'https://api.agentred.io') + '/api/v1',
      timeout: config.timeout || 60000,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'agentred-js/0.1.0',
      },
    });

    this.http.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          throw new AgentRedAuthError('Invalid or expired API key');
        }
        if (error.response?.status === 429) {
          throw new AgentRedRateLimitError('Rate limit exceeded');
        }
        const message = (error.response?.data as any)?.detail || error.message;
        throw new AgentRedError(message, error.response?.status);
      }
    );

    this.scans = new ScansResource(this.http);
    this.targets = new TargetsResource(this.http);
    this.reports = new ReportsResource(this.http);
    this.compliance = new ComplianceResource(this.http);
    this.attacks = new AttacksResource(this.http);
  }

  async ping(): Promise<boolean> {
    try {
      await this.http.get('/health');
      return true;
    } catch {
      return false;
    }
  }
}

export class AgentRedError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'AgentRedError';
  }
}

export class AgentRedAuthError extends AgentRedError {
  constructor(message: string) {
    super(message, 401);
    this.name = 'AgentRedAuthError';
  }
}

export class AgentRedRateLimitError extends AgentRedError {
  constructor(message: string) {
    super(message, 429);
    this.name = 'AgentRedRateLimitError';
  }
}
