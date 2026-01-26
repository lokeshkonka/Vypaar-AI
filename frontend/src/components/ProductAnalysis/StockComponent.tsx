// src/components/product-analysis/StockComponent.tsx
import {
  FiTrendingUp,
  FiPackage,
  FiAlertTriangle,
  FiAlertCircle,
} from "react-icons/fi";
import { useContextAnalysis } from "../../context/ContextAnalysis";
import MetricCard from "../ui/MetricCard";

export default function StockComponent() {
  const { stockMetrics } = useContextAnalysis();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Predicted Demand */}
      <MetricCard
        title="Predicted Demand"
        value={stockMetrics.predictedDemand}
        unit="kg"
        subtitle="Forecasted demand"
        icon={<FiTrendingUp size={18} />}
      />

      {/* Stock Needed */}
      <MetricCard
        title="Stock Needed"
        value={stockMetrics.stockNeeded}
        unit="kg"
        subtitle="Recommended inventory"
        icon={<FiPackage size={18} />}
      />

      {/* Overstock Risk */}
      <MetricCard
        title="Overstock Risk"
        value={stockMetrics.overstockRisk}
        unit="%"
        subtitle="Excess inventory risk"
        icon={<FiAlertTriangle size={18} />}
      />

      {/* Understock Risk */}
      <MetricCard
        title="Understock Risk"
        value={stockMetrics.understockRisk}
        unit="%"
        subtitle="Stockout probability"
        icon={<FiAlertCircle size={18} />}
      />
    </div>
  );
}
