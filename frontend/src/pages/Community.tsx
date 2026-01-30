import { useEffect, useState } from "react";
import { Search, Heart, MessageCircle, Loader } from "lucide-react";
import { DashboardLayout } from "../components/layout/DashboardLayout";

interface Discussion {
  id: string;
  author: string;
  avatar: string;
  title: string;
  content: string;
  commodity: string;
  timestamp: Date;
  likes: number;
  replies: number;
}

function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function Community() {
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCommodity, setSelectedCommodity] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDiscussions();
  }, []);

  const fetchDiscussions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("http://localhost:8000/api/v1/discussions");

      if (!response.ok) {
        throw new Error(`Failed to fetch discussions: ${response.statusText}`);
      }

      const data = await response.json();

      const transformedDiscussions = (data.discussions || data || []).map((d: any) => ({
        id: d.id || d._id || String(Math.random()),
        author: d.author || "Anonymous",
        avatar:
          d.avatar ||
          `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.author || "user"}`,
        title: d.title || d.subject || "Untitled",
        content: d.content || d.description || d.message || "",
        commodity: d.commodity || d.category || "General",
        timestamp: new Date(d.timestamp || d.createdAt || Date.now()),
        likes: d.likes || 0,
        replies: d.replies || 0,
      }));

      setDiscussions(transformedDiscussions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load discussions");
      console.error("Error fetching discussions:", err);
    } finally {
      setLoading(false);
    }
  };

  const commodities = Array.from(new Set(discussions.map((d) => d.commodity))).sort();

  const filteredDiscussions = discussions.filter((d) => {
    const matchesSearch =
      d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.author.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCommodity = !selectedCommodity || d.commodity === selectedCommodity;

    return matchesSearch && matchesCommodity;
  });

  const handleLike = (id: string) => {
    setDiscussions((prev) =>
      prev.map((d) => (d.id === id ? { ...d, likes: d.likes + 1 } : d))
    );
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Discussion Board
            </h1>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
              Discuss commodity prices and trading strategies with the community.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700 mb-6 space-y-3 shadow-sm">
            <div className="relative">
              <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500"
              />
              <input
                type="text"
                placeholder="Search discussions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:focus:ring-emerald-600 transition"
              />
            </div>

            <select
              value={selectedCommodity || ""}
              onChange={(e) => setSelectedCommodity(e.target.value || null)}
              className="w-full px-3 py-2.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:focus:ring-emerald-600 transition"
            >
              <option value="">All Commodities</option>
              {commodities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <Loader className="w-10 h-10 text-emerald-500 dark:text-emerald-400 animate-spin mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-400 font-medium">
                  Loading discussions...
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 sm:p-5 mb-6 shadow-sm">
              <p className="text-red-700 dark:text-red-300 text-sm">
                <span className="font-semibold">Error:</span> {error}
              </p>
              <button
                onClick={fetchDiscussions}
                className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 active:bg-red-800 text-white text-sm font-medium rounded-lg transition shadow-sm"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-3 sm:space-y-4">
              {filteredDiscussions.length > 0 ? (
                filteredDiscussions.map((discussion) => (
                  <div
                    key={discussion.id}
                    className="bg-white dark:bg-gray-800 rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600 transition-all"
                  >
                    <div className="flex gap-3 sm:gap-4">
                      <img
                        src={discussion.avatar}
                        alt={discussion.author}
                        className="w-10 h-10 sm:w-12 sm:h-12 rounded-full flex-shrink-0 ring-2 ring-gray-200 dark:ring-gray-700"
                      />

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className="font-semibold text-gray-900 dark:text-white text-sm sm:text-base">
                            {discussion.author}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {timeAgo(discussion.timestamp)}
                          </span>
                          <span className="text-xs bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded-full font-medium">
                            {discussion.commodity}
                          </span>
                        </div>

                        <h3 className="font-semibold text-gray-900 dark:text-white mb-1.5 text-sm sm:text-base">
                          {discussion.title}
                        </h3>

                        <p className="text-gray-700 dark:text-gray-300 text-sm mb-3 line-clamp-2">
                          {discussion.content}
                        </p>

                        <div className="flex items-center gap-4 sm:gap-6">
                          <button
                            onClick={() => handleLike(discussion.id)}
                            className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition text-sm font-medium"
                          >
                            <Heart size={16} className="flex-shrink-0" />
                            <span>{discussion.likes}</span>
                          </button>
                          <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 text-sm font-medium">
                            <MessageCircle size={16} className="flex-shrink-0" />
                            <span>{discussion.replies}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-10 sm:p-12 text-center border border-dashed border-gray-300 dark:border-gray-700">
                  <p className="text-gray-500 dark:text-gray-400">
                    {discussions.length === 0
                      ? "No discussions found"
                      : "No discussions match your search"}
                  </p>
                </div>
              )}
            </div>
          )}

          {!loading && !error && discussions.length > 0 && (
            <div className="grid grid-cols-3 gap-3 sm:gap-4 mt-6 sm:mt-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 sm:p-4 border border-gray-200 dark:border-gray-700 text-center shadow-sm hover:shadow-md transition">
                <div className="text-xl sm:text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {discussions.length}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Discussions
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 sm:p-4 border border-gray-200 dark:border-gray-700 text-center shadow-sm hover:shadow-md transition">
                <div className="text-xl sm:text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {commodities.length}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Commodities
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 sm:p-4 border border-gray-200 dark:border-gray-700 text-center shadow-sm hover:shadow-md transition">
                <div className="text-xl sm:text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {discussions.reduce((sum, d) => sum + d.replies, 0)}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Total Replies
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
