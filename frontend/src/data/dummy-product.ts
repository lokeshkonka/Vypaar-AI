// src/data/dummy.ts

export const selectorData = {
  market: "Andheri",
  product: "Tomatoes",
  forecastRange: "Next 7 Days",
};

export const stockMetrics = {
  predictedDemand: 520,
  stockNeeded: 540,
  overstockRisk: 12,
  understockRisk: 8,
};

export const demandGraphData = [
  { day: "Mon", actual: 420, forecast: 450 },
  { day: "Tue", actual: 460, forecast: 480 },
  { day: "Wed", actual: 430, forecast: 470 },
  { day: "Thu", actual: 410, forecast: 460 },
  { day: "Fri", actual: 440, forecast: 490 },
];

export const impactData = {
  festival: "Shivratri",
  festivalImpact: "Expected ++",
  weather: "Rains expected in next days",
};

export const recommendationTable = [
  {
    product: "Tomatoes",
    current: 500,
    suggested: 540,
    buffer: 40,
    risk: "Low",
  },
];
