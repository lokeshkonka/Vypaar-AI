export const API_BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function initUser(token: string) {
  try {
    const res = await fetch(`${API_BASE}/users/init`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok && res.status !== 404) {
      throw new Error("Failed to initialize user");
    }

    if (res.status === 404) {
      console.info("User init endpoint not yet available on backend");
      return null;
    }

    return res.json();
  } catch (error) {
    // Log but don't throw - user sync is not critical
    console.warn("User sync error (non-critical):", error);
    return null;
  }
}
