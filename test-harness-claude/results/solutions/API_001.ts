async function fetchWithRetry<T>(url: string, options: RequestInit, maxRetries: number): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);

      if (res.status >= 400 && res.status < 500) {
        throw new Error(`Client error: ${res.status}`);
      }

      if (res.status >= 500) {
        throw new Error(`Server error: ${res.status}`);
      }

      return await res.json() as T;
    } catch (err) {
      lastError = err as Error;

      if ((err as Error).message.startsWith('Client error')) {
        throw err;
      }

      if (attempt < maxRetries) {
        const delay = 100 * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
