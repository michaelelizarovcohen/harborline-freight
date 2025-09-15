// Background location pings while a driver is on an active job.
// Pings are batched and sent every ~2 minutes to save battery/data.
import * as Location from "expo-location";
import * as TaskManager from "expo-task-manager";
import { api } from "../api/client";

export const LOCATION_TASK = "hbl-location-pings";
const queue = [];
let activeJobId = null;

TaskManager.defineTask(LOCATION_TASK, async ({ data, error }) => {
  if (error || !activeJobId) return;
  const { locations = [] } = data || {};
  locations.forEach((loc) =>
    queue.push({
      lat: loc.coords.latitude,
      lng: loc.coords.longitude,
      speed_mps: loc.coords.speed,
      heading: loc.coords.heading,
      accuracy_m: loc.coords.accuracy,
      recorded_at: new Date(loc.timestamp).toISOString(),
    })
  );
  await flush();
});

async function flush() {
  if (!queue.length || !activeJobId) return;
  const batch = queue.splice(0, queue.length);
  try {
    await api.post(`/v1/drivers/jobs/${activeJobId}/positions`, { positions: batch });
  } catch (e) {
    // put them back; we'll retry on the next tick
    queue.unshift(...batch.slice(-200));
  }
}

export async function startTracking(jobId) {
  const fg = await Location.requestForegroundPermissionsAsync();
  if (fg.status !== "granted") throw new Error("Location permission is required for active jobs.");
  const bg = await Location.requestBackgroundPermissionsAsync();
  activeJobId = jobId;
  if (bg.status !== "granted") return false;
  await Location.startLocationUpdatesAsync(LOCATION_TASK, {
    accuracy: Location.Accuracy.Balanced,
    timeInterval: 120000,
    distanceInterval: 250,
    deferredUpdatesInterval: 120000,
    showsBackgroundLocationIndicator: true,
    foregroundService: {
      notificationTitle: "Harborline Driver",
      notificationBody: "Sharing location for your active load",
      notificationColor: "#0b2f45",
    },
  });
  return true;
}

export async function stopTracking() {
  await flush();
  activeJobId = null;
  if (await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK)) {
    await Location.stopLocationUpdatesAsync(LOCATION_TASK);
  }
}
