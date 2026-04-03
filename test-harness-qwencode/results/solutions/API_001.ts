async function fetchWithRetry<T>(url: string, options: RequestInit, maxRetries: number): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);

      // Don't retry on 4xx errors
      if (res.status >= 400 && res.status < 500) {
        throw new Error(`Client error: ${res.status}`);
      }

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      return res.json();
    } catch (err) {
      lastError = err as Error;

      // Only retry on network errors or 5xx, and only if we have retries left
      if (attempt < maxRetries) {
        const delay = 100 * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}
