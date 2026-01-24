// src/context/types.ts

export interface SelectorData {
  market: string;
  product: string;
  forecastRange: string;
}

export interface StockMetrics {
  predictedDemand: number;
  stockNeeded: number;
  overstockRisk: number;
  understockRisk: number;
}

/**
 * actual = historical sales
 * forecast = predicted demand
 */
export interface DemandGraphPoint {
  day: string;
  actual: number;
  forecast: number;
}

export interface ImpactData {
  festival: string;
  festivalImpact: string;
  weather: string;
}

export interface RecommendationRow {
  product: string;
  current: number;
  suggested: number;
  buffer: number;
  risk: string;
}

export interface AnalysisContextValue {
  selectorData: SelectorData;
  stockMetrics: StockMetrics;
  demandGraphData: DemandGraphPoint[];
  impactData: ImpactData;
  recommendationTable: RecommendationRow[];
}
