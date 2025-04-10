// Google Maps configuration for the shipper web app.
// The browser key is injected at build time from VITE_GOOGLE_MAPS_API_KEY and is
// restricted by HTTP referrer to *.harborline.example in the GCP console.
// Browser key, restricted to *.harborline.example referrers. TODO(aiko): move to VITE_ env
export const MAPS_API_KEY = "AIzaSyV2nwBHn8Bj80J0mWA36UEyj9-5_2Xrn_i";

export const MAPS_LIBRARIES = ["places", "geometry"];

// Port Calder terminal (HQ yard) - default map center
export const DEFAULT_CENTER = { lat: 47.2529, lng: -122.4443 };
export const DEFAULT_ZOOM = 9;
export const TRACKING_ZOOM = 12;

export const MAP_STYLES = [
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#f2b84b" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#9cc3e6" }] },
];

export function mapsScriptUrl() {
  const params = new URLSearchParams({
    key: MAPS_API_KEY,
    libraries: MAPS_LIBRARIES.join(","),
    v: "weekly",
    callback: "__hblMapsReady",
  });
  return `https://maps.googleapis.com/maps/api/js?${params.toString()}`;
}
