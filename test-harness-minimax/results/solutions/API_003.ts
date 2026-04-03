interface PaginatedResponse<T> {
  data: T[];
  next_cursor: string | null;
}

async function fetchAllPages<T>(baseUrl: string, headers: Record<string, string>): Promise<T[]> {
  const allItems: T[] = [];
  let cursor: string | null = null;

  do {
    const url = cursor
      ? `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}cursor=${cursor}`
      : baseUrl;

    const res = await fetch(url, { headers });

    if (!res.ok) {
      throw new Error(`Failed to fetch: ${res.status}`);
    }

    const response: PaginatedResponse<T> = await res.json();
    allItems.push(...response.data);
    cursor = response.next_cursor;
  } while (cursor !== null);

  return allItems;
}
