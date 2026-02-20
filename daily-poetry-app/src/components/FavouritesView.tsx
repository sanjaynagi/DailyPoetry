import type { FavouritePoem, FavouritesSource } from "../types/poetry";

type FavouritesViewProps = {
  favourites: FavouritePoem[];
  loading: boolean;
  error: string | null;
  source: FavouritesSource;
};

export function FavouritesView({ favourites, loading, error, source }: FavouritesViewProps) {
  return (
    <section className="panel">
      <h2 className="section-title">Favourites</h2>
      <p className="section-subtitle">Source: {source === "remote" ? "Backend" : "Local cache"}</p>
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
                    {item.author} · {item.dateFeatured}
                  </p>
                </summary>
                {item.poemText ? <pre className="favourite-poem-text">{item.poemText}</pre> : null}
              </details>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
