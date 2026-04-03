const inFlight = new Map<string, Promise<any>>();

async function dedupedFetch<T>(url: string): Promise<T> {
  if (inFlight.has(url)) {
    return inFlight.get(url)! as Promise<T>;
  }

  const promise = fetch(url)
    .then(r => r.json())
    .finally(() => {
      inFlight.delete(url);
    });

  inFlight.set(url, promise);
  return promise as Promise<T>;
}
