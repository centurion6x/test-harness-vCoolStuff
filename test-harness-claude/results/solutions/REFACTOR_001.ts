class ApiService {
  private getToken: () => string;

  constructor(getToken: () => string) {
    this.getToken = getToken;
  }

  async get<T>(endpoint: string): Promise<T> {
    const res = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${this.getToken()}` },
    });
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json();
  }
}

function getToken(): string {
  return '';
}

const api = new ApiService(getToken);

async function getUsers() {
  return api.get('/api/users');
}

async function getOrders() {
  return api.get('/api/orders');
}

async function getProducts() {
  return api.get('/api/products');
}
