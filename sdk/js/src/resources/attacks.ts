import { AxiosInstance } from 'axios';

export class AttacksResource {
  constructor(private http: AxiosInstance) {}

  async list(category?: string): Promise<any[]> {
    const { data } = await this.http.get('/attacks', { params: { category } });
    return data;
  }

  async getCategories(): Promise<string[]> {
    const { data } = await this.http.get('/attacks/categories');
    return data;
  }

  async getStats(): Promise<{ total: number; by_category: Record<string, number> }> {
    const { data } = await this.http.get('/attacks/stats');
    return data;
  }
}
