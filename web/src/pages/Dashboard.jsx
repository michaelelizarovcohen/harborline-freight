import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import useShipments from "../hooks/useShipments.js";
import ShipmentTable from "../components/ShipmentTable.jsx";

const FILTERS = [
  { value: "", label: "All" },
  { value: "booked", label: "Booked" },
  { value: "in_transit", label: "In transit" },
  { value: "delivered", label: "Delivered" },
  { value: "exception", label: "Exceptions" },
];

export default function Dashboard() {
  const [status, setStatus] = useState("");
  const { shipments, loading, error, reload } = useShipments({ status });

  const stats = useMemo(() => {
    const byStatus = shipments.reduce((acc, s) => {
      acc[s.status] = (acc[s.status] || 0) + 1;
      return acc;
    }, {});
    const spend = shipments.reduce((sum, s) => sum + (s.quoted_price_cents || 0), 0);
    return { byStatus, spend };
  }, [shipments]);

  return (
    <section>
      <div className="page-header">
        <h1>Shipments</h1>
        <Link className="button primary" to="/book">
          + New booking
        </Link>
      </div>

      <div className="stat-row">
        <div className="stat">
          <span className="stat-label">In transit</span>
          <span className="stat-value">{stats.byStatus.in_transit || 0}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Exceptions</span>
          <span className="stat-value warn">{stats.byStatus.exception || 0}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Booked spend (shown)</span>
          <span className="stat-value">
            {(stats.spend / 100).toLocaleString("en-US", { style: "currency", currency: "USD" })}
          </span>
        </div>
      </div>

      <div className="filters">
        {FILTERS.map((f) => (
          <button
            key={f.value || "all"}
            className={status === f.value ? "chip active" : "chip"}
            onClick={() => setStatus(f.value)}
          >
            {f.label}
          </button>
        ))}
        <button className="link" onClick={reload}>
          Refresh
        </button>
      </div>

      {error && <p className="error">Could not load shipments: {error.message}</p>}
      {loading ? <p className="muted">Loading…</p> : <ShipmentTable shipments={shipments} />}
    </section>
  );
}
