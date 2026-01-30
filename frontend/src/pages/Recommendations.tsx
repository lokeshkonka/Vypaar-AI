import { useEffect, useState } from "react";
import { FiBarChart2, FiCheckCircle, FiClock, FiTrendingUp } from "react-icons/fi";
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { Skeleton } from "../components/common";
import DashFooter from "../components/dashboard/Home/dashFooter";
import { useRecommendations } from "../context/RecommendationContext";
import type {
  Recommendation,
  RecommendationHistoryItem,
} from "../context/RecommendationContext";

const tabs = [
  { id: "active", label: "Active", icon: <FiTrendingUp /> },
  { id: "history", label: "History", icon: <FiClock /> },
  { id: "metrics", label: "Metrics", icon: <FiBarChart2 /> },
];

const getTypeColor = (type: string) => {
  switch (type) {
    case "BUY":
      return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200";
    case "SELL":
      return "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200";
    case "STOCK_UP":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200";
    case "STOCK_DOWN":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-200";
  }
};

const getConfidenceColor = (confidence: string) => {
  switch (confidence) {
    case "HIGH":
      return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-200";
    case "MEDIUM":
      return "bg-yellow-500/10 text-yellow-700 dark:text-yellow-200";
    default:
      return "bg-gray-500/10 text-gray-700 dark:text-gray-200";
  }
};

export default function Recommendations() {
  const [activeTab, setActiveTab] = useState("active");
  const {
    recommendations,
    history,
    metrics,
    isLoading,
    error,
    successMessage,
    fetchRecommendations,
    fetchHistory,
    fetchMetrics,
    acknowledgeRecommendation,
  } = useRecommendations();

  useEffect(() => {
    if (activeTab === "active") {
      fetchRecommendations();
    } else if (activeTab === "history") {
      fetchHistory();
    } else if (activeTab === "metrics") {
      fetchMetrics();
    }
  }, [activeTab, fetchRecommendations, fetchHistory, fetchMetrics]);

  const renderActive = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
      {recommendations.map((rec: Recommendation) => (
        <div
          key={rec.id}
          className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between gap-3 mb-4">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white truncate">
                {rec.commodity_name}
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                {rec.market_name || "Market"} • {rec.time_horizon.replace("_", " ")}
              </p>
            </div>
            <span
              className={`px-2.5 sm:px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${getTypeColor(
                rec.recommendation_type
              )}`}
            >
              {rec.recommendation_type}
            </span>
          </div>

          <div className="space-y-2 text-sm bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 sm:p-4 mb-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Current Price</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                ₹{rec.current_price?.toFixed(2) ?? "--"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Target Price</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                ₹{rec.target_price?.toFixed(2) ?? "--"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Expected Change</span>
              <span className={`font-semibold ${
                (rec.expected_change_pct ?? 0) > 0 
                  ? "text-emerald-600 dark:text-emerald-400" 
                  : "text-red-600 dark:text-red-400"
              }`}>
                {rec.expected_change_pct?.toFixed(1) ?? "--"}%
              </span>
            </div>
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
            {rec.reasoning}
          </div>

          <div className="flex items-center justify-between gap-3 pt-3 border-t border-gray-200 dark:border-gray-800">
            <span
              className={`px-2.5 sm:px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(
                rec.confidence
              )}`}
            >
              {rec.confidence}
            </span>

            {rec.acknowledged ? (
              <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 text-sm font-medium">
                <FiCheckCircle className="w-4 h-4" /> Acknowledged
              </span>
            ) : (
              <button
                onClick={() => acknowledgeRecommendation(rec.id)}
                className="px-3 sm:px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs sm:text-sm font-semibold hover:bg-emerald-700 active:bg-emerald-800 transition-colors"
              >
                Acknowledge
              </button>
            )}
          </div>
        </div>
      ))}

      {recommendations.length === 0 && (
        <div className="col-span-full text-center py-12 sm:py-16 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-dashed border-gray-300 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400">No active recommendations yet.</p>
        </div>
      )}
    </div>
  );

  const renderHistory = () => (
    <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shadow-sm">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <tr className="text-left text-gray-600 dark:text-gray-400">
            <th className="px-3 sm:px-4 py-3 font-semibold">Commodity</th>
            <th className="px-3 sm:px-4 py-3 font-semibold">Type</th>
            <th className="px-3 sm:px-4 py-3 font-semibold">Outcome</th>
            <th className="px-3 sm:px-4 py-3 font-semibold">Change</th>
            <th className="px-3 sm:px-4 py-3 font-semibold">ROI</th>
            <th className="px-3 sm:px-4 py-3 font-semibold">Date</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item: RecommendationHistoryItem, index: number) => (
            <tr
              key={item.id}
              className={`${
                index !== history.length - 1 
                  ? "border-b border-gray-200 dark:border-gray-800" 
                  : ""
              } text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors`}
            >
              <td className="px-3 sm:px-4 py-3 font-medium whitespace-nowrap">{item.commodity_name}</td>
              <td className="px-3 sm:px-4 py-3">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${getTypeColor(
                    item.recommendation_type
                  )}`}
                >
                  {item.recommendation_type}
                </span>
              </td>
              <td className="px-3 sm:px-4 py-3 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  item.outcome === "SUCCESS" 
                    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200"
                    : "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200"
                }`}>
                  {item.outcome}
                </span>
              </td>
              <td className={`px-3 sm:px-4 py-3 font-semibold whitespace-nowrap ${
                (item.actual_change_pct ?? 0) > 0 
                  ? "text-emerald-600 dark:text-emerald-400" 
                  : "text-red-600 dark:text-red-400"
              }`}>
                {item.actual_change_pct?.toFixed(1) ?? "--"}%
              </td>
              <td className={`px-3 sm:px-4 py-3 font-semibold whitespace-nowrap ${
                (item.roi_pct ?? 0) > 0 
                  ? "text-emerald-600 dark:text-emerald-400" 
                  : "text-red-600 dark:text-red-400"
              }`}>
                {item.roi_pct?.toFixed(1) ?? "--"}%
              </td>
              <td className="px-3 sm:px-4 py-3 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                {new Date(item.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {history.length === 0 && (
        <div className="text-center py-10 text-gray-500 dark:text-gray-400">
          No historical recommendations yet.
        </div>
      )}
    </div>
  );

  const renderMetrics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2">Accuracy Rate</p>
          <p className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            {metrics ? `${Math.round(metrics.accuracy_rate * 100)}%` : "--"}
          </p>
        </div>
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2">Average ROI</p>
          <p className="text-2xl sm:text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {metrics ? `${metrics.average_roi_pct.toFixed(1)}%` : "--"}
          </p>
        </div>
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2">Total Recommendations</p>
          <p className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            {metrics ? metrics.total_recommendations : "--"}
          </p>
        </div>
      </div>

      {metrics && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-5 sm:p-6 shadow-sm">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Accuracy by Type
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {Object.entries(metrics.by_type_accuracy).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-lg bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 px-3 sm:px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
              >
                <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">{key}</span>
                <span className="text-sm sm:text-base font-bold text-gray-900 dark:text-white">
                  {Math.round(value * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <DashboardLayout>
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 pt-24 pb-20">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2 text-gray-900 dark:text-white">
            Recommendations
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            Actionable buy/sell insights with confidence scores and history.
          </p>
        </div>

        <div className="mb-6 flex flex-wrap gap-2 sm:gap-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all border shadow-sm ${
                activeTab === tab.id
                  ? "bg-emerald-600 text-white border-emerald-600 shadow-emerald-500/20"
                  : "bg-white dark:bg-gray-950 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 hover:text-gray-900 dark:hover:text-white"
              }`}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {successMessage && (
          <div className="mb-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200">
            {successMessage}
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800 dark:border-red-800 dark:bg-red-900/30 dark:text-red-200">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="space-y-6">
            <Skeleton className="h-48 rounded-xl" />
            <Skeleton className="h-48 rounded-xl" />
          </div>
        ) : activeTab === "active" ? (
          renderActive()
        ) : activeTab === "history" ? (
          renderHistory()
        ) : (
          renderMetrics()
        )}
      </main>

      <DashFooter />
    </DashboardLayout>
  );
}
