async function loadDashboard(userId: string): Promise<any> {
  const user = await getUser(userId);
  const orders = await getOrders(user.id);
  const products = await getProducts(orders[0].id);
  return { user, orders, products };
}
