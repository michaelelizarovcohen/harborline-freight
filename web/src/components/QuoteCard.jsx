export default function QuoteCard({ quote, selected, onSelect }) {
  const total = (quote.total_cents / 100).toLocaleString("en-US", { style: "currency", currency: "USD" });
  return (
    <button type="button" className={selected ? "quote-card selected" : "quote-card"} onClick={onSelect}>
      <div className="quote-main">
        <span className="quote-carrier">{quote.carrier_name}</span>
        <span className="quote-total">{total}</span>
      </div>
      <div className="quote-meta">
        <span>{quote.transit_days} day transit</span>
        <span>Linehaul ${(quote.linehaul_cents / 100).toFixed(2)}</span>
        <span>Fuel ${(quote.fuel_surcharge_cents / 100).toFixed(2)}</span>
        {quote.accessorials_cents > 0 && <span>Accessorials ${(quote.accessorials_cents / 100).toFixed(2)}</span>}
      </div>
      <div className="quote-expiry muted">Rate valid until {new Date(quote.expires_at).toLocaleString()}</div>
    </button>
  );
}
