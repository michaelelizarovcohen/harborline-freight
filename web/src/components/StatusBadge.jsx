const LABELS = {
  quoted: "Quoted",
  booked: "Booked",
  tendered: "Tendered",
  in_transit: "In transit",
  delivered: "Delivered",
  exception: "Exception",
  cancelled: "Cancelled",
  open: "Open",
  paid: "Paid",
  void: "Void",
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{LABELS[status] || status}</span>;
}
