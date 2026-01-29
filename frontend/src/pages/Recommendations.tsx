import { useEffect, useState } from "react";
import { FiBarChart2, FiCheckCircle, FiClock, FiTrendingUp } from "react-icons/fi";
import Navbar from "../components/dashboard/Navbar/Navbar";
import DashFooter from "../components/dashboard/Home/dashFooter";
import GraphBackgroundCorner from "../components/Background/GraphBackgroundCorner";
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
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {recommendations.map((rec: Recommendation) => (
        <div
          key={rec.id}
          className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {rec.commodity_name}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {rec.market_name || "Market"} • {rec.time_horizon.replace("_", " ")}
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${getTypeColor(
                rec.recommendation_type
              )}`}
            >
              {rec.recommendation_type}
            </span>
          </div>

          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Current Price</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                ₹{rec.current_price?.toFixed(2) ?? "--"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Target Price</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                ₹{rec.target_price?.toFixed(2) ?? "--"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Expected Change</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {rec.expected_change_pct?.toFixed(1) ?? "--"}%
              </span>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
            {rec.reasoning}
          </div>

          <div className="mt-4 flex items-center justify-between">
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(
                rec.confidence
              )}`}
            >
              Confidence: {rec.confidence}
            </span>

            {rec.acknowledged ? (
              <span className="flex items-center gap-2 text-emerald-600 dark:text-emerald-300 text-sm font-medium">
                <FiCheckCircle /> Acknowledged
              </span>
            ) : (
              <button
                onClick={() => acknowledgeRecommendation(rec.id)}
                className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition"
              >
                Acknowledge
              </button>
            )}
          </div>
        </div>
      ))}

      {recommendations.length === 0 && (
        <div className="col-span-full text-center py-16 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-dashed border-gray-300 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400">No active recommendations yet.</p>
        </div>
      )}
    </div>
  );

  const renderHistory = () => (
    <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr className="text-left text-gray-600 dark:text-gray-400">
            <th className="px-4 py-3">Commodity</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Outcome</th>
            <th className="px-4 py-3">Actual Change</th>
            <th className="px-4 py-3">ROI</th>
            <th className="px-4 py-3">Date</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item: RecommendationHistoryItem) => (
            <tr
              key={item.id}
              className="border-t border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-200"
            >
              <td className="px-4 py-3 font-medium">{item.commodity_name}</td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${getTypeColor(
                    item.recommendation_type
                  )}`}
                >
                  {item.recommendation_type}
                </span>
              </td>
              <td className="px-4 py-3">{item.outcome}</td>
              <td className="px-4 py-3">
                {item.actual_change_pct?.toFixed(1) ?? "--"}%
              </td>
              <td className="px-4 py-3">{item.roi_pct?.toFixed(1) ?? "--"}%</td>
              <td className="px-4 py-3">
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6">
        <p className="text-sm text-gray-500 dark:text-gray-400">Accuracy Rate</p>
        <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {metrics ? `${Math.round(metrics.accuracy_rate * 100)}%` : "--"}
        </p>
      </div>
      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6">
        <p className="text-sm text-gray-500 dark:text-gray-400">Average ROI</p>
        <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {metrics ? `${metrics.average_roi_pct.toFixed(1)}%` : "--"}
        </p>
      </div>
      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6">
        <p className="text-sm text-gray-500 dark:text-gray-400">Total Recommendations</p>
        <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {metrics ? metrics.total_recommendations : "--"}
        </p>
      </div>

      {metrics && (
        <div className="col-span-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Accuracy by Type
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(metrics.by_type_accuracy).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-800 px-4 py-3"
              >
                <span className="text-sm text-gray-600 dark:text-gray-400">{key}</span>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
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
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-white">
      <GraphBackgroundCorner />
      <Navbar />

      <main className="relative z-10 max-w-6xl mx-auto px-4 pt-28 pb-20">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Recommendations</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Actionable buy/sell insights with confidence scores and history.
          </p>
        </div>

        <div className="mb-6 flex flex-wrap gap-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all border ${
                activeTab === tab.id
                  ? "bg-emerald-600 text-white border-emerald-600"
                  : "bg-white dark:bg-gray-950 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white"
              }`}
            >
              {tab.icon}
              {tab.label}
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
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading recommendations...</p>
            </div>
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
    </div>
  );
}
