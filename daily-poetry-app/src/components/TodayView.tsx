import type { DailyPoemResponse } from "../types/poetry";
import { formatIsoDate } from "../lib/date";

type TodayViewProps = {
  daily: DailyPoemResponse;
  isFavourite: boolean;
  theme: "light" | "dark";
  favouriteSyncing: boolean;
  notificationsSupported: boolean;
  notificationsEnabled: boolean;
  notificationsLoading: boolean;
  notificationsSyncing: boolean;
  notificationsError: string | null;
  onToggleFavourite: () => void;
  onToggleNotifications: () => void;
};

export function TodayView({
  daily,
  isFavourite,
  theme,
  favouriteSyncing,
  notificationsSupported,
  notificationsEnabled,
  notificationsLoading,
  notificationsSyncing,
  notificationsError,
  onToggleFavourite,
  onToggleNotifications,
}: TodayViewProps) {
  const topLogoSrc = theme === "dark" ? "/dailypoetry-light.png" : "/dailypoetry-dark.png";
  const formattedDate = formatIsoDate(daily.date, "long");

  return (
    <>
      <div className="top-logo-wrap">
        <img className="top-logo" src={topLogoSrc} alt="DailyPoetry" />
      </div>
      <section className="panel">
        <p className="date-label">{formattedDate}</p>

        <div className="poem-card-wrap">
          <article className="poem-card">
            <h1 className="poem-title">{daily.poem.title}</h1>
            <pre className="poem-text">{daily.poem.text}</pre>
          </article>

          <button
            className={isFavourite ? "heart-button heart-button-active" : "heart-button"}
            type="button"
            aria-label={isFavourite ? "Remove favourite" : "Add favourite"}
            title={isFavourite ? "Remove favourite" : "Add favourite"}
            onClick={onToggleFavourite}
            disabled={favouriteSyncing}
          >
            {favouriteSyncing ? (
              "..."
            ) : (
              <svg className="heart-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12.1 21.35 10.55 19.95C5.4 15.3 2 12.25 2 8.5 2 5.45 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.45 22 8.5c0 3.75-3.4 6.8-8.55 11.45z" />
              </svg>
            )}
          </button>
        </div>

        <section className="notification-panel" aria-label="Daily reminders">
          <div className="notification-row">
            <span className="notification-label">Daily reminders</span>
            <button
              className={notificationsEnabled ? "notification-toggle notification-toggle-active" : "notification-toggle"}
              type="button"
              onClick={onToggleNotifications}
              disabled={!notificationsSupported || notificationsLoading || notificationsSyncing}
            >
              {notificationsSyncing ? "..." : notificationsEnabled ? "On" : "Off"}
            </button>
          </div>
          {!notificationsSupported ? <p className="notification-note">Notifications are not supported here.</p> : null}
          {notificationsError ? <p className="status status-error">{notificationsError}</p> : null}
        </section>

        <footer className="author-panel">
          <div className="author-block">
            {daily.author.image_url ? (
              <img className="author-image" src={daily.author.image_url} alt={daily.author.name} />
            ) : null}
            <div>
              <p className="author-name">{daily.author.name}</p>
              <p className="author-bio">{daily.author.bio_short}</p>
            </div>
          </div>
        </footer>
      </section>
    </>
  );
}
