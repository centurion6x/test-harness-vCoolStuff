function getToken(): string {
  // Implementation of token retrieval
  return '';
}

interface ApiResponse<T> {
  data: T;
}

class ApiService {
  private baseUrl: string = '';
  private token: string = '';

  private async request<T>(endpoint: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json() as Promise<T>;
  }

  async getUsers<T>(): Promise<T> {
    return this.request<T>('/api/users');
  }

  async getOrders<T>(): Promise<T> {
    return this.request<T>('/api/orders');
  }

  async getProducts<T>(): Promise<T> {
    return this.request<T>('/api/products');
  }
}
