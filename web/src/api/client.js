// Thin fetch wrapper around the Harborline Book API.
// The session token comes from POST /v1/auth/login and lives in sessionStorage
// (not localStorage - see SEC-112, tokens must not survive the tab).

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
const STORAGE_KEY = "hbl.session";

export const session = {
  get() {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY));
    } catch {
      return null;
    }
  },
  set(value) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  },
  clear() {
    sessionStorage.removeItem(STORAGE_KEY);
  },
  isAuthenticated() {
    const s = this.get();
    return Boolean(s && s.expires_at && Date.parse(s.expires_at) > Date.now());
  },
};

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.error || `Request failed with status ${status}`);
    this.status = status;
    this.body = body;
  }
}

async function request(method, path, { body, query, signal } = {}) {
  const url = new URL(API_BASE + path, window.location.origin);
  if (query) {
    Object.entries(query)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const headers = { Accept: "application/json" };
  const current = session.get();
  if (current?.token) {
    headers.Authorization = `Bearer ${current.token}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
    credentials: "include",
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401) session.clear();
    throw new ApiError(res.status, data);
  }
  return data;
}

export const api = {
  get: (path, opts) => request("GET", path, opts),
  post: (path, body, opts) => request("POST", path, { ...opts, body }),
  patch: (path, body, opts) => request("PATCH", path, { ...opts, body }),
  delete: (path, opts) => request("DELETE", path, opts),
};

export async function login(email, password) {
  const data = await api.post("/v1/auth/login", { email, password });
  session.set({ token: data.token, expires_at: data.expires_at });
  return data.account;
}
