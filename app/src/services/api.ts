import axios from 'axios';
import type { User, Category, Product, Customer, LoginCredentials } from '@/types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth
export const login = async (credentials: LoginCredentials) => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

// Users
export const getUsers = async () => {
  const response = await api.get('/users');
  return response.data;
};

export const createUser = async (data: Partial<User>) => {
  const response = await api.post('/users', data);
  return response.data;
};

export const updateUser = async (id: number, data: Partial<User>) => {
  const response = await api.put(`/users/${id}`, data);
  return response.data;
};

export const deleteUser = async (id: number) => {
  const response = await api.delete(`/users/${id}`);
  return response.data;
};

// Categories
export const getCategories = async () => {
  const response = await api.get('/categories');
  return response.data;
};

export const createCategory = async (data: Partial<Category>) => {
  const response = await api.post('/categories', data);
  return response.data;
};

export const updateCategory = async (id: number, data: Partial<Category>) => {
  const response = await api.put(`/categories/${id}`, data);
  return response.data;
};

export const deleteCategory = async (id: number) => {
  const response = await api.delete(`/categories/${id}`);
  return response.data;
};

// Products
export const getProducts = async (params?: { search?: string; category_id?: number; low_stock?: boolean }) => {
  const response = await api.get('/products', { params });
  return response.data;
};

export const getProduct = async (id: number) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

export const getProductByBarcode = async (barcode: string) => {
  const response = await api.get(`/products/barcode/${barcode}`);
  return response.data;
};

export const createProduct = async (data: Partial<Product>) => {
  const response = await api.post('/products', data);
  return response.data;
};

export const updateProduct = async (id: number, data: Partial<Product>) => {
  const response = await api.put(`/products/${id}`, data);
  return response.data;
};

export const deleteProduct = async (id: number) => {
  const response = await api.delete(`/products/${id}`);
  return response.data;
};

// Customers
export const getCustomers = async (search?: string) => {
  const response = await api.get('/customers', { params: { search } });
  return response.data;
};

export const getCustomer = async (id: number) => {
  const response = await api.get(`/customers/${id}`);
  return response.data;
};

export const createCustomer = async (data: Partial<Customer>) => {
  const response = await api.post('/customers', data);
  return response.data;
};

export const updateCustomer = async (id: number, data: Partial<Customer>) => {
  const response = await api.put(`/customers/${id}`, data);
  return response.data;
};

export const deleteCustomer = async (id: number) => {
  const response = await api.delete(`/customers/${id}`);
  return response.data;
};

// Orders
export const getOrders = async (limit?: number, offset?: number) => {
  const response = await api.get('/orders', { params: { limit, offset } });
  return response.data;
};

export const getOrder = async (id: number) => {
  const response = await api.get(`/orders/${id}`);
  return response.data;
};

export const createOrder = async (data: {
  customer_id?: number;
  user_id: number;
  items: { product_id: number; quantity: number; unit_price: number; total_price: number }[];
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_method: string;
  notes?: string;
}) => {
  const response = await api.post('/orders', data);
  return response.data;
};

export const deleteOrder = async (id: number) => {
  const response = await api.delete(`/orders/${id}`);
  return response.data;
};

// Dashboard
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const getSalesChart = async (period: string = 'week') => {
  const response = await api.get('/dashboard/sales-chart', { params: { period } });
  return response.data;
};

export const getTopProducts = async (limit: number = 5) => {
  const response = await api.get('/dashboard/top-products', { params: { limit } });
  return response.data;
};

export const getCategorySales = async () => {
  const response = await api.get('/dashboard/category-sales');
  return response.data;
};

export const getInventoryLogs = async (limit: number = 50) => {
  const response = await api.get('/dashboard/inventory-logs', { params: { limit } });
  return response.data;
};

// Settings
export const getSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

export const updateSetting = async (key: string, value: string) => {
  const response = await api.put(`/settings/${key}`, { value });
  return response.data;
};

export default api;
