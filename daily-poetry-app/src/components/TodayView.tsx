import type { DailyPoemResponse } from "../types/poetry";

type TodayViewProps = {
  daily: DailyPoemResponse;
  isFavourite: boolean;
  fromCache: boolean;
  favouriteSyncing: boolean;
  onToggleFavourite: () => void;
};

export function TodayView({
  daily,
  isFavourite,
  fromCache,
  favouriteSyncing,
  onToggleFavourite,
}: TodayViewProps) {
  return (
    <section className="panel">
      <header className="panel-header">
        <p className="date-label">{daily.date}</p>
        {fromCache ? <p className="offline-chip">Offline / cached</p> : null}
      </header>

      <h1 className="poem-title">{daily.poem.title}</h1>

      <pre className="poem-text">{daily.poem.text}</pre>

      <footer className="author-block">
        {daily.author.image_url ? (
          <img className="author-image" src={daily.author.image_url} alt={daily.author.name} />
        ) : null}
        <div>
          <p className="author-name">{daily.author.name}</p>
          <p className="author-bio">{daily.author.bio_short}</p>
        </div>
      </footer>

      <button
        className={isFavourite ? "heart-button heart-button-active" : "heart-button"}
        type="button"
        aria-label={isFavourite ? "Remove favourite" : "Add favourite"}
        title={isFavourite ? "Remove favourite" : "Add favourite"}
        onClick={onToggleFavourite}
        disabled={favouriteSyncing}
      >
        {favouriteSyncing ? "..." : isFavourite ? "♥" : "♡"}
      </button>
    </section>
  );
}
