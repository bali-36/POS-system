export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  phone?: string;
  role: 'admin' | 'cashier';
  is_active: number;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  sku: string;
  barcode?: string;
  category_id?: number;
  category_name?: string;
  price: number;
  cost_price: number;
  quantity: number;
  min_stock_level: number;
  unit: string;
  is_active: number;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  loyalty_points: number;
  is_active: number;
  created_at: string;
}

export interface OrderItem {
  id?: number;
  order_id?: number;
  product_id: number;
  product_name?: string;
  sku?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id?: number;
  customer_name?: string;
  user_id: number;
  user_name?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_method: string;
  payment_status: string;
  status: string;
  notes?: string;
  items?: OrderItem[];
  created_at: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface DashboardStats {
  total_products: number;
  total_customers: number;
  orders_today: number;
  sales_today: number;
  low_stock_count: number;
  total_revenue: number;
}

export interface SalesChartData {
  date: string;
  total: number;
  orders: number;
}

export interface InventoryLog {
  id: number;
  product_id: number;
  product_name?: string;
  type: string;
  quantity: number;
  previous_stock: number;
  new_stock: number;
  notes?: string;
  created_at: string;
}

export interface Setting {
  id: number;
  key: string;
  value: string;
  description?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}
