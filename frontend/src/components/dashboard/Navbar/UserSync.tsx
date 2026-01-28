import { useEffect, useRef } from "react";
import { useAuth } from "@clerk/clerk-react";
import { initUser } from "../../../lib/api";


export default function UserSync() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const hasSynced = useRef(false);

  useEffect(() => {
    if (!isLoaded || !isSignedIn || hasSynced.current) return;

    const sync = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        await initUser(token);
        hasSynced.current = true;
      } catch (err) {
        // Non-critical error - still mark as synced to avoid retrying
        console.warn("Backend user sync warning (non-critical):", err);
        hasSynced.current = true;
      }
    };

    sync();
  }, [isLoaded, isSignedIn, getToken]);

  return null; 
}
