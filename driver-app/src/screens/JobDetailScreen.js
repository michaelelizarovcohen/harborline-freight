import { useState } from "react";
import { Alert, Linking, Platform, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import MapView, { Marker } from "react-native-maps";
import { api } from "../api/client";
import { startTracking, stopTracking } from "../services/location";

function openNavigation(stop) {
  const q = encodeURIComponent(`${stop.address_line1}, ${stop.city}, ${stop.state} ${stop.postal_code}`);
  const url = Platform.OS === "ios" ? `maps://?daddr=${q}` : `google.navigation:q=${q}`;
  Linking.openURL(url).catch(() => Linking.openURL(`https://www.google.com/maps/dir/?api=1&destination=${q}`));
}

export default function JobDetailScreen({ route, navigation }) {
  const [job, setJob] = useState(route.params.job);
  const [busy, setBusy] = useState(false);
  const stop = job.status === "assigned" ? job.pickup : job.dropoff;

  async function transition(action) {
    setBusy(true);
    try {
      const updated = await api.post(`/v1/drivers/jobs/${job.id}/${action}`, {});
      setJob(updated);
      if (action === "start") await startTracking(job.id);
      if (action === "arrive_dropoff") navigation.navigate("Delivery", { job: updated });
    } catch (e) {
      Alert.alert("Couldn't update job", e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScrollView style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{ latitude: stop.lat, longitude: stop.lng, latitudeDelta: 0.05, longitudeDelta: 0.05 }}
      >
        <Marker coordinate={{ latitude: job.pickup.lat, longitude: job.pickup.lng }} title="Pickup" />
        <Marker coordinate={{ latitude: job.dropoff.lat, longitude: job.dropoff.lng }} title="Drop-off" pinColor="#0b4f71" />
      </MapView>
      <View style={styles.section}>
        <Text style={styles.ref}>{job.shipment_reference}</Text>
        <Text style={styles.label}>{job.status === "assigned" ? "Pickup" : "Drop-off"}</Text>
        <Text style={styles.address}>
          {stop.name}
          {"\n"}
          {stop.address_line1}, {stop.city}, {stop.state} {stop.postal_code}
        </Text>
        {stop.appointment && <Text style={styles.label}>Appointment: {stop.appointment}</Text>}
        {job.special_instructions ? <Text style={styles.notes}>{job.special_instructions}</Text> : null}
      </View>
      <Pressable style={styles.secondary} onPress={() => openNavigation(stop)}>
        <Text style={styles.secondaryText}>Navigate</Text>
      </Pressable>
      {job.status === "assigned" && (
        <Pressable style={styles.primary} disabled={busy} onPress={() => transition("start")}>
          <Text style={styles.primaryText}>Start job (loaded)</Text>
        </Pressable>
      )}
      {job.status === "in_transit" && (
        <Pressable style={styles.primary} disabled={busy} onPress={() => transition("arrive_dropoff")}>
          <Text style={styles.primaryText}>Arrived at drop-off</Text>
        </Pressable>
      )}
      {job.status === "delivered" && (
        <Pressable style={styles.secondary} onPress={stopTracking}>
          <Text style={styles.secondaryText}>Delivered ✓</Text>
        </Pressable>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f9" },
  map: { height: 240 },
  section: { padding: 16, backgroundColor: "#fff" },
  ref: { fontSize: 18, fontWeight: "700" },
  label: { color: "#6b7a86", marginTop: 8 },
  address: { fontSize: 16, marginTop: 4 },
  notes: { marginTop: 10, backgroundColor: "#fff3d6", padding: 10, borderRadius: 8 },
  primary: { margin: 16, marginTop: 8, backgroundColor: "#0b4f71", padding: 16, borderRadius: 10, alignItems: "center" },
  primaryText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  secondary: { margin: 16, marginBottom: 0, borderColor: "#0b4f71", borderWidth: 1, padding: 14, borderRadius: 10, alignItems: "center" },
  secondaryText: { color: "#0b4f71", fontWeight: "600" },
});
