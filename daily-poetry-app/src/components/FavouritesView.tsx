import type { FavouritePoem } from "../types/poetry";
import { formatIsoDate } from "../lib/date";

type FavouritesViewProps = {
  favourites: FavouritePoem[];
  loading: boolean;
  error: string | null;
  theme: "light" | "dark";
  notificationsSupported: boolean;
  notificationsEnabled: boolean;
  notificationsLoading: boolean;
  notificationsSyncing: boolean;
  notificationsError: string | null;
  onToggleNotifications: () => void;
};

export function FavouritesView({
  favourites,
  loading,
  error,
  theme,
  notificationsSupported,
  notificationsEnabled,
  notificationsLoading,
  notificationsSyncing,
  notificationsError,
  onToggleNotifications,
}: FavouritesViewProps) {
  const topLogoSrc = theme === "dark" ? "/dailypoetry-light.png" : "/dailypoetry-dark.png";

  return (
    <>
      <div className="top-logo-wrap">
        <img className="top-logo" src={topLogoSrc} alt="daily-poetry" />
      </div>
      <section className="panel">
        <section className="notification-panel" aria-label="Daily reminders">
          <div className="notification-row">
            <span className="notification-label">Daily reminder</span>
            <button
              className={notificationsEnabled ? "notification-switch notification-switch-active" : "notification-switch"}
              type="button"
              role="switch"
              aria-checked={notificationsEnabled}
              aria-label={notificationsEnabled ? "Disable daily reminder" : "Enable daily reminder"}
              onClick={onToggleNotifications}
              disabled={!notificationsSupported || notificationsLoading || notificationsSyncing}
            >
              <span className="notification-switch-track" aria-hidden="true">
                <span className="notification-switch-thumb" />
              </span>
            </button>
          </div>
          {notificationsSyncing ? <p className="notification-note">Updating reminder...</p> : null}
          {!notificationsSupported ? <p className="notification-note">Notifications are not supported here.</p> : null}
          {notificationsError ? <p className="status status-error">{notificationsError}</p> : null}
        </section>
        <section className="favourites-box" aria-label="Favourites">
          <h2 className="section-title">Favourites</h2>
          {loading ? <p className="status">Loading favourites...</p> : null}
          {error ? <p className="status status-error">{error}</p> : null}

          {!loading && favourites.length === 0 ? (
            <p className="empty-state">No favourites yet.</p>
          ) : (
            <ul className="favourites-list">
              {favourites.map((item) => (
                <li className="favourite-row" key={item.poemId}>
                  <details>
                    <summary className="favourite-summary">
                      <p className="favourite-title">{item.title}</p>
                      <p className="favourite-meta">
                        {item.author} · {formatIsoDate(item.dateFeatured, "short")}
                      </p>
                    </summary>
                    {item.poemText ? <pre className="favourite-poem-text">{item.poemText}</pre> : null}
                  </details>
                </li>
              ))}
            </ul>
          )}
        </section>
      </section>
    </>
  );
}
