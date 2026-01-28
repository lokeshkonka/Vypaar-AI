/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  forecastDummy,
  type ProductCategory,
  type ForecastRangeValue,
} from "../data/forecast-dummy";

/* =========================
   TYPES
   ========================= */

export type ForecastSelection = {
  state?: string;
  city?: string;
  marketType?: string;
  market?: string;

  category?: ProductCategory;
  product?: string;

  forecastRange?: ForecastRangeValue;
};

type ForecastContextType = {
  /* Selection */
  selection: ForecastSelection;
  setSelection: (data: Partial<ForecastSelection>) => void;

  /* Reference data (from backend/dummy) */
  markets: typeof forecastDummy.markets;
  products: typeof forecastDummy.products;
  categories: ProductCategory[];
  forecastRanges: typeof forecastDummy.forecastRanges;

  /* Actions */
  generateForecast: () => Promise<void>;
  isSelectionComplete: boolean;
};

/* =========================
   CONTEXT
   ========================= */

const ForecastContext = createContext<ForecastContextType | null>(null);

/* =========================
   PROVIDER
   ========================= */

export function ForecastProvider({ children }: { children: ReactNode }) {
  const [selection, setSelectionState] =
    useState<ForecastSelection>({});

  const setSelection = (data: Partial<ForecastSelection>) => {
    setSelectionState((prev) => ({ ...prev, ...data }));
  };

  const categories = useMemo(() => {
    return Array.from(
      new Set(
        forecastDummy.products.map((p) => p.category)
      )
    );
  }, []);

  const isSelectionComplete = useMemo(() => {
    return Boolean(
      selection.state &&
      selection.city &&
      selection.marketType &&
      selection.market &&
      selection.category &&
      selection.product &&
      selection.forecastRange
    );
  }, [selection]);

  /* -------- backend integration (commented) -------- */
  const generateForecast = async () => {
    /*
    await fetch(`${BACKEND_URL}/api/forecast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selection),
    });
    */
    console.log("Forecast payload:", selection);
  };

  return (
    <ForecastContext.Provider
      value={{
        selection,
        setSelection,

        markets: forecastDummy.markets,
        products: forecastDummy.products,
        categories,
        forecastRanges: forecastDummy.forecastRanges,

        generateForecast,
        isSelectionComplete,
      }}
    >
      {children}
    </ForecastContext.Provider>
  );
}

/* =========================
   HOOK
   ========================= */

export function useForecast() {
  const ctx = useContext(ForecastContext);
  if (!ctx) {
    throw new Error(
      "useForecast must be used inside ForecastProvider"
    );
  }
  return ctx;
}
