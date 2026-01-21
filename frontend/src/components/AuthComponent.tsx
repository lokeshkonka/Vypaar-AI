import { SignIn, SignedIn, SignedOut } from "@clerk/clerk-react";
import { Navigate } from "react-router-dom";
import MarketGraphBackground from "./MarketGraphBackground";

export default function AuthComponent() {
  return (
    <div className="glass-bg">
      <div className="glass-overlay" />
      <MarketGraphBackground />

      <div className="auth-container">
        {/* If already signed in → dashboard */}
        <SignedIn>
          <Navigate to="/dashboard" replace />
        </SignedIn>

        {/* If signed out → show SignIn */}
        <SignedOut>
          <SignIn
            appearance={{
              elements: {
                card: "bg-transparent shadow-none scale-105",
                headerTitle: "text-3xl font-semibold text-gray-800",
                headerSubtitle: "text-gray-500",
              },
            }}
          />
        </SignedOut>
      </div>
    </div>
  );
}
