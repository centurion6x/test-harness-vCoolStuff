declare function getToken(): string;
declare function fetch(url: string, options?: any): Promise<any>;

class ApiService {
  async get<T>(endpoint: string): Promise<T> {
    const res = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return res.json();
  }
}
