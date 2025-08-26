export function labelizeCategory(key?: string | null): string {
  const safe = (key ?? "").toString();

  return safe
    .replace(/_/g, " ")
    .trim()
    .split(/\s+/) // режем по одному или нескольким пробелам
    .map(w => (w ? w.charAt(0).toUpperCase() + w.slice(1) : "")) // без s[0]
    .join(" ");
}
