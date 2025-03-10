import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge.jsx";

export default function ShipmentTable({ shipments }) {
  if (!shipments.length) {
    return <p className="muted">No shipments match this filter.</p>;
  }
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Reference</th>
          <th>Lane</th>
          <th>Pickup</th>
          <th>Carrier</th>
          <th>Status</th>
          <th className="num">Quoted</th>
        </tr>
      </thead>
      <tbody>
        {shipments.map((s) => (
          <tr key={s.id}>
            <td>
              <Link to={`/track/${s.reference}`}>{s.reference}</Link>
            </td>
            <td>
              {s.origin_city} → {s.destination_city}
            </td>
            <td>{s.pickup_date}</td>
            <td>{s.carrier_name || <span className="muted">Pending tender</span>}</td>
            <td>
              <StatusBadge status={s.status} />
            </td>
            <td className="num">${(s.quoted_price_cents / 100).toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
