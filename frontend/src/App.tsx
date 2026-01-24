import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SignedIn, SignedOut } from "@clerk/clerk-react";

import AuthComponent from "./components/auth/AuthComponent";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/auth" element={<AuthComponent />} />

        {/* ROOT (protected dashboard) */}
        <Route
          path="/dashboard"
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
      </Routes>




    </BrowserRouter>
  );
}

export default App;
