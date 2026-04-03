const inFlight = new Map<string, Promise<any>>();

export async function dedupedFetch<T>(url: string): Promise<T> {
  if (inFlight.has(url)) {
    return inFlight.get(url)!;
  }

  const promise = fetch(url).then(r => r.json());
  inFlight.set(url, promise);

  promise.finally(() => {
    inFlight.delete(url);
  });

  return promise;
}
