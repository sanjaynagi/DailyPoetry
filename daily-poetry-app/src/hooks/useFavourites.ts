import { useEffect, useMemo, useState } from "react";
import { AuthNotConfiguredError, createFavourite, fetchFavourites } from "../lib/api";
import { STORAGE_KEYS } from "../lib/constants";
import { readJson, writeJson } from "../lib/storage";
import type { DailyPoemResponse, FavouritePoem, FavouritesSource } from "../types/poetry";

function toFavourite(daily: DailyPoemResponse): FavouritePoem {
  return {
    poemId: daily.poem.id,
    title: daily.poem.title,
    author: daily.author.name,
    dateFeatured: daily.date,
  };
}

export function useFavourites() {
  const [favourites, setFavourites] = useState<FavouritePoem[]>(() =>
    readJson<FavouritePoem[]>(STORAGE_KEYS.favourites) ?? [],
  );
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<FavouritesSource>("local");

  const favouriteIds = useMemo(() => new Set(favourites.map((item) => item.poemId)), [favourites]);

  useEffect(() => {
    async function loadFavourites() {
      setLoading(true);
      setError(null);

      try {
        const remoteFavourites = await fetchFavourites();
        setFavourites(remoteFavourites);
        setSource("remote");
        writeJson(STORAGE_KEYS.favourites, remoteFavourites);
      } catch (loadError) {
        const local = readJson<FavouritePoem[]>(STORAGE_KEYS.favourites) ?? [];
        setFavourites(local);
        setSource("local");

        if (loadError instanceof AuthNotConfiguredError) {
          setError("Auth token not configured; using local favourites.");
        } else {
          setError(loadError instanceof Error ? loadError.message : "Failed to load favourites");
        }
      } finally {
        setLoading(false);
      }
    }

    void loadFavourites();
  }, []);

  async function toggleFavourite(daily: DailyPoemResponse): Promise<void> {
    const favourite = toFavourite(daily);
    const exists = favourites.some((item) => item.poemId === favourite.poemId);

    setError(null);
    setSyncing(true);

    if (!exists) {
      try {
        await createFavourite(favourite.poemId);
        setSource("remote");
      } catch (syncError) {
        if (syncError instanceof AuthNotConfiguredError) {
          setSource("local");
          setError("Auth token not configured; saved favourite locally only.");
        } else {
          setError(syncError instanceof Error ? syncError.message : "Failed to create favourite");
        }
      }
    }

    setFavourites((current) => {
      const isInCurrent = current.some((item) => item.poemId === favourite.poemId);
      const next = isInCurrent
        ? current.filter((item) => item.poemId !== favourite.poemId)
        : [favourite, ...current];
      writeJson(STORAGE_KEYS.favourites, next);
      return next;
    });

    setSyncing(false);
  }

  return {
    favourites,
    loading,
    syncing,
    error,
    source,
    isFavourite: (poemId: string) => favouriteIds.has(poemId),
    toggleFavourite,
  };
}
