type CacheEntry<T> = { data: T; expiresAt: number };
const cache = new Map<string, CacheEntry<any>>();

async function cachedFetch<T>(url: string, ttlMs: number): Promise<T> {
  const cached = cache.get(url);
  if (cached && Date.now() < cached.expiresAt) {
    return cached.data as T;
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);

  const data: T = await res.json();
  cache.set(url, { data, expiresAt: Date.now() + ttlMs });
  return data;
}
