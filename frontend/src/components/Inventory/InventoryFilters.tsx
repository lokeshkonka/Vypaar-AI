import CardComponent from "../ui/CardComponent";
import { useInventory } from "../../context/InventoryContext";
import { useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

interface Market {
  id: number;
  name: string;
  state: string;
  city: string;
}

interface Commodity {
  id: number;
  name: string;
  category: string;
}

export default function InventoryFilters() {
  const { filters, setFilters, updateStock, isUpdating } = useInventory();
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [marketsRes, commoditiesRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/markets`),
          fetch(`${BACKEND_URL}/api/commodities`)
        ]);
        
        if (marketsRes.ok) {
          setMarkets(await marketsRes.json());
        }
        if (commoditiesRes.ok) {
          setCommodities(await commoditiesRes.json());
        }
      } catch (error) {
        console.error("Failed to fetch filter data:", error);
      }
    };
    fetchData();
  }, []);

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
          {[...new Set(commodities.map((p) => p.category))].map((c) => (
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
          {commodities.map((p) => (
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
