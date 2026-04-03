class ApiService {
  private async request<T>(endpoint: string): Promise<T> {
    const res = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }
}

async function getUsers() {
  const service = new ApiService();
  return service.get('/api/users');
}

async function getOrders() {
  const service = new ApiService();
  return service.get('/api/orders');
}

async function getProducts() {
  const service = new ApiService();
  return service.get('/api/products');
}
