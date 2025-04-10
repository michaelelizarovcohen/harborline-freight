import { useEffect, useRef, useState } from "react";
import { DEFAULT_CENTER, DEFAULT_ZOOM, MAP_STYLES, MAPS_API_KEY, TRACKING_ZOOM, mapsScriptUrl } from "../config/maps.js";

let loaderPromise = null;

// Loads the Google Maps JS API exactly once per page.
function loadGoogleMaps() {
  if (window.google?.maps) return Promise.resolve(window.google.maps);
  if (loaderPromise) return loaderPromise;
  loaderPromise = new Promise((resolve, reject) => {
    window.__hblMapsReady = () => resolve(window.google.maps);
    const script = document.createElement("script");
    script.src = mapsScriptUrl();
    script.async = true;
    script.onerror = () => reject(new Error("Google Maps failed to load"));
    document.head.appendChild(script);
  });
  return loaderPromise;
}

export default function MapView({ markers = [], path = [] }) {
  const el = useRef(null);
  const [failed, setFailed] = useState(!MAPS_API_KEY);

  useEffect(() => {
    if (!MAPS_API_KEY) return;
    let cancelled = false;
    loadGoogleMaps()
      .then((maps) => {
        if (cancelled || !el.current) return;
        const map = new maps.Map(el.current, {
          center: markers[markers.length - 1] || DEFAULT_CENTER,
          zoom: markers.length ? TRACKING_ZOOM : DEFAULT_ZOOM,
          styles: MAP_STYLES,
          disableDefaultUI: true,
          zoomControl: true,
        });
        const bounds = new maps.LatLngBounds();
        markers.forEach((m) => {
          new maps.Marker({ position: { lat: m.lat, lng: m.lng }, map, title: m.label || m.city });
          bounds.extend({ lat: m.lat, lng: m.lng });
        });
        if (path.length > 1) {
          new maps.Polyline({ path, map, strokeColor: "#0b4f71", strokeWeight: 4, strokeOpacity: 0.8 });
        }
        if (markers.length > 1) map.fitBounds(bounds, 48);
      })
      .catch(() => setFailed(true));
    return () => {
      cancelled = true;
    };
  }, [markers, path]);

  if (failed) {
    return <div className="map-placeholder muted">Map unavailable (no Maps key configured for this environment).</div>;
  }
  return <div ref={el} className="map" role="img" aria-label="Shipment route map" />;
}
