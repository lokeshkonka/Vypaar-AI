import React, { useState, useEffect } from "react";
import { useBuySellAlerts } from "../../context/BuySellAlertContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

interface Commodity {
  id: number;
  name: string;
  category: string;
}

interface Market {
  id: number;
  name: string;
  state: string;
}

interface CreateAlertFormProps {
  onSuccess?: () => void;
}

export default function CreateAlertForm({ onSuccess }: CreateAlertFormProps) {
  const { createAlert, fetchAlerts } = useBuySellAlerts();
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    commodity_id: "",
    market_id: "",
    buy_threshold: "",
    sell_threshold: "",
    priority: "MEDIUM",
    notification_channels: ["in_app"],
    message: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log("Fetching commodities and markets from:", BACKEND_URL);
        const [commodRes, marketsRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/v1/market-data/commodities?limit=100`),
          fetch(`${BACKEND_URL}/api/v1/market-data/markets?limit=100`),
        ]);

        console.log("Commodities response status:", commodRes.status);
        console.log("Markets response status:", marketsRes.status);

        if (commodRes.ok) {
          const data = await commodRes.json();
          console.log("Commodities data:", data);
          // Handle both array and wrapped response
          const commArray = Array.isArray(data) ? data : (data.data || data.commodities || []);
          setCommodities(commArray);
        }
        if (marketsRes.ok) {
          const data = await marketsRes.json();
          console.log("Markets data:", data);
          // Handle both array and wrapped response
          const mktArray = Array.isArray(data) ? data : (data.data || data.markets || []);
          setMarkets(mktArray);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };

    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Validation
      if (!formData.commodity_id || !formData.market_id) {
        throw new Error("Please select commodity and market");
      }

      const buyThreshold = parseFloat(formData.buy_threshold);
      const sellThreshold = parseFloat(formData.sell_threshold);

      if (isNaN(buyThreshold) || isNaN(sellThreshold)) {
        throw new Error("Please enter valid prices");
      }

      if (buyThreshold >= sellThreshold) {
        throw new Error("Buy threshold must be less than sell threshold");
      }

      await createAlert({
        commodity_id: parseInt(formData.commodity_id),
        market_id: parseInt(formData.market_id),
        buy_threshold: buyThreshold,
        sell_threshold: sellThreshold,
        priority: formData.priority,
        notification_channels: formData.notification_channels,
        message: formData.message || undefined,
        enabled: true,
      });

      // Reset form
      setFormData({
        commodity_id: "",
        market_id: "",
        buy_threshold: "",
        sell_threshold: "",
        priority: "MEDIUM",
        notification_channels: ["in_app"],
        message: "",
      });

      await fetchAlerts();
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create alert");
      console.error("Error creating alert:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
    >
      <h3 className="text-lg font-semibold mb-6 text-gray-900 dark:text-white">
        Create Buy/Sell Alert
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded text-red-700 dark:text-red-100 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Commodity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Commodity *
          </label>
          <select
            value={formData.commodity_id}
            onChange={(e) => setFormData({ ...formData, commodity_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          >
            <option value="">Select commodity</option>
            {commodities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Market */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Market *
          </label>
          <select
            value={formData.market_id}
            onChange={(e) => setFormData({ ...formData, market_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          >
            <option value="">Select market</option>
            {markets.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.state})
              </option>
            ))}
          </select>
        </div>

        {/* Buy Threshold */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Buy Threshold (₹) *
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.buy_threshold}
            onChange={(e) => setFormData({ ...formData, buy_threshold: e.target.value })}
            placeholder="Price at which to trigger BUY"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />
        </div>

        {/* Sell Threshold */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sell Threshold (₹) *
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.sell_threshold}
            onChange={(e) => setFormData({ ...formData, sell_threshold: e.target.value })}
            placeholder="Price at which to trigger SELL"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Priority
          </label>
          <select
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {/* Message */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Alert Message (Optional)
        </label>
        <textarea
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          placeholder="Custom message for this alert"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600 text-white font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
      >
        {isLoading ? "Creating..." : "Create Alert"}
      </button>
    </form>
  );
}
