class ApiService {
  private baseUrl: string;
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request<T>(url: string): Promise<T> {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${this.token}` } });
    if (!res.ok) throw new Error(`Failed to fetch`);
    return res.json();
  }

  async getUsers(): Promise<any> {
    return this.request<any>('/api/users');
  }

  async getOrders(): Promise<any> {
    return this.request<any>('/api/orders');
  }

  async getProducts(): Promise<any> {
    return this.request<any>('/api/products');
  }
}
