import { useEffect, useState } from "react";
import { Search, Heart, MessageCircle, Loader, Plus } from "lucide-react";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import CreatePostModal from "../components/community/CreatePostModal";
import CommentsSection from "../components/community/CommentsSection";

interface Discussion {
  id: string;
  author: string;
  avatar: string;
  title: string;
  content: string;
  commodity: string;
  market?: string;
  tags?: string[];
  timestamp: Date;
  likes: number;
  replies: number;
}

interface Comment {
  id: number;
  discussion_id: number;
  author: string;
  avatar_url: string;
  content: string;
  likes_count: number;
  created_at: string;
}

interface PostData {
  title: string;
  content: string;
  commodity: string;
  market?: string;
  tags: string[];
  author: string;
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
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newCommodity, setNewCommodity] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [expandedDiscussion, setExpandedDiscussion] = useState<string | null>(null);
  const [comments, setComments] = useState<Record<string, Comment[]>>({});

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
        id: String(d.id || d._id || Math.random()),
        author: d.author || "Anonymous",
        avatar:
          d.avatar_url ||
          d.avatar ||
          `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.author || "user"}`,
        title: d.title || d.subject || "Untitled",
        content: d.content || d.description || d.message || "",
        commodity: d.commodity || d.category || "General",
        timestamp: new Date(d.created_at || d.createdAt || d.timestamp || Date.now()),
        likes: d.likes_count ?? d.likes ?? 0,
        replies: d.replies_count ?? d.replies ?? 0,
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

  const handleLike = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/discussions/${id}/like`, {
        method: 'POST',
      });
      
      if (response.ok) {
        setDiscussions((prev) =>
          prev.map((d) => (d.id === id ? { ...d, likes: d.likes + 1 } : d))
        );
      }
    } catch (error) {
      console.error('Error liking discussion:', error);
    }
  };

  const handleCreatePost = async (postData: PostData) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/discussions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });

      if (!response.ok) {
        throw new Error('Failed to create post');
      }

      await fetchDiscussions();
    } catch (error) {
      console.error('Error creating post:', error);
      throw error;
    }
  };

  const fetchComments = async (discussionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/discussions/${discussionId}/comments`);
      if (response.ok) {
        const data = await response.json();
        setComments((prev) => ({ ...prev, [discussionId]: data.comments || [] }));
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleAddComment = async (discussionId: string, content: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/discussions/${discussionId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          author: 'Anonymous User', // TODO: Get from auth context
        }),
      });

      if (response.ok) {
        await fetchComments(discussionId);
        setDiscussions((prev) =>
          prev.map((d) => (d.id === discussionId ? { ...d, replies: d.replies + 1 } : d))
        );
      }
    } catch (error) {
      console.error('Error adding comment:', error);
      throw error;
    }
  };

  const handleLikeComment = async (discussionId: string, commentId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/discussions/${discussionId}/comments/${commentId}/like`,
        {
          method: 'POST',
        }
      );

      if (response.ok) {
        await fetchComments(discussionId);
      }
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };

  const toggleComments = async (discussionId: string) => {
    if (expandedDiscussion === discussionId) {
      setExpandedDiscussion(null);
    } else {
      setExpandedDiscussion(discussionId);
      if (!comments[discussionId]) {
        await fetchComments(discussionId);
      }
    }
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="mb-6 sm:mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Discussion Board
              </h1>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                Discuss commodity prices and trading strategies with the community.
              </p>
            </div>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition flex items-center gap-2 shadow-lg"
            >
              <Plus size={20} />
              <span className="hidden sm:inline">New Post</span>
            </button>
          </div>

          {/* Search & Filter Card */}
          <div className="glass-card p-4 sm:p-5 lg:p-6 mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <div className="relative flex-1">
                <Search
                  size={18}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--text-soft)" }}
                />
                <input
                  type="text"
                  placeholder="Search discussions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border focus:outline-none focus:ring-2 transition"
                  style={{ 
                    borderColor: "var(--border)", 
                    background: "var(--panel)", 
                    color: "var(--text-main)",
                    borderRadius: 0
                  }}
                />
              </div>

              <select
                value={selectedCommodity || ""}
                onChange={(e) => setSelectedCommodity(e.target.value || null)}
                className="sm:w-56 px-4 py-3 text-sm border focus:outline-none focus:ring-2 transition"
                style={{ 
                  borderColor: "var(--border)", 
                  background: "var(--panel)", 
                  color: "var(--text-main)",
                  borderRadius: 0
                }}
              >
                <option value="">All Commodities</option>
                {commodities.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-16 sm:py-20">
              <div className="text-center">
                <div className="relative inline-block">
                  <Loader className="w-12 h-12 sm:w-14 sm:h-14 text-emerald-500 dark:text-emerald-400 animate-spin" />
                  <div className="absolute inset-0 blur-xl bg-emerald-500/30 dark:bg-emerald-400/30 animate-pulse"></div>
                </div>
                <p className="text-gray-600 dark:text-gray-400 font-medium mt-4 text-sm sm:text-base">
                  Loading discussions...
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50/80 dark:bg-red-900/20 backdrop-blur-xl border border-red-200 dark:border-red-800 rounded-2xl p-5 sm:p-6 mb-6 shadow-xl shadow-red-500/5">
              <p className="text-red-700 dark:text-red-300 text-sm sm:text-base mb-3">
                <span className="font-semibold">Error:</span> {error}
              </p>
              <button
                onClick={fetchDiscussions}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-700 active:scale-95 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-red-500/20"
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
                          {discussion.market && (
                            <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-2 py-0.5 rounded-full font-medium">
                              {discussion.market}
                            </span>
                          )}
                        </div>

                        <h3 className="font-semibold text-gray-900 dark:text-white mb-1.5 text-sm sm:text-base">
                          {discussion.title}
                        </h3>

                        <p className="text-gray-700 dark:text-gray-300 text-sm mb-3 line-clamp-2">
                          {discussion.content}
                        </p>

                        {discussion.tags && discussion.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {discussion.tags.map((tag, i) => (
                              <span
                                key={i}
                                className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded-full"
                              >
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center gap-4 sm:gap-6">
                          <button
                            onClick={() => handleLike(discussion.id)}
                            className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition text-sm font-medium"
                          >
                            <Heart size={16} className="flex-shrink-0" />
                            <span>{discussion.likes}</span>
                          </button>
                          <button
                            onClick={() => toggleComments(discussion.id)}
                            className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 transition text-sm font-medium"
                          >
                            <MessageCircle size={16} className="flex-shrink-0" />
                            <span>{discussion.replies}</span>
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Comments Section */}
                    {expandedDiscussion === discussion.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <CommentsSection
                          discussionId={parseInt(discussion.id)}
                          comments={comments[discussion.id] || []}
                          onAddComment={(content) => handleAddComment(discussion.id, content)}
                          onLikeComment={(commentId) => handleLikeComment(discussion.id, commentId)}
                        />
                      </div>
                    )}
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
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 lg:gap-5 mt-6 sm:mt-8 lg:mt-10">
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 border border-gray-200 dark:border-gray-700 text-center shadow-lg hover:shadow-2xl hover:shadow-emerald-500/10 transition-all group">
                <MessageSquare className="w-8 h-8 sm:w-10 sm:h-10 text-emerald-600 dark:text-emerald-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">
                  {discussions.length}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Discussions
                </div>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 border border-gray-200 dark:border-gray-700 text-center shadow-lg hover:shadow-2xl hover:shadow-blue-500/10 transition-all group">
                <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 dark:text-blue-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  {commodities.length}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Commodities
                </div>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-4 sm:p-5 lg:p-6 border border-gray-200 dark:border-gray-700 text-center shadow-lg hover:shadow-2xl hover:shadow-purple-500/10 transition-all group">
                <Users className="w-8 h-8 sm:w-10 sm:h-10 text-purple-600 dark:text-purple-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                  {discussions.reduce((sum, d) => sum + d.replies, 0)}
                </div>
                <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Total Replies
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Post Modal */}
      <CreatePostModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreatePost}
      />
    </DashboardLayout>
  );
}
