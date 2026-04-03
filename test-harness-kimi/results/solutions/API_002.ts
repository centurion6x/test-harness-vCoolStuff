declare function fetch(url: string): Promise<any>;

const inFlight = new Map<string, Promise<any>>();

export async function dedupedFetch<T>(url: string): Promise<T> {
  const existing = inFlight.get(url);
  if (existing) {
    return existing;
  }

  const promise = fetch(url)
    .then(r => r.json())
    .finally(() => {
      inFlight.delete(url);
    });

  inFlight.set(url, promise);
  return promise;
}
