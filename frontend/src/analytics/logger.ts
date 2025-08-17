import {
    API_BASE
} from "@/api/client";


type EventName =
  | "page_view"
  | "nav_menu_open"
  | "nav_menu_close"
  | "submenu_toggle"
  | "auth_modal_open"
  | "register_submit"
  | "register_success"
  | "register_fail";

type JSONValue = string | number | boolean | null | JSONValue[] | { [k: string]: JSONValue };


export interface LogEvent {
  name: EventName;
  ts: number;
  props?: Record<string, JSONValue>;
  sid?: string | null;
  user_id?: string | null;
}


interface InitOptions {
  path?: string;
  getAccessToken?: () => string | null | undefined;
}


const STORAGE_KEY = "bs_evt_queue";
const MAX_BATCH = 25;
const FLUSH_INTERVAL = 5000;


function decodeJwt(token?: string | null): Record<string, any> {
  try {
    if (!token) return {};
    const [, raw = ""] = token.split(".");
    if (!raw) return {};

    const base64 = raw.replace(/-/g, "+").replace(/_/g, "/");

    const json = atob(base64);
    return JSON.parse(json);
  } catch {
    return {};
  }
}


function loadQueue(): LogEvent[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as LogEvent[]) : [];
  } catch { return []; }
}


function saveQueue(q: LogEvent[]) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(q)); } catch {}
}


export class Logger {
  private static _instance: Logger | null = null;
  static get i(): Logger { return (this._instance ??= new Logger()); }

  private endpoint = "";
  private getAccessToken: (() => string | null | undefined) | undefined = undefined;

  private queue: LogEvent[] = [];
  private timer: number | null = null;

  init(opts: InitOptions = {}): void {
    const path = (opts.path ?? "/audit/events").replace(/^\/?/, "");
    this.endpoint = new URL(path, API_BASE).toString();
    this.getAccessToken = opts.getAccessToken;
    this.queue = loadQueue();

    this.planFlush();
    window.addEventListener("online", () => this.flushSoon());
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") {
        this.flush({ useBeacon: true }).catch(() => {});
      }
    });

    this.log("page_view", { path: location.pathname, ref: document.referrer || "" });
  }


  log(name: EventName, props?: Record<string, JSONValue>): void {
    const now = Date.now();
    const access = this.getAccessToken?.() ?? null;
    const jwt = decodeJwt(access);

    const base = {
      name,
      ts: now,
      sid: (jwt?.sid as string) ?? null,
      user_id: (jwt?.sub as string) ?? null,
    } as const;

    const ev: LogEvent = props !== undefined ? { ...base, props } : base;

    this.queue.push(ev);
    if (this.queue.length >= MAX_BATCH) this.flushSoon();
    else this.planFlush();
  }


  private planFlush() {
    if (this.timer) return;
    this.timer = window.setTimeout(() => {
      this.timer = null;
      this.flush().catch(() => {});
    }, FLUSH_INTERVAL);
  }
  private flushSoon() {
    if (this.timer) { clearTimeout(this.timer); this.timer = null; }
    void this.flush();
  }


  async flush(opts: { useBeacon?: boolean } = {}): Promise<void> {
    if (!this.queue.length) return;

    const batch = this.queue.splice(0, MAX_BATCH);
    saveQueue(this.queue);

    const access = this.getAccessToken?.() ?? undefined;
    const body = JSON.stringify({ events: batch, access_token: access });

    if (opts.useBeacon && navigator.sendBeacon) {
      const ok = navigator.sendBeacon(this.endpoint, new Blob([body], { type: "application/json" }));
      if (ok) return;
    }

    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (access) headers["Authorization"] = `Bearer ${access}`;

    const res = await fetch(this.endpoint, {
      method: "POST",
      headers,
      body,
      keepalive: !!opts.useBeacon,
      credentials: "include",
    });

    if (!res.ok) {
      this.queue.unshift(...batch);
      saveQueue(this.queue);
      throw new Error(`log failed: ${res.status}`);
    }
  }
}


export const log = (name: EventName, props?: Record<string, JSONValue>) =>
  Logger.i.log(name, props);
