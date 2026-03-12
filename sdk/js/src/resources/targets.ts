import { AxiosInstance } from 'axios';
import { Target, CreateTargetRequest } from '../types';

export class TargetsResource {
  constructor(private http: AxiosInstance) {}

  async list(): Promise<Target[]> {
    const { data } = await this.http.get('/targets');
    return data;
  }

  async create(request: CreateTargetRequest): Promise<Target> {
    const { data } = await this.http.post('/targets', request);
    return data;
  }

  async get(targetId: string): Promise<Target> {
    const { data } = await this.http.get(`/targets/${targetId}`);
    return data;
  }

  async update(targetId: string, updates: Partial<CreateTargetRequest>): Promise<Target> {
    const { data } = await this.http.patch(`/targets/${targetId}`, updates);
    return data;
  }

  async delete(targetId: string): Promise<void> {
    await this.http.delete(`/targets/${targetId}`);
  }

  async testConnection(targetId: string): Promise<{ connected: boolean; latency_ms: number; error?: string }> {
    const { data } = await this.http.post(`/targets/${targetId}/test`);
    return data;
  }
}
