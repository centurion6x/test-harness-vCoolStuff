interface PaginatedResponse<T> {
  data: T[];
  next_cursor: string | null;
}

async function fetchAllPages<T>(baseUrl: string, headers: Record<string, string>): Promise<T[]> {
  const allItems: T[] = [];
  let cursor: string | null = null;

  do {
    const url = cursor ? `${baseUrl}?cursor=${cursor}` : baseUrl;
    const response = await fetch(url, { headers });
    const result: PaginatedResponse<T> = await response.json();

    allItems.push(...result.data);
    cursor = result.next_cursor;
  } while (cursor);

  return allItems;
}
