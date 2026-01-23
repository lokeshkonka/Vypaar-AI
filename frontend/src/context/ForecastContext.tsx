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
  marketType?: string;
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

export function ForecastProvider({ children }: { children: ReactNode }) {
  const [selection, setSelectionState] = useState<ForecastSelection>({});

  const setSelection = (data: ForecastSelection) => {
    setSelectionState((prev) => ({
      ...prev,
      ...data,
    }));
  };

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

  const generateForecast = async () => {
    if (!isSelectionComplete) {
      throw new Error("Forecast selection incomplete");
    }

    // 🔒 backend call goes here later
    console.log("Generating forecast with:", selection);
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


export function useForecast() {
  const ctx = useContext(ForecastContext);
  if (!ctx) {
    throw new Error("useForecast must be used inside ForecastProvider");
  }
  return ctx;
}
