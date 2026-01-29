import { useEffect, useState } from "react";
import { useUserSettings } from "../context/UserSettingsContext";
import Breadcrumbs from "../components/common/Breadcrumbs";
import { FiUser, FiBell, FiKey, FiLock, FiLogOut, FiSave, FiCheck, FiX, FiCopy, FiTrash2, FiEye, FiEyeOff } from "react-icons/fi";

export default function UserSettings() {
  const {
    profile,
    notifications,
    apiKeys,
    securitySettings,
    sessions,
    isLoading,
    error,
    getProfile,
    updateProfile,
    getNotifications,
    updateNotifications,
    listAPIKeys,
    createAPIKey,
    revokeAPIKey,
    getSecuritySettings,
    enableTwoFactor,
    listSessions,
    revokeSession,
    revokeAllSessions,
  } = useUserSettings();

  const [activeTab, setActiveTab] = useState<"profile" | "notifications" | "api-keys" | "security">("profile");
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [successMessage, setSuccessMessage] = useState("");
  const [showNewKeyModal, setShowNewKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [createdKey, setCreatedKey] = useState<any>(null);
  const [keysCopied, setKeysCopied] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (activeTab === "profile") {
          await getProfile();
        } else if (activeTab === "notifications") {
          await getNotifications();
        } else if (activeTab === "api-keys") {
          await listAPIKeys();
        } else if (activeTab === "security") {
          await getSecuritySettings();
          await listSessions();
        }
      } catch (err) {
        console.error("Failed to load data:", err);
      }
    };
    loadData();
  }, [activeTab]);

  useEffect(() => {
    if (profile && editMode) {
      setFormData({
        first_name: profile.first_name,
        last_name: profile.last_name,
        email: profile.email,
        phone: profile.phone || "",
        organization: profile.organization || "",
        bio: profile.bio || "",
      });
    }
  }, [profile, editMode]);

  const handleSaveProfile = async () => {
    try {
      await updateProfile(formData);
      setEditMode(false);
      setSuccessMessage("Profile updated successfully!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update profile:", err);
    }
  };

  const handleToggleNotification = async (index: number) => {
    if (!notifications) return;
    const updated = [...notifications];
    updated[index].enabled = !updated[index].enabled;
    try {
      await updateNotifications(updated);
      setSuccessMessage("Notification preferences updated!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to update notifications:", err);
    }
  };

  const handleCreateAPIKey = async () => {
    if (!newKeyName.trim()) return;
    try {
      const key = await createAPIKey(newKeyName, 365);
      setCreatedKey(key);
      setNewKeyName("");
      setSuccessMessage("API key created successfully!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to create API key:", err);
    }
  };

  const handleRevokeAPIKey = async (keyId: string) => {
    if (!confirm("Are you sure you want to revoke this API key?")) return;
    try {
      await revokeAPIKey(keyId);
      setSuccessMessage("API key revoked successfully!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to revoke API key:", err);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setKeysCopied(true);
    setTimeout(() => setKeysCopied(false), 2000);
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await revokeSession(sessionId);
      setSuccessMessage("Session revoked!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to revoke session:", err);
    }
  };

  const handleRevokeAllSessions = async () => {
    if (!confirm("This will log you out from all other devices. Continue?")) return;
    try {
      await revokeAllSessions();
      setSuccessMessage("All sessions revoked!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Failed to revoke sessions:", err);
    }
  };

  const breadcrumbs = [
    { label: "Settings", href: "/dashboard/settings" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0a1515] pt-20 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Breadcrumbs items={breadcrumbs} />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mt-4">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your profile, preferences, and security settings</p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg flex items-center gap-3">
            <FiCheck className="text-emerald-600 dark:text-emerald-400" />
            <span className="text-emerald-700 dark:text-emerald-300">{successMessage}</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
            <FiX className="text-red-600 dark:text-red-400" />
            <span className="text-red-700 dark:text-red-300">{error}</span>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-200 dark:border-gray-700">
          {[
            { id: "profile", label: "Profile", icon: FiUser },
            { id: "notifications", label: "Notifications", icon: FiBell },
            { id: "api-keys", label: "API Keys", icon: FiKey },
            { id: "security", label: "Security", icon: FiLock },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition ${
                activeTab === id
                  ? "border-emerald-500 text-emerald-600 dark:text-emerald-400"
                  : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-[#1a2f2f] rounded-lg border border-gray-200 dark:border-gray-700 p-8">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
            </div>
          ) : activeTab === "profile" ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={editMode ? formData.first_name : profile?.first_name}
                    onChange={(e) => editMode && setFormData({ ...formData, first_name: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={editMode ? formData.last_name : profile?.last_name}
                    onChange={(e) => editMode && setFormData({ ...formData, last_name: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={editMode ? formData.email : profile?.email}
                    onChange={(e) => editMode && setFormData({ ...formData, email: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={editMode ? formData.phone : profile?.phone}
                    onChange={(e) => editMode && setFormData({ ...formData, phone: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Organization
                  </label>
                  <input
                    type="text"
                    value={editMode ? formData.organization : profile?.organization}
                    onChange={(e) => editMode && setFormData({ ...formData, organization: e.target.value })}
                    disabled={!editMode}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bio
                  </label>
                  <textarea
                    value={editMode ? formData.bio : profile?.bio}
                    onChange={(e) => editMode && setFormData({ ...formData, bio: e.target.value })}
                    disabled={!editMode}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white disabled:opacity-50"
                  />
                </div>
              </div>
              <div className="flex gap-4">
                {!editMode ? (
                  <button
                    onClick={() => setEditMode(true)}
                    className="px-6 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition flex items-center gap-2"
                  >
                    <FiUser size={18} /> Edit Profile
                  </button>
                ) : (
                  <>
                    <button
                      onClick={handleSaveProfile}
                      className="px-6 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition flex items-center gap-2"
                    >
                      <FiSave size={18} /> Save Changes
                    </button>
                    <button
                      onClick={() => {
                        setEditMode(false);
                        setFormData({});
                      }}
                      className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>
          ) : activeTab === "notifications" ? (
            <div className="space-y-4">
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Manage how you receive notifications from Vypaar AI
              </p>
              {notifications?.map((notif, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">{notif.notification_type}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Frequency: {notif.frequency}</p>
                  </div>
                  <button
                    onClick={() => handleToggleNotification(idx)}
                    className={`px-4 py-2 rounded-lg transition ${
                      notif.enabled
                        ? "bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                    }`}
                  >
                    {notif.enabled ? "Enabled" : "Disabled"}
                  </button>
                </div>
              ))}
            </div>
          ) : activeTab === "api-keys" ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">API Keys</h3>
                <button
                  onClick={() => setShowNewKeyModal(true)}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition flex items-center gap-2"
                >
                  <FiKey size={18} /> Create New Key
                </button>
              </div>

              {createdKey && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-3">New API Key Created</h4>
                  <p className="text-sm text-blue-800 dark:text-blue-400 mb-3">
                    Copy your API key now. You won't be able to see it again.
                  </p>
                  <div className="flex gap-2 mb-3">
                    <input
                      type="text"
                      readOnly
                      value={createdKey.secret_key}
                      className="flex-1 px-3 py-2 border border-blue-300 dark:border-blue-700 rounded bg-white dark:bg-blue-950 text-blue-900 dark:text-blue-300 font-mono text-sm"
                    />
                    <button
                      onClick={() => copyToClipboard(createdKey.secret_key)}
                      className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition flex items-center gap-2"
                    >
                      <FiCopy size={18} /> {keysCopied ? "Copied!" : "Copy"}
                    </button>
                  </div>
                  <button
                    onClick={() => setCreatedKey(null)}
                    className="text-sm text-blue-700 dark:text-blue-400 hover:underline"
                  >
                    I've saved my key
                  </button>
                </div>
              )}

              <div className="space-y-3">
                {apiKeys?.map((key) => (
                  <div key={key.key_id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">{key.name}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Key: {key.key_prefix}...</p>
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        Created: {new Date(key.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRevokeAPIKey(key.key_id)}
                      className="px-3 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/40 transition flex items-center gap-2"
                    >
                      <FiTrash2 size={16} /> Revoke
                    </button>
                  </div>
                ))}
              </div>

              {showNewKeyModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white dark:bg-[#1a2f2f] rounded-lg p-6 max-w-md w-full">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create API Key</h3>
                    <input
                      type="text"
                      placeholder="Key name (e.g., Production Key)"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0a1515] text-gray-900 dark:text-white mb-4"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleCreateAPIKey}
                        className="flex-1 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition"
                      >
                        Create
                      </button>
                      <button
                        onClick={() => {
                          setShowNewKeyModal(false);
                          setNewKeyName("");
                        }}
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : activeTab === "security" ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Two-Factor Authentication</h3>
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {securitySettings?.two_factor_enabled ? "Enabled" : "Disabled"}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {securitySettings?.two_factor_method ? `Method: ${securitySettings.two_factor_method}` : "Not configured"}
                      </p>
                    </div>
                    <button className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition">
                      {securitySettings?.two_factor_enabled ? "Change Method" : "Enable 2FA"}
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Active Sessions</h3>
                <div className="space-y-3">
                  {sessions?.map((session) => (
                    <div key={session.session_id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                          {session.device}
                          {session.is_current && (
                            <span className="px-2 py-1 text-xs bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 rounded">
                              Current
                            </span>
                          )}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">IP: {session.ip_address}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Last active: {new Date(session.last_activity).toLocaleString()}
                        </p>
                      </div>
                      {!session.is_current && (
                        <button
                          onClick={() => handleRevokeSession(session.session_id)}
                          className="px-3 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/40 transition"
                        >
                          Revoke
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleRevokeAllSessions}
                  className="mt-4 px-4 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 transition flex items-center gap-2"
                >
                  <FiLogOut size={18} /> Log Out All Other Devices
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
