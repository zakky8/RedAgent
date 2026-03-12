import { AxiosInstance } from 'axios';
import { Report } from '../types';

export class ReportsResource {
  constructor(private http: AxiosInstance) {}

  async list(): Promise<Report[]> {
    const { data } = await this.http.get('/reports');
    return data;
  }

  async generate(scanId: string, reportType: string = 'executive'): Promise<Report> {
    const { data } = await this.http.post('/reports', { scan_id: scanId, report_type: reportType });
    return data;
  }

  async get(reportId: string): Promise<Report> {
    const { data } = await this.http.get(`/reports/${reportId}`);
    return data;
  }

  async download(reportId: string): Promise<Buffer> {
    const { data } = await this.http.get(`/reports/${reportId}/download`, { responseType: 'arraybuffer' });
    return Buffer.from(data);
  }
}
