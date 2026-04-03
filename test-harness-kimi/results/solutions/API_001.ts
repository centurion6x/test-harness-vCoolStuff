declare function fetch(url: string, options?: any): Promise<any>;

async function fetchWithRetry<T>(
  url: string,
  options: RequestInit,
  maxRetries: number
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);

      if (res.ok) {
        return res.json();
      }

      const status = res.status;
      if (status >= 400 && status < 500) {
        throw new Error(`HTTP ${status}: ${res.statusText}`);
      }

      if (attempt === maxRetries) {
        throw new Error(`HTTP ${status}: ${res.statusText}`);
      }

      const delay = 100 * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    } catch (err: any) {
      lastError = err;

      if (err.message && err.message.startsWith('HTTP 4')) {
        throw err;
      }

      if (attempt === maxRetries) {
        throw err;
      }

      const delay = 100 * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}
