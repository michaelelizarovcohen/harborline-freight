import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client.js";

// Loads the shipper's shipments with simple status filtering + polling.
export default function useShipments({ status, pollMs = 60000 } = {}) {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(
    async (signal) => {
      try {
        const data = await api.get("/v1/shipments", { query: { status, per_page: 50 }, signal });
        setShipments(data.items || []);
        setError(null);
      } catch (err) {
        if (err.name !== "AbortError") setError(err);
      } finally {
        setLoading(false);
      }
    },
    [status]
  );

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    load(controller.signal);
    const timer = pollMs ? setInterval(() => load(controller.signal), pollMs) : null;
    return () => {
      controller.abort();
      if (timer) clearInterval(timer);
    };
  }, [load, pollMs]);

  return { shipments, loading, error, reload: () => load() };
}
