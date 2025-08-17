function normalize(base: string): string {
  return (base || "").replace(/\/+$/, "") + "/";
}


function join(base: string, path: string): string {
  return normalize(base) + path.replace(/^\/+/, "");
}


export const API_BASE = (import.meta.env.VITE_API_BASE as string) || "";


if (!API_BASE || !/^https?:\/\//i.test(API_BASE)) {
  throw new Error(
    "[client] VITE_API_BASE is not set or invalid. " +
      "Set NGINX_HOST/NGINX_PORT in your .env and restart Vite."
  );
}


export async function apiFetch<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {}
): Promise<T> {
  const url = join(API_BASE, path);
  const headers = new Headers(init.headers || {});
  const { json, ...rest } = init;

  if (json !== undefined) headers.set("Content-Type", "application/json");

  const res = await fetch(url, {
    ...rest,
    headers,
    ...(json !== undefined ? { body: JSON.stringify(json) } : {}),
    credentials: "include",
  });

  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : await res.text();

  if (!res.ok) {
    const err = new Error(typeof data === "string" ? data : `HTTP ${res.status}`) as
      Error & { status?: number; body?: unknown };
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data as T;
}