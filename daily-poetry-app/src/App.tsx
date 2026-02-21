import { useEffect, useState } from "react";
import { FavouritesView } from "./components/FavouritesView";
import { TodayView } from "./components/TodayView";
import { useFavourites } from "./hooks/useFavourites";
import { useNotifications } from "./hooks/useNotifications";
import { fetchDailyPoem } from "./lib/api";
import { STORAGE_KEYS } from "./lib/constants";
import type { DailyPoemResponse } from "./types/poetry";

type ViewMode = "daily_poem" | "favourites";
type ThemeMode = "light" | "dark";

function getInitialTheme(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEYS.theme);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>("daily_poem");
  const [theme, setTheme] = useState<ThemeMode>(getInitialTheme);
  const [daily, setDaily] = useState<DailyPoemResponse | null>(null);
  const [loadingDaily, setLoadingDaily] = useState(true);
  const [dailyError, setDailyError] = useState<string | null>(null);

  const {
    favourites,
    loading: loadingFavourites,
    syncing: syncingFavourites,
    error: favouritesError,
    isFavourite,
    toggleFavourite,
  } = useFavourites();
  const {
    supported: notificationsSupported,
    enabled: notificationsEnabled,
    loading: notificationsLoading,
    syncing: notificationsSyncing,
    error: notificationsError,
    toggleNotifications,
  } = useNotifications();

  useEffect(() => {
    async function loadDailyPoem() {
      setLoadingDaily(true);
      setDailyError(null);

      try {
        const result = await fetchDailyPoem();
        setDaily(result.data);
      } catch (loadError) {
        setDailyError(loadError instanceof Error ? loadError.message : "Failed to load daily poem");
      } finally {
        setLoadingDaily(false);
      }
    }

    void loadDailyPoem();
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(STORAGE_KEYS.theme, theme);
  }, [theme]);

  const dailyPoemLogoSrc = theme === "dark" ? "/dailypoetry-light.png" : "/dailypoetry-dark.png";

  return (
    <main className="page">
      <button
        className={theme === "dark" ? "theme-toggle app-theme-toggle theme-toggle-dark" : "theme-toggle app-theme-toggle"}
        type="button"
        onClick={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
        aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
        title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
      >
        <span className="theme-toggle-track" aria-hidden="true">
          <span className="theme-toggle-icon">☀</span>
          <span className="theme-toggle-icon">☾</span>
          <span className="theme-toggle-thumb" />
        </span>
      </button>
      <section className="content-wrap">
        {loadingDaily ? (
          <section className="loading-splash" aria-label="Loading">
            <div className="loading-shell">
              <img className="loading-logo" src="/logo-transparent.png" alt="daily-poetry" />
              <p className="loading-title">Loading today's poem</p>
              <p className="loading-subtitle">Waking up the API server. This can take a few seconds.</p>
              <div className="loading-progress" aria-hidden="true">
                <span className="loading-progress-fill" />
              </div>
            </div>
          </section>
        ) : null}
        {dailyError ? <p className="status status-error">{dailyError}</p> : null}
        {syncingFavourites ? <p className="status">Syncing favourites...</p> : null}

        {!loadingDaily && daily && viewMode === "daily_poem" ? (
          <TodayView
            daily={daily}
            theme={theme}
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
            theme={theme}
            notificationsSupported={notificationsSupported}
            notificationsEnabled={notificationsEnabled}
            notificationsLoading={notificationsLoading}
            notificationsSyncing={notificationsSyncing}
            notificationsError={notificationsError}
            onToggleNotifications={() => void toggleNotifications()}
          />
        ) : null}
      </section>

      <nav className="bottom-tabs" aria-label="Primary">
        <button
          className={viewMode === "daily_poem" ? "tab-btn tab-btn-active" : "tab-btn"}
          type="button"
          onClick={() => setViewMode("daily_poem")}
          aria-label="DailyPoem"
        >
          <img className="tab-logo" src={dailyPoemLogoSrc} alt="daily-poetry" />
        </button>
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
