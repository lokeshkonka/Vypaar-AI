// src/context/ModelContext.tsx
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";
import {
  modelAccuracyDummy,
  modelGraphDummy,
  type ModelAccuracyMetrics,
  type ModelGraphPoint,
} from "../data/model-dummy";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

interface ModelContextValue {
  metrics: ModelAccuracyMetrics;
  graphData: ModelGraphPoint[];
  isLoading: boolean;
}

const ModelContext = createContext<ModelContextValue | null>(null);

export function ModelProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState<ModelAccuracyMetrics>(modelAccuracyDummy);
  const [graphData, setGraphData] = useState<ModelGraphPoint[]>(modelGraphDummy);

  // Fetch model accuracy from backend
  useEffect(() => {
    const fetchModelAccuracy = async () => {
      try {
        setIsLoading(true);
        const res = await fetch(`${BACKEND_URL}/api/model/accuracy`);
        if (res.ok) {
          const data = await res.json();
          setMetrics(data?.metrics || modelAccuracyDummy);
          setGraphData(data?.graphData || modelGraphDummy);
        }
      } catch (error) {
        console.error("Failed to fetch model accuracy:", error);
        setMetrics(modelAccuracyDummy);
        setGraphData(modelGraphDummy);
      } finally {
        setIsLoading(false);
      }
    };
    fetchModelAccuracy();
  }, []);

  return (
    <ModelContext.Provider
      value={{
        metrics,
        graphData,
        isLoading,
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
