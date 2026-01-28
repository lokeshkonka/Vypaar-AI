import Navbar from "../components/dashboard/Navbar/Navbar";
import DashFooter from "../components/dashboard/Home/dashFooter";
import GraphBackgroundBottom from "../components/Background/graphBackgroundBottom";

import { ContextAnalysisProvider } from "../context/ContextAnalysis";
import ActionRequiredCard from "../components/Inventory/ActionRequiredCard";
import DecisionInsightCard from "../components/Inventory/DecisionInsightCard";
import StockCompare from "../components/Inventory/StockCompare";
import YourStock from "../components/Inventory/YourStock";
import StockComponent from "../components/ProductAnalysis/StockComponent";
import { InventoryProvider } from "../context/InventoryContext";
import { ForecastProvider } from "../context/ForecastContext";

export default function Inventory() {
  return (
    <ContextAnalysisProvider>
      <div className="relative min-h-screen overflow-hidden">
        {/* Background glows */}
        <div className="absolute -top-40 -left-40 h-105 w-105 rounded-full bg-emerald-500/20 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 h-105 w-105 rounded-full bg-emerald-400/10 blur-[120px]" />

        <Navbar />
        <GraphBackgroundBottom />

        <main className="relative z-10 max-w-6xl mx-auto px-4 pt-28 space-y-6">
          <h1 className="text-2xl font-semibold tracking-tight">
            Inventory Recommendation
          </h1>
            <StockComponent  />
          <ActionRequiredCard />
          <DecisionInsightCard />
          <StockCompare />
          < ForecastProvider>
          <InventoryProvider>
            <YourStock />
          </InventoryProvider>
          </ForecastProvider>
        </main>

        <DashFooter />
      </div>
    </ContextAnalysisProvider>
  );
}
