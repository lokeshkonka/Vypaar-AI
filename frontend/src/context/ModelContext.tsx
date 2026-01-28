// src/context/ModelContext.tsx
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext } from "react";
import {
  modelAccuracyDummy,
  modelGraphDummy,
  type ModelAccuracyMetrics,
  type ModelGraphPoint,
} from "../data/model-dummy";

interface ModelContextValue {
  metrics: ModelAccuracyMetrics;
  graphData: ModelGraphPoint[];
}

const ModelContext = createContext<ModelContextValue | null>(null);

export function ModelProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  /*
  // 🔒 BACKEND (COMMENTED)
  const fetchModelAccuracy = async () => {
    const res = await fetch(`${BACKEND_URL}/api/model/accuracy`);
    return await res.json();
  };
  */

  return (
    <ModelContext.Provider
      value={{
        metrics: modelAccuracyDummy,
        graphData: modelGraphDummy,
      }}
    >
      {children}
    </ModelContext.Provider>
  );
}

export function useModelAccuracy(): ModelContextValue {
  const ctx = useContext(ModelContext);
  if (!ctx) {
    throw new Error("useModelAccuracy must be used inside ModelProvider");
  }
  return ctx;
}
