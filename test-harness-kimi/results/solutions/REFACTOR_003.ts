declare function getUser(userId: string, callback: (err: Error | null, user?: any) => void): void;
declare function getOrders(userId: string, callback: (err: Error | null, orders?: any[]) => void): void;
declare function getProducts(orderId: string, callback: (err: Error | null, products?: any) => void): void;

async function loadDashboard(userId: string): Promise<any> {
  const user = await getUserAsync(userId);
  const orders = await getOrdersAsync(user.id);
  const products = await getProductsAsync(orders[0].id);
  return { user, orders, products };
}

function getUserAsync(userId: string): Promise<any> {
  return new Promise((resolve, reject) => {
    getUser(userId, (err, user) => {
      if (err) reject(err);
      else resolve(user);
    });
  });
}

function getOrdersAsync(userId: string): Promise<any[]> {
  return new Promise((resolve, reject) => {
    getOrders(userId, (err, orders) => {
      if (err) reject(err);
      else resolve(orders);
    });
  });
}

function getProductsAsync(orderId: string): Promise<any> {
  return new Promise((resolve, reject) => {
    getProducts(orderId, (err, products) => {
      if (err) reject(err);
      else resolve(products);
    });
  });
}
