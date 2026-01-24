import { useEffect, useState } from "react";

import Navbar from "../components/dashboard/Navbar/Navbar";
import UserSync from "../components/dashboard/Navbar/UserSync";
import DashboardLoader from "../components/dashboard/Home/DashboardLoader";

import { ForecastProvider } from "../context/ForecastContext";

import WelcomeCard from "../components/dashboard/Home/WelcomeCard";
import MarketSelector from "../components/dashboard/Home/MarketSelector";
import ProductSelector from "../components/dashboard/Home/ProductSelector";
import GenerateForecastCTA from "../components/dashboard/Home/GenerateForecastCTA";
import DashboardGraphBackground from "../components/dashboard/Home/DashboardGraphBackground";
import DashFooter from "../components/dashboard/Home/dashFooter";


export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate / wait for user + dashboard readiness
    // Replace this later with Clerk / Supabase / API readiness
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800); // subtle delay to avoid flash

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <DashboardLoader />;
  }

  return (
    <ForecastProvider>
      <div className="dashboard relative min-h-screen overflow-hidden">
        <DashboardGraphBackground />
        <Navbar />
        <UserSync />

        {/* Home content */}
        <main className="dashboard-body relative z-10 max-w-2xl mx-auto mt-12">
          <WelcomeCard />

          <div className="grid gap-6">
            <MarketSelector />
            <ProductSelector />
            <GenerateForecastCTA />
          </div>
        </main>
      </div>
      <DashFooter/>
    </ForecastProvider>
  );
}
