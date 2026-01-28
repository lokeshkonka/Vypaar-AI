/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useMemo, useState, useEffect } from "react";
import { inventoryDummy, type InventoryRow } from "../data/inventory-dummy";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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
  isLoading: boolean;
};

const InventoryContext = createContext<InventoryContextType | null>(null);

export function InventoryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [filters, setFiltersState] = useState<InventoryFilters>({});
  const [isUpdating, setIsUpdating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [inventoryData, setInventoryData] = useState<InventoryRow[]>(inventoryDummy);

  // Fetch inventory data from backend
  useEffect(() => {
    const fetchInventory = async () => {
      try {
        setIsLoading(true);
        const res = await fetch(`${BACKEND_URL}/api/inventory/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setInventoryData(data || inventoryDummy);
        }
      } catch (error) {
        console.error("Failed to fetch inventory:", error);
        setInventoryData(inventoryDummy);
      } finally {
        setIsLoading(false);
      }
    };
    fetchInventory();
  }, []);

  const setFilters = (f: Partial<InventoryFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...f }));
  };

  const inventory = useMemo(() => {
    return inventoryData.map((row) => ({
      ...row,
      buffer: row.suggested - row.current,
    })).filter((row) => {
      return (
        (!filters.market || row.market === filters.market) &&
        (!filters.category || row.category === filters.category) &&
        (!filters.product || row.product === filters.product)
      );
    });
  }, [filters, inventoryData]);

  // Update stock via backend
  const updateStock = async () => {
    setIsUpdating(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/inventory/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (res.ok) {
        await res.json();
      }
    } catch (error) {
      console.error("Failed to update stock:", error);
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
        isUpdating,
        updateStock,
        isLoading,
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
