/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useMemo, useState } from "react";
import { inventoryDummy, type InventoryRow } from "../data/inventory-dummy";

type InventoryFilters = {
  market?: string;
  category?: string;
  product?: string;
};

type InventoryContextType = {
  filters: InventoryFilters;
  setFilters: (f: Partial<InventoryFilters>) => void;
  inventory: InventoryRow[];
  isUpdating: boolean;
  updateStock: () => Promise<void>;
};

const InventoryContext = createContext<InventoryContextType | null>(null);

export function InventoryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [filters, setFiltersState] = useState<InventoryFilters>({});
  const [isUpdating, setIsUpdating] = useState(false);

  const setFilters = (f: Partial<InventoryFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...f }));
  };

  const inventory = useMemo(() => {
    return inventoryDummy.map((row) => ({
      ...row,
      buffer: row.suggested - row.current,
    })).filter((row) => {
      return (
        (!filters.market || row.market === filters.market) &&
        (!filters.category || row.category === filters.category) &&
        (!filters.product || row.product === filters.product)
      );
    });
  }, [filters]);

  // TEMP: Simulated update (backend later)
  const updateStock = async () => {
    setIsUpdating(true);
    await new Promise((r) => setTimeout(r, 1200));
    setIsUpdating(false);
  };

  return (
    <InventoryContext.Provider
      value={{
        filters,
        setFilters,
        inventory,
        isUpdating,
        updateStock,
      }}
    >
      {children}
    </InventoryContext.Provider>
  );
}

export function useInventory() {
  const ctx = useContext(InventoryContext);
  if (!ctx) {
    throw new Error("useInventory must be used inside InventoryProvider");
  }
  return ctx;
}
