import { Package } from "lucide-react";
import { products } from "../../../data/dummyData";
import { useForecast } from "../../../context/ForecastContext";

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

export default function ProductSelector() {
  const { selection, setSelection } = useForecast();

  const categories = Array.from(
    new Set(products.map((p) => p.category))
  );

  const filteredProducts = products.filter(
    (p) => p.category === selection.category
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
