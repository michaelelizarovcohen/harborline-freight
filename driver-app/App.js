import { useEffect, useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import LoginScreen from "./src/screens/LoginScreen";
import JobsScreen from "./src/screens/JobsScreen";
import JobDetailScreen from "./src/screens/JobDetailScreen";
import DeliveryScreen from "./src/screens/DeliveryScreen";
import { loadSession, clearSession } from "./src/api/client";
import { installCrashReporter } from "./src/services/crashReporter";

const Stack = createNativeStackNavigator();

installCrashReporter();

export default function App() {
  const [session, setSession] = useState(undefined);

  useEffect(() => {
    loadSession().then(setSession);
  }, []);

  if (session === undefined) return null; // splash stays up while SecureStore loads

  async function signOut() {
    await clearSession();
    setSession(null);
  }

  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: "#0b2f45" },
          headerTintColor: "#fff",
        }}
      >
        {!session ? (
          <Stack.Screen name="Login" options={{ headerShown: false }}>
            {(props) => <LoginScreen {...props} onSignedIn={setSession} />}
          </Stack.Screen>
        ) : (
          <>
            <Stack.Screen name="Jobs" options={{ title: "Today's jobs" }}>
              {(props) => <JobsScreen {...props} driver={session.driver} onSignOut={signOut} />}
            </Stack.Screen>
            <Stack.Screen name="JobDetail" component={JobDetailScreen} options={{ title: "Job" }} />
            <Stack.Screen name="Delivery" component={DeliveryScreen} options={{ title: "Proof of delivery" }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
