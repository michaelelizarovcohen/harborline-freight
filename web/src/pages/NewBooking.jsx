import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import QuoteCard from "../components/QuoteCard.jsx";

const EQUIPMENT = [
  { value: "dry_van_53", label: "53' dry van" },
  { value: "reefer_53", label: "53' reefer" },
  { value: "flatbed_48", label: "48' flatbed" },
  { value: "container_40", label: "40' container (drayage)" },
];

const EMPTY = {
  origin_postal: "",
  destination_postal: "",
  pickup_date: "",
  equipment: "dry_van_53",
  weight_lbs: "",
  pallets: "",
  hazmat: false,
  reference: "",
};

export default function NewBooking() {
  const [form, setForm] = useState(EMPTY);
  const [quotes, setQuotes] = useState([]);
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  function update(field) {
    return (e) => {
      const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
      setForm((f) => ({ ...f, [field]: value }));
    };
  }

  async function requestQuotes(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setSelected(null);
    try {
      const data = await api.post("/v1/quotes", {
        ...form,
        weight_lbs: Number(form.weight_lbs),
        pallets: form.pallets ? Number(form.pallets) : null,
      });
      setQuotes(data.quotes || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function book() {
    if (!selected) return;
    setBusy(true);
    try {
      const booking = await api.post("/v1/bookings", {
        quote_id: selected.id,
        shipper_reference: form.reference || undefined,
      });
      navigate(`/track/${booking.shipment_reference}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <section className="booking">
      <h1>New booking</h1>
      <form className="card form-grid" onSubmit={requestQuotes}>
        <label>
          Origin ZIP
          <input required pattern="\d{5}" value={form.origin_postal} onChange={update("origin_postal")} />
        </label>
        <label>
          Destination ZIP
          <input required pattern="\d{5}" value={form.destination_postal} onChange={update("destination_postal")} />
        </label>
        <label>
          Pickup date
          <input required type="date" value={form.pickup_date} onChange={update("pickup_date")} />
        </label>
        <label>
          Equipment
          <select value={form.equipment} onChange={update("equipment")}>
            {EQUIPMENT.map((eq) => (
              <option key={eq.value} value={eq.value}>
                {eq.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Weight (lbs)
          <input required type="number" min="1" max="48000" value={form.weight_lbs} onChange={update("weight_lbs")} />
        </label>
        <label>
          Pallets
          <input type="number" min="0" max="30" value={form.pallets} onChange={update("pallets")} />
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={form.hazmat} onChange={update("hazmat")} /> Hazmat
        </label>
        <label>
          Your reference (PO #)
          <input value={form.reference} onChange={update("reference")} maxLength={40} />
        </label>
        <button className="button primary" disabled={busy}>
          {busy ? "Pricing…" : "Get quotes"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {quotes.length > 0 && (
        <div className="quotes">
          <h2>Available rates</h2>
          {quotes.map((q) => (
            <QuoteCard key={q.id} quote={q} selected={selected?.id === q.id} onSelect={() => setSelected(q)} />
          ))}
          <button className="button primary" disabled={!selected || busy} onClick={book}>
            Book selected rate
          </button>
        </div>
      )}
    </section>
  );
}
