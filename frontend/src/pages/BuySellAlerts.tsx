import React, { useState } from "react";
import Navbar from "../components/dashboard/Navbar/Navbar";
import DashFooter from "../components/dashboard/Home/dashFooter";
import { BuySellAlertProvider } from "../context/BuySellAlertContext";
import AlertsList from "../components/BuySellAlerts/AlertsList";
import CreateAlertForm from "../components/BuySellAlerts/CreateAlertForm";
import GraphBackgroundCorner from "../components/Background/GraphBackgroundCorner";

function BuySellAlertsContent() {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-white">
      <GraphBackgroundCorner />
      <Navbar />

      <main className="relative z-10 max-w-6xl mx-auto px-4 pt-32 pb-20">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Buy/Sell Alerts</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Set up automatic buy and sell signals based on price thresholds
          </p>
        </div>

        {/* Action Button */}
        <div className="mb-8 flex gap-3">
          <button
            onClick={() => setShowForm(!showForm)}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              showForm
                ? "bg-gray-300 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-400 dark:hover:bg-gray-600"
                : "bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600"
            }`}
          >
            {showForm ? "✕ Hide Form" : "+ Create New Alert"}
          </button>
        </div>

        {/* Create Alert Form - Visible when showForm is true */}
        {showForm && (
          <div className="mb-8">
            <CreateAlertForm onSuccess={() => setShowForm(false)} />
          </div>
        )}

        {/* Alerts List Section */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Your Alerts</h2>
          <AlertsList />
        </div>
      </main>

      <DashFooter />
    </div>
  );
}

export default function BuySellAlerts() {
  return (
    <BuySellAlertProvider>
      <BuySellAlertsContent />
    </BuySellAlertProvider>
  );
}
