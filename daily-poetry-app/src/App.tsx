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
          ♥
        </button>
      </nav>
    </main>
  );
}

export default App;
