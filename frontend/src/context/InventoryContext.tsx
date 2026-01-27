/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useForecast } from "./ForecastContext";
import {
  inventoryDummy,
  type InventoryRow,
} from "../data/inventory-dummy";

import type { ProductCategory } from "../data/forecast-dummy";

/* =========================
   TYPES
   ========================= */

type InventoryFilters = {
  market?: string;
  category?: ProductCategory;
  product?: string;
};

type InventoryContextType = {
  filters: InventoryFilters;
  setFilters: (f: Partial<InventoryFilters>) => void;

  inventory: InventoryRow[];

  updateStock: () => Promise<void>;
  isUpdating: boolean;
};

/* =========================
   CONTEXT
   ========================= */

const InventoryContext =
  createContext<InventoryContextType | null>(null);

/* =========================
   PROVIDER
   ========================= */

export function InventoryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { selection } = useForecast();

  const [filters, setFiltersState] =
    useState<InventoryFilters>({});

  const [isUpdating, setIsUpdating] = useState(false);

  /* ---------------------------
     Sync from ForecastContext
     --------------------------- */
  useEffect(() => {
    setFiltersState((prev) => ({
      ...prev,
      market: selection.market ?? prev.market,
      category: selection.category ?? prev.category,
      product: selection.product ?? prev.product,
    }));
  }, [selection.market, selection.category, selection.product]);

  /* ---------------------------
     Filter updater
     --------------------------- */
  const setFilters = (f: Partial<InventoryFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...f }));
  };

  /* ---------------------------
     Derived inventory
     --------------------------- */
  const inventory = useMemo(() => {
    return inventoryDummy.filter((row) => {
      return (
        (!filters.market || row.market === filters.market) &&
        (!filters.category ||
          row.category === filters.category) &&
        (!filters.product ||
          row.product === filters.product)
      );
    });
  }, [filters]);

  /* ---------------------------
     Update stock (backend)
     --------------------------- */
  const updateStock = async () => {
    try {
      setIsUpdating(true);

      /*
      await fetch(`${BACKEND_URL}/api/inventory/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filters,
          items: inventory,
        }),
      });
      */

      // TEMP: simulate API delay
      await new Promise((r) => setTimeout(r, 1200));
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <InventoryContext.Provider
      value={{
        filters,
        setFilters,
        inventory,
        updateStock,
        isUpdating,
      }}
    >
      {children}
    </InventoryContext.Provider>
  );
}

/* =========================
   HOOK
   ========================= */

export function useInventory() {
  const ctx = useContext(InventoryContext);
  if (!ctx) {
    throw new Error(
      "useInventory must be used inside InventoryProvider"
    );
  }
  return ctx;
}
