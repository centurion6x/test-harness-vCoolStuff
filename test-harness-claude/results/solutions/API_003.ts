async function fetchAllPages<T>(baseUrl: string, headers: Record<string, string>): Promise<T[]> {
  const allItems: T[] = [];
  let cursor: string | null = null;

  while (true) {
    const url = cursor ? `${baseUrl}?cursor=${encodeURIComponent(cursor)}` : baseUrl;
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);

    const page: { data: T[]; next_cursor: string | null } = await res.json();
    allItems.push(...page.data);

    if (!page.next_cursor) break;
    cursor = page.next_cursor;
  }

  return allItems;
}
