import { useCallback, useEffect, useState } from "react";
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { api } from "../api/client";
import JobCard from "../components/JobCard";

export default function JobsScreen({ navigation, driver, onSignOut }) {
  const [jobs, setJobs] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const data = await api.get("/v1/drivers/me/jobs?window=today");
      setJobs(data.items || []);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
    navigation.setOptions({
      headerRight: () => (
        <Pressable onPress={onSignOut}>
          <Text style={{ color: "#fff" }}>Sign out</Text>
        </Pressable>
      ),
    });
  }, [load, navigation, onSignOut]);

  return (
    <View style={styles.container}>
      <Text style={styles.greeting}>Hi {driver?.first_name || "driver"} — {jobs.length} stop(s) today</Text>
      {error && <Text style={styles.error}>{error}</Text>}
      <FlatList
        data={jobs}
        keyExtractor={(j) => String(j.id)}
        renderItem={({ item }) => <JobCard job={item} onPress={() => navigation.navigate("JobDetail", { job: item })} />}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
        ListEmptyComponent={!refreshing && <Text style={styles.empty}>No jobs assigned yet. Pull to refresh.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f9", padding: 12 },
  greeting: { fontSize: 16, fontWeight: "600", marginBottom: 8 },
  error: { color: "#b3261e", marginBottom: 8 },
  empty: { textAlign: "center", color: "#6b7a86", marginTop: 40 },
});
