declare function fetch(url: string, options?: any): Promise<any>;

async function fetchAllPages<T>(
  baseUrl: string,
  headers: Record<string, string>
): Promise<T[]> {
  const results: T[] = [];
  let cursor: string | null = null;

  while (true) {
    const url = cursor
      ? `${baseUrl}?cursor=${encodeURIComponent(cursor)}`
      : baseUrl;

    const res = await fetch(url, { headers });
    const data: { data: T[]; next_cursor: string | null } = await res.json();

    results.push(...data.data);

    if (data.next_cursor === null) {
      break;
    }

    cursor = data.next_cursor;
  }

  return results;
}
