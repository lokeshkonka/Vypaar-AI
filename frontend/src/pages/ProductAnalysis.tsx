import Navbar from "../components/dashboard/Navbar/Navbar";
import DashFooter from "../components/dashboard/Home/dashFooter";
import { ContextAnalysisProvider } from "../context/ContextAnalysis";

import SelectorComponent from "../components/ProductAnalysis/SelectorComponent";
import StockComponent from "../components/ProductAnalysis/StockComponent";
import DemandGraph from "../components/ProductAnalysis/DemandGraph";
import ImpactComponent from "../components/ProductAnalysis/ImpactComponent";
import RecommendTable from "../components/ProductAnalysis/RecommendTable";
import GraphBackgroundCorner from "../components/Background/GraphBackgroundCorner";

const ProductAnalysis = () => {
  return (
    <ContextAnalysisProvider>
      <Navbar />
      <GraphBackgroundCorner/>
      <main
        className="mx-auto px-4 pt-20 space-y-8 max-w-6xl">
          <header>
            <h1 className="text-3xl font-semibold">
              Product Analysis
            </h1>
            <p className="text-soft">
              In-depth insights and recommendations for your products
            </p>
          </header>
        <SelectorComponent />
        <StockComponent />
        <DemandGraph />
        <ImpactComponent />
        <RecommendTable />
      </main>

      <DashFooter />
    </ContextAnalysisProvider>
  );
};

export default ProductAnalysis;
