import { AxiosInstance } from 'axios';
import { ComplianceAssessment } from '../types';

export class ComplianceResource {
  constructor(private http: AxiosInstance) {}

  async listFrameworks(): Promise<string[]> {
    const { data } = await this.http.get('/compliance/frameworks');
    return data;
  }

  async assess(scanId: string, framework: string): Promise<ComplianceAssessment> {
    const { data } = await this.http.post('/compliance/assess', { scan_id: scanId, framework });
    return data;
  }

  async getAssessment(assessmentId: string): Promise<ComplianceAssessment> {
    const { data } = await this.http.get(`/compliance/${assessmentId}`);
    return data;
  }

  async getSummary(scanId: string): Promise<Record<string, ComplianceAssessment>> {
    const { data } = await this.http.get(`/compliance/summary/${scanId}`);
    return data;
  }
}
