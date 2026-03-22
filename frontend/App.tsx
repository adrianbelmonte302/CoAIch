import { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Platform, SafeAreaView, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

const WEB_FALLBACK_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";
const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE ||
  (Platform.OS === "web" ? WEB_FALLBACK_BASE : "http://localhost:8000");
const API_USER = process.env.EXPO_PUBLIC_API_USER || "";
const API_PASS = process.env.EXPO_PUBLIC_API_PASS || "";
const BASIC_AUTH =
  API_USER && API_PASS ? `Basic ${btoa(`${API_USER}:${API_PASS}`)}` : "";

type SessionSummary = {
  id: string;
  date?: string;
  title?: string;
  session_tags?: string[];
  estimated_duration_min?: number;
  is_rest_day?: boolean;
  deload_week?: boolean;
  data_status?: string;
};

type SessionDetail = SessionSummary & {
  warmup?: {
    quote?: string;
    mobility?: string;
    activation?: string;
    raw_text?: string;
  };
  blocks?: Array<{
    id: string;
    title?: string;
    content_mode?: string;
    raw_text?: string;
    coach_notes?: string;
    has_external_reference?: boolean;
    exercises_raw?: Array<{
      id: string;
      name?: string;
      format?: string;
      notes?: string;
    }>;
    items_canonical?: Array<{
      id: string;
      movement_name?: string;
      raw_origin_text?: string;
      execution_notes?: string;
    }>;
  }>;
};

const Stack = createNativeStackNavigator();

function Badge({ label }: { label: string }) {
  return (
    <View
      style={{
        backgroundColor: "#111",
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 4,
        marginRight: 4,
      }}
    >
      <Text style={{ color: "white", fontSize: 12 }}>{label}</Text>
    </View>
  );
}

function SessionListScreen({ navigation }: any) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/sessions/`, {
      headers: BASIC_AUTH ? { Authorization: BASIC_AUTH } : undefined,
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => setSessions(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12 }}>Cargando sesiones...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6" }}>
      <FlatList
        data={sessions}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={{
              backgroundColor: "white",
              padding: 16,
              borderRadius: 12,
              marginBottom: 12,
              shadowColor: "#000",
              shadowOpacity: 0.05,
              shadowRadius: 8,
              elevation: 3,
            }}
            onPress={() => navigation.push("Detail", { sessionId: item.id })}
          >
            <Text style={{ fontSize: 18, fontWeight: "600" }}>{item.title || "Sin nombre"}</Text>
            <Text style={{ color: "#666", marginTop: 4 }}>
              {item.date || "Fecha sin definir"}
            </Text>
            <View style={{ flexDirection: "row", marginTop: 8 }}>
              {item.is_rest_day && <Badge label="Rest" />}
              {item.deload_week && <Badge label="Deload" />}
              {item.data_status === "external_reference" && <Badge label="External" />}
              {item.session_tags?.map((tag) => (
                <Badge key={tag} label={tag} />
              ))}
            </View>
            <Text style={{ marginTop: 8, color: "#333" }}>
              Duración estimada: {item.estimated_duration_min ?? "—"} min
            </Text>
          </TouchableOpacity>
        )}
      />
    </SafeAreaView>
  );
}

function SessionDetailScreen({ route }: any) {
  const { sessionId } = route.params;
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/sessions/${sessionId}`, {
      headers: BASIC_AUTH ? { Authorization: BASIC_AUTH } : undefined,
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => setSession(data))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading || !session) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12 }}>Cargando detalles...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f5f5f5" }} contentContainerStyle={{ padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: "700" }}>{session.title}</Text>
      <Text style={{ color: "#666", marginTop: 4 }}>{session.date}</Text>
      <View style={{ flexDirection: "row", marginTop: 8 }}>
        {(session.session_tags || []).map((tag) => (
          <Badge key={tag} label={tag} />
        ))}
        {session.is_rest_day && <Badge label="Descanso" />}
        {session.deload_week && <Badge label="Deload" />}
        {session.data_status === "external_reference" && <Badge label="Referencia externa" />}
      </View>
      <Text style={{ marginTop: 8, fontWeight: "600" }}>
        Duración estimada: {session.estimated_duration_min ?? "—"} min
      </Text>

      {session.warmup && (
        <View style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "600" }}>Warm-up</Text>
          <Text style={{ marginTop: 4 }}>{session.warmup.raw_text || session.warmup.mobility}</Text>
          {session.warmup.activation && <Text style={{ marginTop: 2 }}>{session.warmup.activation}</Text>}
        </View>
      )}

      {(session.blocks || []).map((block) => (
        <View
          key={block.id}
          style={{
            marginTop: 16,
            padding: 16,
            backgroundColor: "white",
            borderRadius: 12,
            shadowColor: "#000",
            shadowOpacity: 0.05,
            shadowRadius: 6,
            elevation: 2,
          }}
        >
          <Text style={{ fontSize: 16, fontWeight: "600" }}>{block.title || "Bloque"}</Text>
          <Text style={{ color: "#888", marginTop: 2 }}>{block.content_mode}</Text>
          {block.raw_text && (
            <Text style={{ marginTop: 8, color: "#222" }}>{block.raw_text}</Text>
          )}
          {block.coach_notes && (
            <Text style={{ marginTop: 4, fontStyle: "italic", color: "#444" }}>
              Coach notes: {block.coach_notes}
            </Text>
          )}
          {(block.exercises_raw || []).map((exercise) => (
            <View key={exercise.id} style={{ marginTop: 8 }}>
              <Text style={{ fontWeight: "600" }}>{exercise.name}</Text>
              <Text style={{ color: "#444" }}>{exercise.format}</Text>
              {exercise.notes && <Text>{exercise.notes}</Text>}
            </View>
          ))}
          {(block.items_canonical || []).map((item) => (
            <View key={item.id} style={{ marginTop: 8, borderTopWidth: 1, borderTopColor: "#eee", paddingTop: 8 }}>
              <Text style={{ fontSize: 14, fontWeight: "600" }}>{item.movement_name || "Item canónico"}</Text>
              {item.execution_notes && <Text style={{ color: "#555" }}>{item.execution_notes}</Text>}
              {item.raw_origin_text && (
                <Text style={{ fontSize: 12, color: "#999", marginTop: 2 }}>{item.raw_origin_text}</Text>
              )}
            </View>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: "#100" }, headerTintColor: "#fff" }}>
        <Stack.Screen name="Sessions" component={SessionListScreen} />
        <Stack.Screen name="Detail" component={SessionDetailScreen} options={{ title: "Detalle de sesión" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
