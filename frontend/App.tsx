import React, { createContext, useContext, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Image,
  Platform,
  SafeAreaView,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

const WEB_FALLBACK_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";
const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE ||
  (Platform.OS === "web" ? WEB_FALLBACK_BASE : "http://localhost:8000");
const API_USER = process.env.EXPO_PUBLIC_API_USER || "";
const API_PASS = process.env.EXPO_PUBLIC_API_PASS || "";

function encodeBase64(value: string): string {
  if (typeof globalThis.btoa === "function") {
    return globalThis.btoa(value);
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const anyGlobal: any = globalThis as any;
  if (anyGlobal.Buffer) {
    return anyGlobal.Buffer.from(value, "utf8").toString("base64");
  }
  return value;
}

function buildBasicAuth(username: string, password: string): string {
  if (!username || !password) return "";
  return `Basic ${encodeBase64(`${username}:${password}`)}`;
}

type SessionSummary = {
  id: string;
  date?: string;
  title?: string;
  session_tags?: string[];
  estimated_duration_min?: number;
  is_rest_day?: boolean;
  deload_week?: boolean;
  data_status?: string;
  weekday?: string;
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
const Tab = createBottomTabNavigator();
const AuthContext = createContext({
  basicAuth: "",
  username: "",
  logout: () => {},
});

const AUTO_LOGOUT_MIN = 60;

const LOGO_DATA_URI =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="220" height="64" viewBox="0 0 220 64">' +
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0" stop-color="#2563eb"/>' +
      '<stop offset="1" stop-color="#0ea5e9"/>' +
      '</linearGradient></defs>' +
      '<rect x="4" y="6" rx="12" ry="12" width="52" height="52" fill="url(#g)"/>' +
      '<path d="M20 40l6-14h12l-6 14h-12z" fill="#fff" opacity="0.95"/>' +
      '<path d="M30 22l6 14h12l-6-14H30z" fill="#fff" opacity="0.85"/>' +
      '<text x="70" y="40" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="700" fill="#0f172a">CoAIch</text>' +
      '<text x="70" y="56" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#64748b">Training Viewer</text>' +
    '</svg>'
  );


function Badge({ label }: { label: string }) {
  return (
    <View
      style={{
        backgroundColor: "#2563eb",
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 4,
        marginRight: 4,
      }}
    >
      <Text style={{ color: "white", fontSize: 12, textAlign: "center" }}>{label}</Text>
    </View>
  );
}

function DatePicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (next: string) => void;
}) {
  if (Platform.OS === "web") {
    return React.createElement("input", {
      type: "date",
      value,
      onChange: (event: any) => onChange(event.target.value),
      style: {
        flex: 1,
        borderWidth: 1,
        borderColor: "#e2e8f0",
        borderRadius: 8,
        padding: "8px 10px",
        backgroundColor: "white",
        fontSize: "14px",
      },
    });
  }
  return (
    <TextInput
      value={value}
      onChangeText={onChange}
      placeholder="2025-12-31"
      style={{
        flex: 1,
        borderWidth: 1,
        borderColor: "#e2e8f0",
        borderRadius: 8,
        paddingHorizontal: 10,
        paddingVertical: 8,
        backgroundColor: "white",
        textAlign: "center",
      }}
    />
  );
}

function getMonthKey(date?: string): string {
  if (!date || date.length < 7) return "Fecha desconocida";
  const [y, m] = date.split("-");
  return `${y}-${m}`;
}

function formatMonthLabel(monthKey: string): string {
  if (monthKey === "Fecha desconocida") return monthKey;
  const [y, m] = monthKey.split("-");
  const month = Number(m);
  const monthNames = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
  ];
  return `${monthNames[month - 1] || "Mes"} ${y}`;
}

function formatDayLabel(session: SessionSummary): string {
  if (!session.date) return "Fecha sin definir";
  const parts: string[] = [];
  if (session.weekday) parts.push(session.weekday);
  parts.push(session.date);
  return parts.join(" ");
}

type ListRow =
  | { type: "month"; key: string; label: string }
  | { type: "day"; key: string; label: string }
  | { type: "session"; key: string; session: SessionSummary };

function SessionListScreen({ navigation, route }: any) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [jumpDate, setJumpDate] = useState("");
  const [filteredDate, setFilteredDate] = useState("");
  const { basicAuth, username, logout } = useContext(AuthContext);

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity onPress={logout} style={{ paddingHorizontal: 12 }}>
          <Text style={{ color: "#fff", fontWeight: "600" }}>Salir</Text>
        </TouchableOpacity>
      ),
      headerLeft: () => (
        <Text style={{ color: "#fff", marginLeft: 12, fontSize: 12 }}>
          {username ? `Usuario: ${username}` : ""}
        </Text>
      ),
    });
  }, [navigation, logout]);

  useEffect(() => {
    if (!basicAuth) {
      return;
    }
    setLoading(true);
    fetch(`${API_BASE}/sessions/`, {
      headers: { Authorization: basicAuth },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => setSessions(data))
      .finally(() => setLoading(false));
  }, [basicAuth]);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12, textAlign: "center" }}>Cargando sesiones...</Text>
      </View>
    );
  }

  const effectiveSessions = filteredDate
    ? sessions.filter((s) => s.date === filteredDate)
    : sessions;

  const rows: ListRow[] = [];
  const seenDays = new Set<string>();
  let currentMonth = "";
  effectiveSessions.forEach((session) => {
    const monthKey = getMonthKey(session.date);
    if (monthKey !== currentMonth) {
      currentMonth = monthKey;
      rows.push({
        type: "month",
        key: `month-${monthKey}`,
        label: formatMonthLabel(monthKey),
      });
    }
    const dayKey = session.date || `unknown-${session.id}`;
    if (!seenDays.has(dayKey)) {
      seenDays.add(dayKey);
      rows.push({
        type: "day",
        key: `day-${dayKey}`,
        label: formatDayLabel(session),
      });
    }
    rows.push({ type: "session", key: session.id, session });
  });

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6" }}>
      <View style={{ paddingHorizontal: 16, paddingTop: 12, alignItems: "center" }}>
        <Text style={{ fontSize: 14, color: "#333", marginBottom: 6, textAlign: "center" }}>
          Saltar a fecha (YYYY-MM-DD)
        </Text>
        <View style={{ flexDirection: "row", marginBottom: 12 }}>
          <DatePicker value={jumpDate} onChange={setJumpDate} />
          <TouchableOpacity
            onPress={() => setFilteredDate(jumpDate.trim())}
            style={{
              marginLeft: 8,
              backgroundColor: "#2563eb",
              paddingHorizontal: 12,
              borderRadius: 8,
              justifyContent: "center",
            }}
          >
            <Text style={{ color: "white", fontWeight: "600" }}>Ir</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setFilteredDate("");
              setJumpDate("");
            }}
            style={{
              marginLeft: 8,
              backgroundColor: "#eee",
              paddingHorizontal: 12,
              borderRadius: 8,
              justifyContent: "center",
            }}
          >
            <Text style={{ color: "#333", fontWeight: "600" }}>Ver todo</Text>
          </TouchableOpacity>
        </View>
        {filteredDate && (
          <Text style={{ color: "#666", marginBottom: 8, textAlign: "center" }}>
            Mostrando sesiones del {filteredDate}
          </Text>
        )}
      </View>
      <FlatList
        data={rows}
        keyExtractor={(item) => item.key}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => {
          if (item.type === "month") {
            return (
              <Text style={{ fontSize: 18, fontWeight: "700", marginBottom: 12, textAlign: "center" }}>
                {item.label}
              </Text>
            );
          }
          if (item.type === "day") {
            return (
              <Text style={{ fontSize: 14, fontWeight: "600", marginBottom: 6, color: "#444", textAlign: "center" }}>
                {item.label}
              </Text>
            );
          }
          const session = item.session;
          const displayTitle = session.title || formatDayLabel(session);
          const displaySubtitle = session.title ? formatDayLabel(session) : "Sesión del día";
          return (
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
                alignItems: "center",
              }}
              onPress={() => navigation.push("Detail", { sessionId: session.id })}
            >
              <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center" }}>{displayTitle}</Text>
              <Text style={{ color: "#666", marginTop: 4, textAlign: "center" }}>{displaySubtitle}</Text>
              <View style={{ flexDirection: "row", marginTop: 8, flexWrap: "wrap", justifyContent: "center" }}>
                {session.is_rest_day && <Badge label="Rest" />}
                {session.deload_week && <Badge label="Deload" />}
                {session.data_status === "external_reference" && <Badge label="External" />}
                {session.session_tags?.map((tag) => (
                  <Badge key={tag} label={tag} />
                ))}
              </View>
              <Text style={{ marginTop: 8, color: "#333", textAlign: "center" }}>
                Duración estimada: {session.estimated_duration_min ?? "—"} min
              </Text>
            </TouchableOpacity>
          );
        }}
      />
    </SafeAreaView>
  );
}


function WorkoutsDbScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6", alignItems: "center", justifyContent: "center" }}>
      <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center" }}>WorkoutsDDBB</Text>
      <Text style={{ marginTop: 8, color: "#555", textAlign: "center" }}>
        Base de datos de WODs y sesiones recopiladas
      </Text>
    </SafeAreaView>
  );
}

function AnalysisScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6", alignItems: "center", justifyContent: "center" }}>
      <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center" }}>Análisis</Text>
      <Text style={{ marginTop: 8, color: "#555", textAlign: "center" }}>
        Métricas y tendencias de entrenamiento
      </Text>
    </SafeAreaView>
  );
}

function CoachScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6", alignItems: "center", justifyContent: "center" }}>
      <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center" }}>Coach</Text>
      <Text style={{ marginTop: 8, color: "#555", textAlign: "center" }}>
        Espacio para notas y planificación del coach
      </Text>
    </SafeAreaView>
  );
}

function SessionDetailScreen({ route }: any) {
  const { sessionId } = route.params;
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { basicAuth } = useContext(AuthContext);

  useEffect(() => {
    if (!basicAuth) {
      return;
    }
    setLoading(true);
    fetch(`${API_BASE}/sessions/${sessionId}`, {
      headers: { Authorization: basicAuth },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => setSession(data))
      .finally(() => setLoading(false));
  }, [sessionId, basicAuth]);

  if (loading || !session) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12 }}>Cargando detalles...</Text>
      </View>
    );
  }

  const detailTitleParts: string[] = [];
  if (session.weekday) detailTitleParts.push(session.weekday);
  if (session.date) detailTitleParts.push(session.date);
  if (session.title) detailTitleParts.push(session.title);
  const detailTitle = detailTitleParts.length ? detailTitleParts.join(" - ") : "Sesión";

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f5f5f5" }} contentContainerStyle={{ padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: "700", textAlign: "center" }}>{detailTitle}</Text>
      <View style={{ flexDirection: "row", marginTop: 8, justifyContent: "center" }}>
        {(session.session_tags || []).map((tag) => (
          <Badge key={tag} label={tag} />
        ))}
        {session.is_rest_day && <Badge label="Descanso" />}
        {session.deload_week && <Badge label="Deload" />}
        {session.data_status === "external_reference" && <Badge label="Referencia externa" />}
      </View>
      <Text style={{ marginTop: 8, fontWeight: "600", textAlign: "center" }}>
        Duración estimada: {session.estimated_duration_min ?? "—"} min
      </Text>
      {session.blocks && session.blocks.length > 0 && (
        <View style={{ marginTop: 12 }}>
          <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center" }}>
            Bloques
          </Text>
          {session.blocks.map((block) => (
            <Text key={block.id} style={{ marginTop: 4, textAlign: "center", color: "#444" }}>
              {block.title || "Bloque"}
            </Text>
          ))}
        </View>
      )}

      {session.warmup && (
        <View style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "600", textAlign: "center" }}>Warm-up</Text>
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
          <Text style={{ fontSize: 16, fontWeight: "600", textAlign: "center" }}>{block.title || "Bloque"}</Text>
          <Text style={{ color: "#888", marginTop: 2, textAlign: "center" }}>{block.content_mode}</Text>
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


function SessionsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: "#0f172a" }, headerTintColor: "#fff" }}>
      <Stack.Screen name="Sessions" component={SessionListScreen} />
      <Stack.Screen name="Detail" component={SessionDetailScreen} options={{ title: "Detalle de sesión" }} />
    </Stack.Navigator>
  );
}

export default function App() {
  const [username, setUsername] = useState(API_USER);
  const [password, setPassword] = useState(API_PASS);
  const [basicAuth, setBasicAuth] = useState(buildBasicAuth(API_USER, API_PASS));
  const [loginError, setLoginError] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(true);

  useEffect(() => {
    if (Platform.OS !== "web") return;
    try {
      const storedUser = window.localStorage.getItem("coaich_user") || "";
      const storedPass = window.localStorage.getItem("coaich_pass") || "";
      if (storedUser && storedPass) {
        setUsername(storedUser);
        setPassword(storedPass);
        setBasicAuth(buildBasicAuth(storedUser, storedPass));
      }
    } catch {
      // ignore storage errors
    }
  }, []);

  const handleLogin = () => {
    setLoginError(null);
    fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Credenciales inválidas");
        }
        return res.json();
      })
      .then(() => {
        const auth = buildBasicAuth(username, password);
        setBasicAuth(auth);
        if (Platform.OS === "web") {
          try {
            if (rememberMe) {
              window.localStorage.setItem("coaich_user", username);
              window.localStorage.setItem("coaich_pass", password);
            } else {
              window.localStorage.removeItem("coaich_user");
              window.localStorage.removeItem("coaich_pass");
            }
          } catch {
            // ignore storage errors
          }
        }
      })
      .catch((err) => setLoginError(err.message || "Error de autenticación"));
  };

  const handleLogout = () => {
    setBasicAuth("");
    setLoginError(null);
    if (Platform.OS === "web") {
      try {
        window.localStorage.removeItem("coaich_user");
        window.localStorage.removeItem("coaich_pass");
      } catch {
        // ignore storage errors
      }
    }
  };

  useEffect(() => {
    if (!basicAuth) return;
    const timeoutMs = AUTO_LOGOUT_MIN * 60 * 1000;
    const timer = setTimeout(() => {
      handleLogout();
    }, timeoutMs);
    return () => clearTimeout(timer);
  }, [basicAuth]);

  if (!basicAuth) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: "center", padding: 16, backgroundColor: "#f1f5f9" }}>
        <View style={{ backgroundColor: "white", padding: 20, borderRadius: 14, maxWidth: 360, width: "100%", alignSelf: "center", shadowColor: "#000", shadowOpacity: 0.08, shadowRadius: 10, elevation: 3 }}>
          <Text style={{ fontSize: 20, fontWeight: "700", marginBottom: 12 }}>Iniciar sesión</Text>
          <Text style={{ marginBottom: 6, color: "#475569", textAlign: "center" }}>Usuario</Text>
          <TextInput
            value={username}
            onChangeText={setUsername}
            placeholder="usuario"
            autoCapitalize="none"
            style={{
              borderWidth: 1,
              borderColor: "#e2e8f0",
              borderRadius: 8,
              padding: 9,
              marginBottom: 12,
            }}
          />
          <Text style={{ marginBottom: 6, color: "#475569", textAlign: "center" }}>Contraseña</Text>
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="contraseña"
            secureTextEntry
            style={{
              borderWidth: 1,
              borderColor: "#e2e8f0",
              borderRadius: 8,
              padding: 9,
              marginBottom: 12,
            }}
          />
          <TouchableOpacity
            onPress={() => setRememberMe((prev) => !prev)}
            style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}
          >
            <View
              style={{
                width: 18,
                height: 18,
                borderWidth: 1,
                borderColor: "#333",
                marginRight: 8,
                backgroundColor: rememberMe ? "#111" : "transparent",
              }}
            />
            <Text>Recordarme en este navegador</Text>
          </TouchableOpacity>
          {loginError && <Text style={{ color: "#b91c1c", marginBottom: 8, textAlign: "center" }}>{loginError}</Text>}
          <TouchableOpacity
            onPress={handleLogin}
            style={{ backgroundColor: "#2563eb", padding: 12, borderRadius: 8 }}
          >
            <Text style={{ color: "white", textAlign: "center", fontWeight: "700" }}>Entrar</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <AuthContext.Provider value={{ basicAuth, username, logout: handleLogout }}>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            headerStyle: { backgroundColor: "#0f172a" },
            headerTintColor: "#fff",
            tabBarStyle: { backgroundColor: "#fff" },
            tabBarLabelStyle: { fontSize: 12 },
          }}
        >
          <Tab.Screen name="Sessions" component={SessionsStack} />
          <Tab.Screen name="WorkoutsDDBB" component={WorkoutsDbScreen} />
          <Tab.Screen name="Análisis" component={AnalysisScreen} />
          <Tab.Screen name="Coach" component={CoachScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </AuthContext.Provider>
  );
}
