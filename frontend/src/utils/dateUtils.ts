function formatDate(isoDateString: string | undefined | null): string {
  if (!isoDateString) return "";
  const date = new Date(isoDateString);
  if (isNaN(date.getTime())) return isoDateString;
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export { formatDate };
