import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { format } from "date-fns";
import { api } from "../api/client.js";
import MapView from "../components/MapView.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function Tracking() {
  const { reference } = useParams();
  const [query, setQuery] = useState(reference || "");
  const [tracking, setTracking] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!reference) return;
    let cancelled = false;
    api
      .get(`/v1/tracking/${encodeURIComponent(reference)}`)
      .then((data) => !cancelled && setTracking(data))
      .catch((err) => !cancelled && setError(err.status === 404 ? "No shipment with that reference." : err.message));
    return () => {
      cancelled = true;
    };
  }, [reference]);

  function submit(e) {
    e.preventDefault();
    setError(null);
    setTracking(null);
    navigate(`/track/${query.trim().toUpperCase()}`);
  }

  return (
    <section>
      <h1>Track a shipment</h1>
      <form className="inline-form" onSubmit={submit}>
        <input placeholder="HBL-2025-000123" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="button">Track</button>
      </form>

      {error && <p className="error">{error}</p>}

      {tracking && (
        <div className="tracking-layout">
          <div className="card">
            <h2>
              {tracking.reference} <StatusBadge status={tracking.status} />
            </h2>
            <p className="muted">
              {tracking.origin.city}, {tracking.origin.state} → {tracking.destination.city}, {tracking.destination.state}
            </p>
            {tracking.eta && <p>ETA: {format(new Date(tracking.eta), "EEE MMM d, h:mm a")}</p>}
            <ol className="timeline">
              {tracking.events.map((ev) => (
                <li key={ev.id}>
                  <strong>{ev.description}</strong>
                  <span className="muted"> · {format(new Date(ev.occurred_at), "MMM d h:mm a")}</span>
                  {ev.location && <div className="muted">{ev.location}</div>}
                </li>
              ))}
            </ol>
          </div>
          <MapView
            markers={[tracking.origin, tracking.destination, tracking.last_position].filter(Boolean)}
            path={tracking.breadcrumbs}
          />
        </div>
      )}
    </section>
  );
}
