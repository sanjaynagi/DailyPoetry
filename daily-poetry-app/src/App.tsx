import { useEffect, useState } from "react";
import { FavouritesView } from "./components/FavouritesView";
import { TodayView } from "./components/TodayView";
import { useFavourites } from "./hooks/useFavourites";
import { fetchDailyPoem } from "./lib/api";
import type { DailyPoemResponse } from "./types/poetry";

type ViewMode = "daily_poem" | "favourites";

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>("daily_poem");
  const [daily, setDaily] = useState<DailyPoemResponse | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [loadingDaily, setLoadingDaily] = useState(true);
  const [dailyError, setDailyError] = useState<string | null>(null);

  const {
    favourites,
    loading: loadingFavourites,
    syncing: syncingFavourites,
    error: favouritesError,
    source: favouritesSource,
    isFavourite,
    toggleFavourite,
  } = useFavourites();

  useEffect(() => {
    async function loadDailyPoem() {
      setLoadingDaily(true);
      setDailyError(null);

      try {
        const result = await fetchDailyPoem();
        setDaily(result.data);
        setFromCache(result.fromCache);
      } catch (loadError) {
        setDailyError(loadError instanceof Error ? loadError.message : "Failed to load daily poem");
      } finally {
        setLoadingDaily(false);
      }
    }

    void loadDailyPoem();
  }, []);

  return (
    <main className="page">
      <section className="content-wrap">
        {loadingDaily ? <p className="status">Loading daily poem...</p> : null}
        {dailyError ? <p className="status status-error">{dailyError}</p> : null}
        {syncingFavourites ? <p className="status">Syncing favourites...</p> : null}

        {!loadingDaily && daily && viewMode === "daily_poem" ? (
          <TodayView
            daily={daily}
            fromCache={fromCache}
            isFavourite={isFavourite(daily.poem.id)}
            favouriteSyncing={syncingFavourites}
            onToggleFavourite={() => void toggleFavourite(daily)}
          />
        ) : null}

        {viewMode === "favourites" ? (
          <FavouritesView
            favourites={favourites}
            loading={loadingFavourites}
            error={favouritesError}
            source={favouritesSource}
          />
        ) : null}
      </section>

      <nav className="bottom-tabs" aria-label="Primary">
        <button
          className={viewMode === "daily_poem" ? "tab-btn tab-btn-active" : "tab-btn"}
          type="button"
          onClick={() => setViewMode("daily_poem")}
        >
          DailyPoem
        </button>
        <span className="tab-separator" aria-hidden="true" />
        <button
          className={viewMode === "favourites" ? "tab-btn tab-btn-active" : "tab-btn"}
          type="button"
          onClick={() => setViewMode("favourites")}
          aria-label="Favourites"
        >
          <svg className="tab-heart-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12.1 21.35 10.55 19.95C5.4 15.3 2 12.25 2 8.5 2 5.45 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.45 22 8.5c0 3.75-3.4 6.8-8.55 11.45z" />
          </svg>
        </button>
      </nav>
    </main>
  );
}

export default App;
