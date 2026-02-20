export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const STORAGE_KEYS = {
  cachedDaily: "daily-poetry.cached-daily",
  favourites: "daily-poetry.favourites",
  authToken: "daily-poetry.auth-token",
  theme: "daily-poetry.theme",
};
