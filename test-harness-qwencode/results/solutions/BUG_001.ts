function getPaginationMeta(totalItems: number, pageSize: number, currentPage: number) {
  const totalPages = Math.ceil(totalItems / pageSize);
  const hasNextPage = currentPage < totalPages;
  const hasPrevPage = currentPage > 1;
  const startItem = (currentPage - 1) * pageSize;
  const endItem = Math.min(startItem + pageSize, totalItems);
  return { totalPages, hasNextPage, hasPrevPage, startItem, endItem };
}
