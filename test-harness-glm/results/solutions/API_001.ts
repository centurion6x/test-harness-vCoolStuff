async function fetchWithRetry<T>(url: string, options: RequestInit, maxRetries: number): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);

      if (res.ok) {
        return res.json();
      }

      if (res.status >= 400 && res.status < 500) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      lastError = new Error(`Request failed with status ${res.status}`);
    } catch (err) {
      lastError = err as Error;

      if (err instanceof Error && err.message.includes('4')) {
        throw err;
      }
    }

    if (attempt < maxRetries) {
      const delay = 100 * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError || new Error('Request failed');
}
