/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext } from "react";
import { insightDummy, type InsightItem } from "../data/insight-dummy";

interface InsightContextValue {
  insights: InsightItem[];
}

const InsightContext = createContext<InsightContextValue | null>(null);

export function InsightProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  /*
  // 🔒 BACKEND INTEGRATION (COMMENTED)
  const fetchInsights = async () => {
    const res = await fetch(`${BACKEND_URL}/api/ai/insights`);
    return await res.json();
  };
  */

  const value: InsightContextValue = {
    insights: insightDummy,
  };

  return (
    <InsightContext.Provider value={value}>
      {children}
    </InsightContext.Provider>
  );
}

export function useInsights(): InsightContextValue {
  const ctx = useContext(InsightContext);
  if (!ctx) {
    throw new Error("useInsights must be used inside InsightProvider");
  }
  return ctx;
}
