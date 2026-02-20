import { useEffect, useState } from "react";
import {
  createNotificationSubscription,
  deleteNotificationSubscription,
  fetchNotificationPreference,
  updateNotificationPreference,
} from "../lib/api";
import { VAPID_PUBLIC_KEY } from "../lib/constants";
import type { NotificationPreference } from "../types/poetry";

type NotificationState = {
  supported: boolean;
  enabled: boolean;
  loading: boolean;
  syncing: boolean;
  error: string | null;
};

function toUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  const output = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i += 1) {
    output[i] = rawData.charCodeAt(i);
  }
  return output;
}

function toBase64(key: ArrayBuffer | null): string {
  if (!key) {
    return "";
  }
  const bytes = new Uint8Array(key);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

function browserSupportsNotifications(): boolean {
  return "Notification" in window && "serviceWorker" in navigator && "PushManager" in window;
}

function defaultPreference(): NotificationPreference {
  const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return {
    enabled: false,
    time_zone: zone || "UTC",
    local_hour: 9,
  };
}

export function useNotifications() {
  const [preference, setPreference] = useState<NotificationPreference>(defaultPreference);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const supported = browserSupportsNotifications();

  useEffect(() => {
    if (!supported) {
      setLoading(false);
      return;
    }

    async function loadPreference() {
      setLoading(true);
      setError(null);

      try {
        const remote = await fetchNotificationPreference();
        setPreference(remote);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load notification preferences");
      } finally {
        setLoading(false);
      }
    }

    void loadPreference();
  }, [supported]);

  async function enableNotifications(): Promise<void> {
    if (!supported) {
      setError("Notifications are not supported in this browser.");
      return;
    }
    if (!VAPID_PUBLIC_KEY.trim()) {
      setError("Notifications are not configured for this environment.");
      return;
    }

    setSyncing(true);
    setError(null);

    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        throw new Error("Notification permission was not granted.");
      }

      const registration = await navigator.serviceWorker.ready;
      let subscription = await registration.pushManager.getSubscription();
      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: toUint8Array(VAPID_PUBLIC_KEY) as BufferSource,
        });
      }

      await createNotificationSubscription({
        endpoint: subscription.endpoint,
        keys: {
          p256dh: toBase64(subscription.getKey("p256dh")),
          auth: toBase64(subscription.getKey("auth")),
        },
      });

      const nextPreference = await updateNotificationPreference({
        enabled: true,
        time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone || preference.time_zone || "UTC",
        local_hour: preference.local_hour,
      });
      setPreference(nextPreference);
    } catch (enableError) {
      setError(enableError instanceof Error ? enableError.message : "Failed to enable notifications");
    } finally {
      setSyncing(false);
    }
  }

  async function disableNotifications(): Promise<void> {
    if (!supported) {
      return;
    }

    setSyncing(true);
    setError(null);

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        await deleteNotificationSubscription(subscription.endpoint);
        await subscription.unsubscribe();
      }

      const nextPreference = await updateNotificationPreference({
        enabled: false,
        time_zone: preference.time_zone,
        local_hour: preference.local_hour,
      });
      setPreference(nextPreference);
    } catch (disableError) {
      setError(disableError instanceof Error ? disableError.message : "Failed to disable notifications");
    } finally {
      setSyncing(false);
    }
  }

  async function toggleNotifications(): Promise<void> {
    if (preference.enabled) {
      await disableNotifications();
      return;
    }
    await enableNotifications();
  }

  const permissionState = supported ? Notification.permission : "denied";

  const state: NotificationState = {
    supported,
    enabled: preference.enabled,
    loading,
    syncing,
    error,
  };

  return {
    ...state,
    permissionState,
    toggleNotifications,
  };
}
