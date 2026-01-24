import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SignedIn, SignedOut } from "@clerk/clerk-react";

import AuthComponent from "./components/auth/AuthComponent";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";
import ProductAnalysis from "./pages/ProductAnalysis";
import ComingSoon from "./pages/ComingSoon";

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
        <Route path="/dashboard/inventory" element={<ComingSoon />} />
        <Route path="/dashboard/insights" element={<ComingSoon />} />
        <Route path="/dashboard/model-accuracy" element={<ComingSoon />} />
        <Route path="/blog" element={<ComingSoon />} />
        <Route path="/pricing" element={<ComingSoon />} />

      </Routes>




    </BrowserRouter>
  );
}

export default App;
