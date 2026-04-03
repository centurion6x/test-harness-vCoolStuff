const inFlight = new Map<string, Promise<any>>();

export async function dedupedFetch<T>(url: string): Promise<T> {
  // If a request to this URL is already in-flight, return the same promise
  if (inFlight.has(url)) {
    return inFlight.get(url) as Promise<T>;
  }

  // Create the new request promise
  const promise = fetch(url).then(r => {
    if (!r.ok) {
      throw new Error(`HTTP error: ${r.status}`);
    }
    return r.json();
  });

  // Store the promise before executing (to handle immediate duplicate calls)
  inFlight.set(url, promise);

  // Clean up after the promise settles
  promise
    .finally(() => {
      inFlight.delete(url);
    });

  return promise;
}
