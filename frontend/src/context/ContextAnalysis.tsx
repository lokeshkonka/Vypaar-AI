/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";
import type { AnalysisContextValue } from "./types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function ContextAnalysisProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [analysis, setAnalysis] = useState<AnalysisContextValue>({
    selectorData: { market: "", product: "", forecastRange: "" },
    stockMetrics: { predictedDemand: 0, stockNeeded: 0, overstockRisk: 0, understockRisk: 0 },
    demandGraphData: [],
    impactData: { festival: [], weather: [] },
    recommendationTable: [],
  });

  // Fetch product analysis from backend
  useEffect(() => {
    const fetchProductAnalysis = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/product-analysis`);
        if (res.ok) {
          const data = await res.json();
          setAnalysis(data);
        } else {
          console.error("Failed to fetch product analysis:", res.status);
        }
      } catch (error) {
        console.error("Failed to fetch product analysis:", error);
      }
    };
    fetchProductAnalysis();
  }, []);

  const value: AnalysisContextValue = {
    ...analysis,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useContextAnalysis(): AnalysisContextValue {
  const ctx = useContext(AnalysisContext);
  if (!ctx) {
    throw new Error(
      "useContextAnalysis must be used inside ContextAnalysisProvider"
    );
  }
  return ctx;
}
