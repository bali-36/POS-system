import { useState, useEffect } from 'react';
import { AlertTriangle, Package, ArrowDown, ArrowUp, History, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getProducts, getInventoryLogs } from '@/services/api';
import type { Product, InventoryLog } from '@/types';

export default function Inventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [logs, setLogs] = useState<InventoryLog[]>([]);
  const [view, setView] = useState<'stock' | 'logs'>('stock');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [productsData, logsData] = await Promise.all([
        getProducts({ low_stock: false }),
        getInventoryLogs(),
      ]);
      setProducts(productsData);
      setLogs(logsData);
    } catch (error) {
      console.error('Error loading inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const lowStockProducts = products.filter(
    (p) => p.quantity <= p.min_stock_level && p.is_active === 1
  );

  const getStockStatus = (product: Product) => {
    if (product.quantity === 0) return { label: 'Out of Stock', color: 'bg-red-100 text-red-700' };
    if (product.quantity <= product.min_stock_level) return { label: 'Low Stock', color: 'bg-amber-100 text-amber-700' };
    if (product.quantity <= product.min_stock_level * 2) return { label: 'Medium', color: 'bg-blue-100 text-blue-700' };
    return { label: 'In Stock', color: 'bg-green-100 text-green-700' };
  };

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'sale': return <ArrowDown className="h-4 w-4 text-red-500" />;
      case 'adjustment': return <ArrowUp className="h-4 w-4 text-emerald-500" />;
      case 'initial': return <Package className="h-4 w-4 text-blue-500" />;
      default: return <RefreshCw className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
                <Package className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{products.filter(p => p.quantity > p.min_stock_level).length}</p>
                <p className="text-xs text-gray-500">Well Stocked</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{lowStockProducts.length}</p>
                <p className="text-xs text-gray-500">Low Stock Items</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <History className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{logs.length}</p>
                <p className="text-xs text-gray-500">Recent Movements</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setView('stock')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            view === 'stock'
              ? 'bg-emerald-600 text-white'
              : 'bg-white border text-gray-600 hover:bg-gray-50'
          }`}
        >
          Stock Levels
        </button>
        <button
          onClick={() => setView('logs')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            view === 'logs'
              ? 'bg-emerald-600 text-white'
              : 'bg-white border text-gray-600 hover:bg-gray-50'
          }`}
        >
          Movement History
        </button>
      </div>

      {view === 'stock' ? (
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Current Stock Levels</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Product</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">SKU</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">Current Stock</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">Min Level</th>
                    <th className="text-center py-3 px-4 font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-400">Loading...</td></tr>
                  ) : products.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-400">No products</td></tr>
                  ) : (
                    products.map((product) => {
                      const status = getStockStatus(product);
                      return (
                        <tr key={product.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium text-gray-900">{product.name}</td>
                          <td className="py-3 px-4 text-gray-500">{product.sku}</td>
                          <td className="py-3 px-4 text-right">
                            <span className={product.quantity <= product.min_stock_level ? 'text-red-600 font-medium' : ''}>
                              {product.quantity} {product.unit}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">{product.min_stock_level}</td>
                          <td className="py-3 px-4 text-center">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${status.color}`}>
                              {status.label}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Inventory Movement History</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Type</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Product</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">Qty</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">Previous</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">New</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Notes</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan={7} className="text-center py-8 text-gray-400">Loading...</td></tr>
                  ) : logs.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-8 text-gray-400">No records</td></tr>
                  ) : (
                    logs.map((log) => (
                      <tr key={log.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            {getLogIcon(log.type)}
                            <span className="capitalize text-gray-600">{log.type}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 font-medium text-gray-900">{log.product_name}</td>
                        <td className="py-3 px-4 text-right text-gray-600">{log.quantity}</td>
                        <td className="py-3 px-4 text-right text-gray-500">{log.previous_stock}</td>
                        <td className="py-3 px-4 text-right font-medium">{log.new_stock}</td>
                        <td className="py-3 px-4 text-gray-500">{log.notes || '-'}</td>
                        <td className="py-3 px-4 text-gray-500 text-xs">
                          {new Date(log.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
