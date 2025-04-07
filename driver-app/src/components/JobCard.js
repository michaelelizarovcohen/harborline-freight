import { Pressable, StyleSheet, Text, View } from "react-native";

const STATUS_COLORS = {
  assigned: "#7a5300",
  in_transit: "#0b4f71",
  delivered: "#1e6b33",
  exception: "#b3261e",
};

export default function JobCard({ job, onPress }) {
  const stop = job.status === "assigned" ? job.pickup : job.dropoff;
  return (
    <Pressable style={styles.card} onPress={onPress}>
      <View style={styles.row}>
        <Text style={styles.ref}>{job.shipment_reference}</Text>
        <Text style={[styles.status, { color: STATUS_COLORS[job.status] || "#333" }]}>{job.status.replace("_", " ")}</Text>
      </View>
      <Text style={styles.stop}>
        {job.status === "assigned" ? "Pickup" : "Drop-off"}: {stop.name}
      </Text>
      <Text style={styles.meta}>
        {stop.city}, {stop.state} · {job.equipment} · {job.weight_lbs.toLocaleString()} lbs
      </Text>
      {stop.appointment && <Text style={styles.meta}>Appt {stop.appointment}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: "#fff", borderRadius: 10, padding: 14, marginBottom: 10 },
  row: { flexDirection: "row", justifyContent: "space-between" },
  ref: { fontWeight: "700", fontSize: 16 },
  status: { textTransform: "capitalize", fontWeight: "600" },
  stop: { marginTop: 6, fontSize: 15 },
  meta: { color: "#6b7a86", marginTop: 2 },
});
