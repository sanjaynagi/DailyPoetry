import { API_BASE_URL, STORAGE_KEYS } from "./constants";
import { mockDailyPoem } from "./mockData";
import { readJson, writeJson } from "./storage";
import type { DailyPoemResponse, FavouritePoem } from "../types/poetry";

export class AuthNotConfiguredError extends Error {
  constructor() {
    super("Auth token is not configured for favourites endpoints");
    this.name = "AuthNotConfiguredError";
  }
}

type RawFavourite = {
  poem_id?: string;
  poemId?: string;
  title?: string;
  author?: string;
  date_featured?: string;
  dateFeatured?: string;
};

function getAuthToken(): string | null {
  const fromStorage = localStorage.getItem(STORAGE_KEYS.authToken);
  if (fromStorage && fromStorage.trim()) {
    return fromStorage;
  }

  const fromEnv = import.meta.env.VITE_AUTH_TOKEN;
  if (typeof fromEnv === "string" && fromEnv.trim()) {
    return fromEnv;
  }

  return null;
}

function authHeaders(): Record<string, string> {
  const token = getAuthToken();
  if (!token) {
    throw new AuthNotConfiguredError();
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

function normalizeFavourite(item: RawFavourite): FavouritePoem | null {
  const poemId = item.poem_id ?? item.poemId;
  if (!poemId) {
    return null;
  }

  return {
    poemId,
    title: item.title ?? "Untitled",
    author: item.author ?? "Unknown Author",
    dateFeatured: item.date_featured ?? item.dateFeatured ?? "",
  };
}

export async function fetchDailyPoem(): Promise<{ data: DailyPoemResponse; fromCache: boolean }> {
  const endpoint = `${API_BASE_URL}/v1/daily`;

  try {
    const response = await fetch(endpoint, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`daily endpoint returned ${response.status}`);
    }

    const data = (await response.json()) as DailyPoemResponse;
    writeJson(STORAGE_KEYS.cachedDaily, data);
    return { data, fromCache: false };
  } catch {
    const cached = readJson<DailyPoemResponse>(STORAGE_KEYS.cachedDaily);
    if (cached) {
      return { data: cached, fromCache: true };
    }

    writeJson(STORAGE_KEYS.cachedDaily, mockDailyPoem);
    return { data: mockDailyPoem, fromCache: true };
  }
}

export async function fetchFavourites(): Promise<FavouritePoem[]> {
  const endpoint = `${API_BASE_URL}/v1/me/favourites`;
  const response = await fetch(endpoint, {
    headers: {
      Accept: "application/json",
      ...authHeaders(),
    },
  });

  if (!response.ok) {
    throw new Error(`favourites endpoint returned ${response.status}`);
  }

  const payload = (await response.json()) as unknown;
  const rawItems = Array.isArray(payload)
    ? payload
    : typeof payload === "object" && payload !== null && "favourites" in payload
      ? (payload as { favourites: unknown }).favourites
      : [];

  if (!Array.isArray(rawItems)) {
    return [];
  }

  return rawItems
    .map((item) => (typeof item === "object" && item !== null ? normalizeFavourite(item as RawFavourite) : null))
    .filter((item): item is FavouritePoem => item !== null);
}

export async function createFavourite(poemId: string): Promise<void> {
  const endpoint = `${API_BASE_URL}/v1/me/favourites`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ poem_id: poemId }),
  });

  if (!response.ok) {
    throw new Error(`create favourite endpoint returned ${response.status}`);
  }
}
