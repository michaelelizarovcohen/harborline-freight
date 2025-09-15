// Lightweight crash reporter for Harborline Driver.
// Captures unhandled JS errors and posts them to the API, which forwards a
// summary to the #driver-app-crashes channel. No third-party SDK on purpose
// (drivers are on metered data plans).
import * as Device from "expo-device";
import Constants from "expo-constants";
import { API_BASE, currentSessionToken } from "../api/client";

const MAX_STACK = 4000;
let installed = false;

function devicePayload() {
  return {
    brand: Device.brand,
    model: Device.modelName,
    os: `${Device.osName} ${Device.osVersion}`,
    app_version: Constants.expoConfig?.version,
    build: Constants.expoConfig?.ios?.buildNumber || Constants.expoConfig?.android?.versionCode,
  };
}

export async function reportCrash(error, { fatal = false, context = {} } = {}) {
  const token = currentSessionToken();
  try {
    await fetch(`${API_BASE}/v1/drivers/crash-reports`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message: String(error?.message || error),
        stack: String(error?.stack || "").slice(0, MAX_STACK),
        fatal,
        context,
        device: devicePayload(),
        occurred_at: new Date().toISOString(),
      }),
    });
  } catch (e) {
    // Never let crash reporting crash the app.
    console.warn("crash report failed", e);
  }
}

export function installCrashReporter() {
  if (installed || !global.ErrorUtils) return;
  installed = true;
  const previous = global.ErrorUtils.getGlobalHandler();
  global.ErrorUtils.setGlobalHandler((error, isFatal) => {
    reportCrash(error, { fatal: Boolean(isFatal) }).finally(() => previous?.(error, isFatal));
  });
}
