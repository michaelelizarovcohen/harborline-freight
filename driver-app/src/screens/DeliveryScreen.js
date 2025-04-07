import { useRef, useState } from "react";
import { Alert, Image, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImageManipulator from "expo-image-manipulator";
import SignatureScreen from "react-native-signature-canvas";
import { api } from "../api/client";
import { stopTracking } from "../services/location";

// Proof of delivery: photo of the freight/BOL + consignee signature + printed name.
export default function DeliveryScreen({ route, navigation }) {
  const { job } = route.params;
  const camera = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [photo, setPhoto] = useState(null);
  const [signature, setSignature] = useState(null);
  const [receivedBy, setReceivedBy] = useState("");
  const [busy, setBusy] = useState(false);

  async function takePhoto() {
    const shot = await camera.current?.takePictureAsync({ quality: 0.7, skipProcessing: true });
    if (!shot) return;
    // Shrink before upload; full-res photos were timing out on rural LTE.
    const small = await ImageManipulator.manipulateAsync(shot.uri, [{ resize: { width: 1280 } }], {
      compress: 0.6,
      format: ImageManipulator.SaveFormat.JPEG,
    });
    setPhoto(small);
  }

  async function submit() {
    if (!photo || !signature || !receivedBy.trim()) {
      Alert.alert("Missing info", "Photo, signature and the receiver's name are all required.");
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("photo", { uri: photo.uri, name: `pod-${job.id}.jpg`, type: "image/jpeg" });
      form.append("signature_png", signature); // data URL from the canvas
      form.append("received_by", receivedBy.trim());
      form.append("delivered_at", new Date().toISOString());
      await api.post(`/v1/drivers/jobs/${job.id}/proof-of-delivery`, form);
      await stopTracking();
      navigation.popToTop();
    } catch (e) {
      Alert.alert("Upload failed", "We saved nothing yet - check signal and try again.\n" + e.message);
    } finally {
      setBusy(false);
    }
  }

  if (!permission) return null;
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text>Camera access is needed for proof of delivery.</Text>
        <Pressable style={styles.primary} onPress={requestPermission}>
          <Text style={styles.primaryText}>Allow camera</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {photo ? (
        <Pressable onPress={() => setPhoto(null)}>
          <Image source={{ uri: photo.uri }} style={styles.preview} />
          <Text style={styles.hint}>Tap photo to retake</Text>
        </Pressable>
      ) : (
        <CameraView ref={camera} style={styles.preview}>
          <Pressable style={styles.shutter} onPress={takePhoto} />
        </CameraView>
      )}
      <TextInput style={styles.input} placeholder="Received by (printed name)" value={receivedBy} onChangeText={setReceivedBy} />
      <View style={styles.signature}>
        <SignatureScreen onOK={setSignature} onClear={() => setSignature(null)} descriptionText="Consignee signature" />
      </View>
      <Pressable style={styles.primary} disabled={busy} onPress={submit}>
        <Text style={styles.primaryText}>{busy ? "Uploading…" : "Complete delivery"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f9" },
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: 24 },
  preview: { height: 220, width: "100%", backgroundColor: "#000", justifyContent: "flex-end", alignItems: "center" },
  shutter: { width: 64, height: 64, borderRadius: 32, backgroundColor: "#fff", marginBottom: 12 },
  hint: { textAlign: "center", color: "#6b7a86", marginTop: 4 },
  input: { backgroundColor: "#fff", margin: 12, marginBottom: 0, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: "#c9d4dc" },
  signature: { height: 200, margin: 12, borderRadius: 8, overflow: "hidden" },
  primary: { margin: 12, backgroundColor: "#0b4f71", padding: 16, borderRadius: 10, alignItems: "center" },
  primaryText: { color: "#fff", fontWeight: "700", fontSize: 16 },
});
