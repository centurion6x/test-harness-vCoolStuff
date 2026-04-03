type CacheEntry<T> = { data: T; expiresAt: number };
const cache = new Map<string, CacheEntry<any>>();

export async function cachedFetch<T>(url: string, ttlMs: number): Promise<T> {
  const now = Date.now();
  const cached = cache.get(url);

  // Return cached data if it's still valid
  if (cached && cached.expiresAt > now) {
    return cached.data as T;
  }

  // Fetch fresh data
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.status}`);
  }

  const data = await response.json() as T;

  // Store in cache with expiration time
  cache.set(url, {
    data,
    expiresAt: now + ttlMs,
  });

  return data;
}
