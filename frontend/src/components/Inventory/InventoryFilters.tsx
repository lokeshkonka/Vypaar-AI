import CardComponent from "../ui/CardComponent";
import { useInventory } from "../../context/InventoryContext";
import { markets, products } from "../../data/dummyData";

export default function InventoryFilters() {
  const { filters, setFilters, updateStock, isUpdating } = useInventory();

  return (
    <CardComponent title="Filter Inventory">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <select
          className="border px-3 py-2 text-sm"
          value={filters.market ?? ""}
          onChange={(e) =>
            setFilters({ market: e.target.value || undefined })
          }
        >
          <option value="">All Markets</option>
          {markets.map((m) => (
            <option key={m.id} value={m.name}>
              {m.name}
            </option>
          ))}
        </select>

        <select
          className="border px-3 py-2 text-sm"
          value={filters.category ?? ""}
          onChange={(e) =>
            setFilters({ category: e.target.value || undefined })
          }
        >
          <option value="">All Categories</option>
          {[...new Set(products.map((p) => p.category))].map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          className="border px-3 py-2 text-sm"
          value={filters.product ?? ""}
          onChange={(e) =>
            setFilters({ product: e.target.value || undefined })
          }
        >
          <option value="">All Products</option>
          {products.map((p) => (
            <option key={p.id} value={p.name}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={updateStock}
        disabled={isUpdating}
        className="
          mt-4 w-full
          px-4 py-3 text-sm font-medium
          bg-emerald-600 dark:text-white text-black hover:bg-emerald-700 hover:shadow-[0_12px_30px_rgba(16,185,129,0.35)] active:scale-[0.98]
          disabled:opacity-50
        "
      >
        {isUpdating ? "Updating Stock…" : "Update Stock"}
      </button>
    </CardComponent>
  );
}
