async function fetchWithRetry<T>(
  url: string,
  options: RequestInit,
  maxRetries: number
): Promise<T> {
  const delays = [100, 200, 400, 800, 1600]; // Exponential backoff

  async function attempt(attemptNumber: number): Promise<T> {
    try {
      const response = await fetch(url, options);

      // Don't retry on 4xx errors
      if (response.status >= 400 && response.status < 500) {
        throw new Error(`Client error: ${response.status}`);
      }

      // Retry on 5xx errors or network errors
      if (response.status >= 500 || !response.ok) {
        if (attemptNumber >= maxRetries) {
          throw new Error(`Failed after ${maxRetries} retries`);
        }
        await new Promise(resolve => setTimeout(resolve, delays[attemptNumber - 1] || 100));
        return attempt(attemptNumber + 1);
      }

      return response.json() as Promise<T>;
    } catch (error) {
      if (attemptNumber >= maxRetries) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, delays[attemptNumber - 1] || 100));
      return attempt(attemptNumber + 1);
    }
  }

  return attempt(1);
}
