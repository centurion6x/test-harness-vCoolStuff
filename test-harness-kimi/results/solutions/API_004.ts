declare function fetch(url: string): Promise<any>;

type CacheEntry<T> = { data: T; expiresAt: number };
const cache = new Map<string, CacheEntry<any>>();

export async function cachedFetch<T>(url: string, ttlMs: number): Promise<T> {
  const entry = cache.get(url);

  if (entry && entry.expiresAt > Date.now()) {
    return entry.data;
  }

  const res = await fetch(url);
  const data: T = await res.json();

  cache.set(url, {
    data,
    expiresAt: Date.now() + ttlMs
  });

  return data;
}
