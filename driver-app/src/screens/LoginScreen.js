import { useState } from "react";
import { ActivityIndicator, KeyboardAvoidingView, Platform, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { signIn } from "../api/client";

export default function LoginScreen({ onSignedIn }) {
  const [phone, setPhone] = useState("");
  const [pin, setPin] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const session = await signIn(phone.replace(/\D/g, ""), pin);
      onSignedIn(session);
    } catch (e) {
      setError(e.status === 401 ? "Phone number or PIN is incorrect." : "Can't reach Harborline right now.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <Text style={styles.title}>Harborline Driver</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Mobile number</Text>
        <TextInput style={styles.input} keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
        <Text style={styles.label}>Driver PIN</Text>
        <TextInput style={styles.input} keyboardType="number-pad" secureTextEntry maxLength={6} value={pin} onChangeText={setPin} />
        {error && <Text style={styles.error}>{error}</Text>}
        <Pressable style={styles.button} onPress={submit} disabled={busy}>
          {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Sign in</Text>}
        </Pressable>
      </View>
      <Text style={styles.help}>Forgot your PIN? Call dispatch: (555) 010-4410</Text>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0b2f45", justifyContent: "center", padding: 24 },
  title: { color: "#fff", fontSize: 28, fontWeight: "700", textAlign: "center", marginBottom: 24 },
  card: { backgroundColor: "#fff", borderRadius: 12, padding: 20 },
  label: { color: "#6b7a86", marginTop: 8 },
  input: { borderWidth: 1, borderColor: "#c9d4dc", borderRadius: 8, padding: 12, fontSize: 18, marginTop: 4 },
  error: { color: "#b3261e", marginTop: 12 },
  button: { backgroundColor: "#0b4f71", borderRadius: 8, padding: 14, alignItems: "center", marginTop: 20 },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  help: { color: "#cfe3ef", textAlign: "center", marginTop: 16 },
});
