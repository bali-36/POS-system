import { useState, useEffect, useRef } from 'react';
import {
  Search,
  Plus,
  Minus,
  Trash2,
  Receipt,
  User,
  CreditCard,
  Banknote,
  QrCode,
  Check,
  Printer,
  ShoppingBag,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { getProducts, getProductByBarcode, getCustomers, createOrder } from '@/services/api';
import type { Product, Customer, CartItem } from '@/types';

export default function POS() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [barcodeInput, setBarcodeInput] = useState('');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [showCustomerDialog, setShowCustomerDialog] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);
  const [lastOrder, setLastOrder] = useState<any>(null);
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [discount, setDiscount] = useState(0);
  const [taxRate] = useState(8.5);
  const [loading, setLoading] = useState(false);
  const barcodeRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadProducts();
    loadCustomers();
    // Focus barcode input on load
    barcodeRef.current?.focus();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data.filter((p: Product) => p.is_active === 1));
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Error loading customers:', error);
    }
  };

  const filteredProducts = products.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.barcode?.includes(searchQuery)
  );

  const addToCart = (product: Product) => {
    if (product.quantity <= 0) return;
    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        if (existing.quantity >= product.quantity) return prev;
        return prev.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  };

  const updateQuantity = (productId: number, delta: number) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.product.id === productId) {
            const newQty = item.quantity + delta;
            if (newQty <= 0) return null;
            if (newQty > item.product.quantity) return item;
            return { ...item, quantity: newQty };
          }
          return item;
        })
        .filter(Boolean) as CartItem[]
    );
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
  };

  const handleBarcodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!barcodeInput.trim()) return;
    try {
      const product = await getProductByBarcode(barcodeInput.trim());
      if (product) {
        addToCart(product);
        setBarcodeInput('');
      }
    } catch (error) {
      // Product not found
    }
  };

  const subtotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const taxAmount = subtotal * (taxRate / 100);
  const total = subtotal + taxAmount - discount;

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    setLoading(true);

    const user = JSON.parse(localStorage.getItem('pos_user') || '{}');

    try {
      const orderData = {
        customer_id: selectedCustomer?.id,
        user_id: user.id || 1,
        items: cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price,
          total_price: item.product.price * item.quantity,
        })),
        subtotal,
        tax_amount: taxAmount,
        discount_amount: discount,
        total_amount: total,
        payment_method: paymentMethod,
      };

      const result = await createOrder(orderData);
      if (result.success) {
        setLastOrder(result.order);
        setShowReceipt(true);
        setCart([]);
        setSelectedCustomer(null);
        setDiscount(0);
        loadProducts();
      }
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-[calc(100vh-100px)]">
      {/* Left: Product Selection */}
      <div className="flex-1 flex flex-col gap-4 min-w-0">
        {/* Barcode & Search */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4 space-y-3">
            <form onSubmit={handleBarcodeSubmit} className="flex gap-2">
              <div className="relative flex-1">
                <QrCode className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  ref={barcodeRef}
                  placeholder="Scan barcode or enter SKU..."
                  value={barcodeInput}
                  onChange={(e) => setBarcodeInput(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button type="submit" size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                <Plus className="h-4 w-4" />
              </Button>
            </form>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search products by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Products Grid */}
        <Card className="border-0 shadow-sm flex-1 overflow-hidden">
          <CardHeader className="pb-2 py-3 px-4">
            <CardTitle className="text-sm font-medium text-gray-500">
              {filteredProducts.length} Products Available
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 overflow-y-auto" style={{ maxHeight: 'calc(100% - 50px)' }}>
            <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-3">
              {filteredProducts.map((product) => (
                <button
                  key={product.id}
                  onClick={() => addToCart(product)}
                  disabled={product.quantity <= 0}
                  className={`p-3 rounded-lg border text-left transition-all hover:shadow-md ${
                    product.quantity <= 0
                      ? 'opacity-50 cursor-not-allowed bg-gray-50'
                      : 'bg-white hover:border-emerald-300 cursor-pointer'
                  }`}
                >
                  <p className="font-medium text-sm text-gray-900 line-clamp-2">{product.name}</p>
                  <p className="text-xs text-gray-500 mt-1">{product.sku}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="font-bold text-emerald-600">
                      {formatCurrency(product.price)}
                    </span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      product.quantity <= product.min_stock_level
                        ? 'bg-red-100 text-red-600'
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {product.quantity} left
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right: Cart */}
      <div className="w-full lg:w-96 flex flex-col gap-4">
        <Card className="border-0 shadow-sm flex-1 flex flex-col overflow-hidden">
          <CardHeader className="pb-2 py-3 px-4 border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Receipt className="h-4 w-4" />
                Cart ({cart.reduce((sum, item) => sum + item.quantity, 0)} items)
              </CardTitle>
              {cart.length > 0 && (
                <button
                  onClick={() => setCart([])}
                  className="text-xs text-red-500 hover:text-red-700"
                >
                  Clear
                </button>
              )}
            </div>
          </CardHeader>

          {/* Customer Selection */}
          <div className="px-4 py-2 border-b bg-gray-50">
            <button
              onClick={() => setShowCustomerDialog(true)}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-emerald-600 transition-colors"
            >
              <User className="h-4 w-4" />
              {selectedCustomer ? selectedCustomer.name : 'Select Customer (Optional)'}
            </button>
          </div>

          {/* Cart Items */}
          <CardContent className="p-0 flex-1 overflow-y-auto">
            {cart.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-gray-400">
                <ShoppingBag className="h-10 w-10 mb-2" />
                <p className="text-sm">Cart is empty</p>
                <p className="text-xs">Add products to get started</p>
              </div>
            ) : (
              <div className="divide-y">
                {cart.map((item) => (
                  <div key={item.product.id} className="p-3 flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-gray-900 truncate">
                        {item.product.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatCurrency(item.product.price)} / {item.product.unit}
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => updateQuantity(item.product.id, -1)}
                        className="p-1 rounded hover:bg-gray-100"
                      >
                        <Minus className="h-3 w-3" />
                      </button>
                      <span className="w-8 text-center text-sm font-medium">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.product.id, 1)}
                        className="p-1 rounded hover:bg-gray-100"
                      >
                        <Plus className="h-3 w-3" />
                      </button>
                    </div>
                    <div className="text-right min-w-[70px]">
                      <p className="font-medium text-sm">
                        {formatCurrency(item.product.price * item.quantity)}
                      </p>
                    </div>
                    <button
                      onClick={() => removeFromCart(item.product.id)}
                      className="p-1 rounded hover:bg-red-50 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>

          {/* Cart Summary */}
          {cart.length > 0 && (
            <div className="border-t p-4 space-y-3 bg-gray-50">
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Subtotal</span>
                  <span>{formatCurrency(subtotal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Tax ({taxRate}%)</span>
                  <span>{formatCurrency(taxAmount)}</span>
                </div>
                {discount > 0 && (
                  <div className="flex justify-between text-red-600">
                    <span>Discount</span>
                    <span>-{formatCurrency(discount)}</span>
                  </div>
                )}
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total</span>
                  <span className="text-emerald-600">{formatCurrency(total)}</span>
                </div>
              </div>

              {/* Payment Method */}
              <div className="flex gap-2">
                <button
                  onClick={() => setPaymentMethod('cash')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                    paymentMethod === 'cash'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-white border text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Banknote className="h-4 w-4" />
                  Cash
                </button>
                <button
                  onClick={() => setPaymentMethod('card')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                    paymentMethod === 'card'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-white border text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <CreditCard className="h-4 w-4" />
                  Card
                </button>
              </div>

              <Button
                onClick={handleCheckout}
                disabled={loading || cart.length === 0}
                className="w-full bg-emerald-600 hover:bg-emerald-700 h-11 text-base"
              >
                {loading ? 'Processing...' : `Charge ${formatCurrency(total)}`}
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* Customer Selection Dialog */}
      <Dialog open={showCustomerDialog} onOpenChange={setShowCustomerDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Select Customer</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            <button
              onClick={() => {
                setSelectedCustomer(null);
                setShowCustomerDialog(false);
              }}
              className={`w-full p-3 rounded-lg border text-left transition-colors ${
                !selectedCustomer ? 'border-emerald-500 bg-emerald-50' : 'hover:bg-gray-50'
              }`}
            >
              <p className="font-medium">Walk-in Customer</p>
              <p className="text-xs text-gray-500">No customer selected</p>
            </button>
            {customers.map((customer) => (
              <button
                key={customer.id}
                onClick={() => {
                  setSelectedCustomer(customer);
                  setShowCustomerDialog(false);
                }}
                className={`w-full p-3 rounded-lg border text-left transition-colors ${
                  selectedCustomer?.id === customer.id
                    ? 'border-emerald-500 bg-emerald-50'
                    : 'hover:bg-gray-50'
                }`}
              >
                <p className="font-medium">{customer.name}</p>
                <p className="text-xs text-gray-500">
                  {customer.phone} {customer.loyalty_points ? `- ${customer.loyalty_points} pts` : ''}
                </p>
              </button>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      {/* Receipt Dialog */}
      <Dialog open={showReceipt} onOpenChange={setShowReceipt}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-center flex items-center justify-center gap-2">
              <Check className="h-5 w-5 text-emerald-600" />
              Order Complete
            </DialogTitle>
          </DialogHeader>
          {lastOrder && (
            <div className="space-y-4">
              <div className="text-center border-b pb-4">
                <p className="text-2xl font-bold text-emerald-600">
                  {formatCurrency(lastOrder.total_amount)}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Order #{lastOrder.order_number}
                </p>
                <p className="text-xs text-gray-400">
                  {new Date(lastOrder.created_at).toLocaleString()}
                </p>
              </div>

              <div className="space-y-2 text-sm">
                {lastOrder.items?.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between">
                    <span>
                      {item.product_name} x{item.quantity}
                    </span>
                    <span>{formatCurrency(item.total_price)}</span>
                  </div>
                ))}
              </div>

              <div className="border-t pt-3 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Subtotal</span>
                  <span>{formatCurrency(lastOrder.subtotal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Tax</span>
                  <span>{formatCurrency(lastOrder.tax_amount)}</span>
                </div>
                <div className="flex justify-between font-bold text-base pt-1">
                  <span>Total</span>
                  <span>{formatCurrency(lastOrder.total_amount)}</span>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Payment</span>
                  <span className="capitalize">{lastOrder.payment_method}</span>
                </div>
              </div>

              <Button
                onClick={() => setShowReceipt(false)}
                className="w-full bg-emerald-600 hover:bg-emerald-700"
              >
                <Printer className="h-4 w-4 mr-2" />
                Print Receipt
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
