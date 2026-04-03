interface User {
  id: string;
}

interface Order {
  id: string;
}

interface Product {
  // product fields
}

interface DashboardData {
  user: User;
  orders: Order[];
  products: Product[];
}

async function loadDashboard(userId: string): Promise<DashboardData> {
  const user = await getUser(userId);
  const orders = await getOrders(user.id);
  const products = await getProducts(orders[0].id);
  return { user, orders, products };
}
