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
        <Route path="/dashboard/product-analysis" element={<ProductAnalysis />} />
        <Route path="/dashboard/inventory" element={<Inventory />} />
        <Route path="/dashboard/insights" element={<Insights />} />
        <Route path="/dashboard/model-accuracy" element={<ModelAccuracy />} />
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
