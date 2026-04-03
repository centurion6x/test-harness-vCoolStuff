function getUser(userId: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // Existing callback implementation wrapped in Promise
  });
}

function getOrders(userId: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // Existing callback implementation wrapped in Promise
  });
}

function getProducts(orderId: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // Existing callback implementation wrapped in Promise
  });
}

async function loadDashboard(userId: string): Promise<any> {
  const user = await getUser(userId);
  const orders = await getOrders(user.id);
  const products = await getProducts(orders[0].id);
  return { user, orders, products };
}
