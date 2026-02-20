export type DailyPoemResponse = {
  date: string;
  poem: {
    id: string;
    title: string;
    text: string;
    linecount: number;
  };
  author: {
    id: string;
    name: string;
    bio_short: string;
    image_url: string;
  };
};

export type FavouritePoem = {
  poemId: string;
  title: string;
  author: string;
  dateFeatured: string;
  poemText?: string;
};

export type FavouritesSource = "remote" | "local";
