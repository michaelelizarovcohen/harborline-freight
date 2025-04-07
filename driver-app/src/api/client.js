import Constants from "expo-constants";
import * as SecureStore from "expo-secure-store";

export const API_BASE = Constants.expoConfig?.extra?.apiBaseUrl || "https://api.harborline.example";
const SESSION_KEY = "hbl_driver_session";

let cached = null;

export async function loadSession() {
  if (cached) return cached;
  const raw = await SecureStore.getItemAsync(SESSION_KEY);
  cached = raw ? JSON.parse(raw) : null;
  if (cached && Date.parse(cached.expires_at) < Date.now()) {
    await clearSession();
    return null;
  }
  return cached;
}

export async function saveSession(session) {
  cached = session;
  await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify(session));
}

export async function clearSession() {
  cached = null;
  await SecureStore.deleteItemAsync(SESSION_KEY);
}

export function currentSessionToken() {
  return cached?.token || null;
}

async function request(method, path, body, { headers = {}, raw = false } = {}) {
  const token = currentSessionToken();
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      Accept: "application/json",
      ...(body && !(body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "X-Client": `harborline-driver/${Constants.expoConfig?.version || "dev"}`,
      ...headers,
    },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) {
    await clearSession();
  }
  if (raw) return res;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(data?.error || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  get: (p) => request("GET", p),
  post: (p, b, o) => request("POST", p, b, o),
  patch: (p, b) => request("PATCH", p, b),
};

export async function signIn(phone, pin) {
  const data = await api.post("/v1/drivers/login", { phone, pin });
  await saveSession({ token: data.token, expires_at: data.expires_at, driver: data.driver });
  return loadSession();
}
