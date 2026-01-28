/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

/* =========================
   TYPES
   ========================= */

export type ForecastSelection = {
  state?: string;
  city?: string;
  market?: string;

  category?: string;
  product?: string;

  forecastRange?: "7" | "14";
};

type ForecastContextType = {
  selection: ForecastSelection;
  setSelection: (data: ForecastSelection) => void;
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

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export function ForecastProvider({ children }: { children: ReactNode }) {
  const [selection, setSelectionState] = useState<ForecastSelection>({});

  /* -------- selection updater -------- */
  const setSelection = (data: ForecastSelection) => {
    setSelectionState((prev) => ({
      ...prev,
      ...data,
    }));
  };

  /* -------- completion guard -------- */
  const isSelectionComplete = useMemo(() => {
    return Boolean(
      selection.state &&
      selection.city &&
      selection.market &&
      selection.category &&
      selection.product &&
      selection.forecastRange
    );
  }, [selection]);

  /* -------- backend integration -------- */
  const generateForecast = async () => {
    if (!isSelectionComplete) {
      throw new Error("Forecast selection incomplete");
    }

    const payload = {
      state: selection.state!,
      city: selection.city!,
      market: selection.market!,
      category: selection.category!,
      product: selection.product!,
      forecastRange: Number(selection.forecastRange),
    };

    try {
      const res = await fetch(`${BACKEND_URL}/api/forecast`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Forecast API failed");
      }

      const data = await res.json();

      // For now just log — later this can be stored in context
      console.log("Forecast response:", data);
    } catch (error) {
      console.error("Forecast generation error:", error);
      throw error;
    }
  };

  return (
    <ForecastContext.Provider
      value={{
        selection,
        setSelection,
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
    throw new Error("useForecast must be used inside ForecastProvider");
  }
  return ctx;
}
