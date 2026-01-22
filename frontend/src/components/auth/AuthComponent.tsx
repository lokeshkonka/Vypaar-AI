import { SignIn, SignedIn, SignedOut, useAuth } from "@clerk/clerk-react";
import { Navigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import MarketGraphBackground from "./MarketGraphBackground";

/* ---------------- Skeleton Loader ---------------- */
function AuthSkeleton() {
  return (
    <div className="w-[360px] rounded-xl bg-white p-6 shadow-sm animate-pulse">
      <div className="h-6 w-2/3 rounded bg-gray-200 mb-3" />
      <div className="h-4 w-1/2 rounded bg-gray-200 mb-6" />

      <div className="space-y-4">
        <div className="h-10 rounded bg-gray-200" />
        <div className="h-10 rounded bg-gray-200" />
        <div className="h-10 rounded bg-gray-200" />
      </div>
    </div>
  );
}

export default function AuthComponent() {
  const { isLoaded } = useAuth();

  return (
    <div className="relative min-h-screen bg-[#f5f7f6] overflow-hidden">
      {/* Background */}
      <MarketGraphBackground />

      {/* Centered Auth Container */}
      <div className="relative z-10 flex min-h-screen items-center justify-center">
        <AnimatePresence mode="wait">
          {/* LOADER */}
          {!isLoaded && (
            <motion.div
              key="loader"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <AuthSkeleton />
            </motion.div>
          )}

          {/* AUTH CONTENT */}
          {isLoaded && (
            <motion.div
              key="auth"
              initial={{ opacity: 0, y: 8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
            >
              {/* If already signed in → dashboard */}
              <SignedIn>
                <Navigate to="/dashboard" replace />
              </SignedIn>

              {/* If signed out → SignIn */}
              <SignedOut>
                <SignIn
                  appearance={{
                    elements: {
                      card: "shadow-none bg-white rounded-xl",
                      headerTitle: "text-2xl font-semibold text-gray-900",
                      headerSubtitle: "text-gray-500",
                    },
                  }}
                />
              </SignedOut>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
