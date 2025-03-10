import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import StatusBadge from "../components/StatusBadge.jsx";

const money = (cents, currency = "USD") =>
  (cents / 100).toLocaleString("en-US", { style: "currency", currency });

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [paying, setPaying] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/v1/invoices").then((d) => setInvoices(d.items || [])).catch((e) => setError(e.message));
  }, []);

  async function pay(invoice) {
    setPaying(invoice.id);
    try {
      // API creates a Stripe Checkout session server-side; we only redirect.
      const { checkout_url } = await api.post(`/v1/invoices/${invoice.id}/checkout`, {});
      window.location.assign(checkout_url);
    } catch (e) {
      setError(e.message);
      setPaying(null);
    }
  }

  return (
    <section>
      <h1>Invoices</h1>
      {error && <p className="error">{error}</p>}
      <table className="table">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Shipment</th>
            <th>Issued</th>
            <th>Due</th>
            <th>Amount</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.number}</td>
              <td>{inv.shipment_reference}</td>
              <td>{inv.issued_on}</td>
              <td>{inv.due_on}</td>
              <td>{money(inv.amount_cents, inv.currency)}</td>
              <td>
                <StatusBadge status={inv.status} />
              </td>
              <td>
                {inv.status === "open" && (
                  <button className="button small" disabled={paying === inv.id} onClick={() => pay(inv)}>
                    {paying === inv.id ? "Redirecting…" : "Pay now"}
                  </button>
                )}
              </td>
            </tr>
          ))}
          {invoices.length === 0 && (
            <tr>
              <td colSpan={7} className="muted">
                No invoices yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
