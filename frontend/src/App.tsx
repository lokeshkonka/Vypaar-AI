import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SignedIn, SignedOut } from "@clerk/clerk-react";

import AuthComponent from "./components/auth/AuthComponent";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";
import ProductAnalysis from "./pages/ProductAnalysis";
import ComingSoon from "./pages/ComingSoon";
import Inventory from "./pages/Inventory";
import Insights from "./pages/Insights";
import ModelAccuracy from "./pages/ModelAccuracy";
import BuySellAlerts from "./pages/BuySellAlerts";
import Docs from "./pages/Docs";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/auth" element={<AuthComponent />} />

        {/* ROOT (protected dashboard) */}
        <Route
          path="/dashboard/selector"
          element={
            <>
              <SignedIn>
                <Dashboard />
              </SignedIn>

              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          }
        />
        <Route path="/" element={<Landing />} />
        <Route 
          path="/dashboard/product-analysis" 
          element={
            <>
              <SignedIn>
                <ProductAnalysis />
              </SignedIn>
              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          } 
        />
        <Route 
          path="/dashboard/inventory" 
          element={
            <>
              <SignedIn>
                <Inventory />
              </SignedIn>
              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          } 
        />
        <Route 
          path="/dashboard/insights" 
          element={
            <>
              <SignedIn>
                <Insights />
              </SignedIn>
              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          } 
        />
        <Route 
          path="/dashboard/model-accuracy" 
          element={
            <>
              <SignedIn>
                <ModelAccuracy />
              </SignedIn>
              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          } 
        />
        <Route 
          path="/dashboard/buysell-alerts" 
          element={
            <>
              <SignedIn>
                <BuySellAlerts />
              </SignedIn>
              <SignedOut>
                <Navigate to="/auth" replace />
              </SignedOut>
            </>
          } 
        />
        <Route path="/blog" element={<ComingSoon />} />
        <Route path="/pricing" element={<ComingSoon />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/about" element={<ComingSoon />} />
        <Route path="/contact" element={<ComingSoon />} />

      </Routes>




    </BrowserRouter>
  );
}

export default App;
