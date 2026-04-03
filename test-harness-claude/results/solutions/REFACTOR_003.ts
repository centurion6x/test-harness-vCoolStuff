async function loadDashboard(userId: string): Promise<{ user: any; orders: any; products: any }> {
  try {
    const user = await getUser(userId);
    const orders = await getOrders(user.id);
    const products = await getProducts(orders[0].id);
    return { user, orders, products };
  } catch (err) {
    throw err;
  }
}
