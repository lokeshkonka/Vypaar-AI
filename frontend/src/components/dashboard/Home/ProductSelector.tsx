import { Package } from "lucide-react";
import { useForecast } from "../../../context/ForecastContext";
import { useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

interface Commodity {
  id: number;
  name: string;
}

const inputBase =
  "w-full h-12 rounded-xl px-4 text-sm transition-colors " +
  // Light mode
  "bg-black border border-gray-300 " +
  "hover:border-gray-400 " +
  // Dark mode
  "dark:bg-white/5 dark:border-white/10  " +
  // Focus
  "focus:outline-none focus:ring-2 focus:ring-emerald-400/40 focus:border-emerald-400 " +
  // Disabled
  "disabled:opacity-60 disabled:cursor-not-allowed";

// Commodity categories - grouping commodities
const COMMODITY_CATEGORIES: { [key: string]: string } = {
  "Tomato": "Vegetables",
  "Potato": "Vegetables",
  "Wheat": "Grains",
  "Rice": "Grains",
};

export default function ProductSelector() {
  const { selection, setSelection } = useForecast();
  const [commodities, setCommodities] = useState<Commodity[]>([]);

  useEffect(() => {
    const fetchCommodities = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/commodities`);
        if (res.ok) {
          const data = await res.json();
          setCommodities(data);
        }
      } catch (error) {
        console.error("Failed to fetch commodities:", error);
      }
    };
    fetchCommodities();
  }, []);

  // Get unique categories from commodities that have mappings
  const categories = Array.from(
    new Set(
      commodities
        .map((p) => COMMODITY_CATEGORIES[p.name])
        .filter((c) => c !== undefined)
    )
  ).sort();

  const filteredProducts = commodities.filter(
    (p) => COMMODITY_CATEGORIES[p.name] === selection.category
  );

  return (
    <div className="glass-card p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Package className="w-5 h-5 text-emerald-600" />
        <h3 className="font-medium ">
          Product Configuration
        </h3>
      </div>

      {/* Category */}
      <select
        className={inputBase}
        value={selection.category || ""}
        onChange={(e) =>
          setSelection({
            category: e.target.value,
            product: undefined,
          })
        }
      >
        <option value="">Select Category</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {/* Product */}
      <select
        className={inputBase}
        value={selection.product || ""}
        disabled={!selection.category}
        onChange={(e) =>
          setSelection({
            product: e.target.value,
          })
        }
      >
        <option value="">Select Product</option>
        {filteredProducts.map((p) => (
          <option key={p.id} value={p.name}>
            {p.name}
          </option>
        ))}
      </select>
    </div>
  );
}
