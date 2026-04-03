async function fetchAllPages<T>(baseUrl: string, headers: Record<string, string>): Promise<T[]> {
  const allItems: T[] = [];
  let cursor: string | null = null;
  let url = baseUrl;

  while (true) {
    const fetchUrl = cursor ? `${baseUrl}?cursor=${cursor}` : baseUrl;
    const res = await fetch(fetchUrl, { headers });
    const { data, next_cursor } = await res.json();

    allItems.push(...data);

    if (next_cursor === null) {
      break;
    }

    cursor = next_cursor;
  }

  return allItems;
}
