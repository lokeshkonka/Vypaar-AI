/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext } from "react";
import {
  selectorData,
  stockMetrics,
  demandGraphData,
  impactData,
  recommendationTable,
} from "../data/dummy-product";

import type { AnalysisContextValue } from "./types";

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function ContextAnalysisProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  /*
  const fetchProductAnalysis = async () => {
    const res = await fetch(`${BACKEND_URL}/api/product-analysis`);
    return await res.json();
  };
  */

  const value: AnalysisContextValue = {
    selectorData,
    stockMetrics,
    demandGraphData,
    impactData,
    recommendationTable,
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
