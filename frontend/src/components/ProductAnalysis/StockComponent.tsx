import { FiBarChart2 } from "react-icons/fi";
import { useContextAnalysis } from "../../context/ContextAnalysis";
import TableComponent from "./ui/TableComponent";

export default function StockComponent() {
  const { stockMetrics } = useContextAnalysis();

  const data = [
    {
      metric: "Predicted Demand",
      value: `${stockMetrics.predictedDemand} Kg`,
    },
    {
      metric: "Stock Needed",
      value: `${stockMetrics.stockNeeded} Kg`,
    },
    {
      metric: "Overstock Risk",
      value: `${stockMetrics.overstockRisk}%`,
    },
    {
      metric: "Understock Risk",
      value: `${stockMetrics.understockRisk}%`,
    },
  ];

  return (
    <TableComponent
      title="Stock Metrics"
      icon={<FiBarChart2 size={16} />}
      columns={[
        { key: "metric", label: "Metric" },
        {
          key: "value",
          label: "Value",
          align: "right",
        },
      ]}
      data={data}
    />
  );
}
