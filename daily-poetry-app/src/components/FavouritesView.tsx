import type { FavouritePoem } from "../types/poetry";
import { formatIsoDate } from "../lib/date";

type FavouritesViewProps = {
  favourites: FavouritePoem[];
  loading: boolean;
  error: string | null;
  theme: "light" | "dark";
};

export function FavouritesView({ favourites, loading, error, theme }: FavouritesViewProps) {
  const topLogoSrc = theme === "dark" ? "/dailypoetry-light.png" : "/dailypoetry-dark.png";

  return (
    <>
      <div className="top-logo-wrap">
        <img className="top-logo" src={topLogoSrc} alt="DailyPoetry" />
      </div>
      <section className="panel">
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
    </>
  );
}
