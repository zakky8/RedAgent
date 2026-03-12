import { AxiosInstance } from 'axios';
import { ScanStatus, AttackResult, CreateScanRequest, PaginatedResponse } from '../types';

export class ScansResource {
  constructor(private http: AxiosInstance) {}

  async list(params?: { page?: number; per_page?: number; status?: string }): Promise<PaginatedResponse<ScanStatus>> {
    const { data } = await this.http.get('/scans', { params });
    return data;
  }

  async create(request: CreateScanRequest): Promise<ScanStatus> {
    const { data } = await this.http.post('/scans', request);
    return data;
  }

  async get(scanId: string): Promise<ScanStatus> {
    const { data } = await this.http.get(`/scans/${scanId}`);
    return data;
  }

  async getResults(scanId: string): Promise<AttackResult[]> {
    const { data } = await this.http.get(`/scans/${scanId}/results`);
    return data;
  }

  async cancel(scanId: string): Promise<void> {
    await this.http.post(`/scans/${scanId}/cancel`);
  }

  async waitForCompletion(scanId: string, pollIntervalMs: number = 5000): Promise<ScanStatus> {
    while (true) {
      const scan = await this.get(scanId);
      if (scan.status === 'completed' || scan.status === 'failed') {
        return scan;
      }
      await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
    }
  }
}
