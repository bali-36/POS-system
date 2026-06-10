import { useState, useEffect } from 'react';
import { Save, Store, Percent, DollarSign, Receipt, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getSettings, updateSetting } from '@/services/api';
import type { Setting } from '@/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      for (const setting of settings) {
        await updateSetting(setting.key, setting.value);
      }
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const updateValue = (key: string, value: string) => {
    setSettings((prev) =>
      prev.map((s) => (s.key === key ? { ...s, value } : s))
    );
  };

  const getIcon = (key: string) => {
    switch (key) {
      case 'store_name': return <Store className="h-5 w-5 text-emerald-600" />;
      case 'store_address': return <Store className="h-5 w-5 text-blue-600" />;
      case 'store_phone': return <Store className="h-5 w-5 text-purple-600" />;
      case 'tax_rate': return <Percent className="h-5 w-5 text-amber-600" />;
      case 'currency': return <DollarSign className="h-5 w-5 text-green-600" />;
      case 'receipt_footer': return <Receipt className="h-5 w-5 text-gray-600" />;
      default: return <MessageSquare className="h-5 w-5 text-gray-600" />;
    }
  };

  const getLabel = (key: string) => {
    switch (key) {
      case 'store_name': return 'Store Name';
      case 'store_address': return 'Store Address';
      case 'store_phone': return 'Store Phone';
      case 'tax_rate': return 'Tax Rate (%)';
      case 'currency': return 'Currency Code';
      case 'receipt_footer': return 'Receipt Footer Text';
      default: return key;
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Store Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading settings...</div>
          ) : (
            settings.map((setting) => (
              <div key={setting.key} className="flex items-start gap-4">
                <div className="mt-2">{getIcon(setting.key)}</div>
                <div className="flex-1 space-y-1.5">
                  <label className="text-sm font-medium text-gray-700">
                    {getLabel(setting.key)}
                  </label>
                  <p className="text-xs text-gray-400">{setting.description}</p>
                  <Input
                    value={setting.value}
                    onChange={(e) => updateValue(setting.key, e.target.value)}
                    type={setting.key === 'tax_rate' ? 'number' : 'text'}
                    step={setting.key === 'tax_rate' ? '0.1' : undefined}
                  />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={saving || loading}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
}
