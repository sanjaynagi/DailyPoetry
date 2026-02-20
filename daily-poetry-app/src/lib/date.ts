export function formatIsoDate(isoDate: string, format: "long" | "short" = "long"): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate);
  if (!match) {
    return isoDate;
  }

  const year = Number(match[1]);
  const monthIndex = Number(match[2]) - 1;
  const day = Number(match[3]);
  const utcDate = new Date(Date.UTC(year, monthIndex, day));

  const options: Intl.DateTimeFormatOptions =
    format === "long"
      ? { weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }
      : { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" };

  return new Intl.DateTimeFormat("en-GB", options).format(utcDate);
}
