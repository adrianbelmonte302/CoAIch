import React, { createContext, useContext, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Image,
  Platform,
  Dimensions,
  SafeAreaView,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { NavigationContainer, useNavigation } from "@react-navigation/native";
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

type ProgramDaySummary = {
  id: string;
  day_id: string;
  date?: string;
  weekday?: string;
  display_title?: string;
  is_rest_day?: boolean;
  deload_week?: boolean;
  day_type?: string;
  program_source?: string;
  athlete_ref?: string;
  session_context?: {
    tags?: string[];
    estimated_duration_min?: number | null;
    priority?: string | null;
  };
};

type ProgramDayDetail = ProgramDaySummary & {
  schema_version?: string;
  entity_type?: string;
  classification?: Record<string, unknown> | null;
  related_workout_ids?: string[] | null;
  related_competition_ids?: string[] | null;
  source_integrity?: Record<string, unknown> | null;
  raw_content?: Record<string, unknown> | null;
  session_flow?: Record<string, any> | null;
  execution_log?: Record<string, unknown> | null;
  athlete_feedback?: Record<string, unknown> | null;
  derived_metrics?: Record<string, unknown> | null;
  ai_annotations?: Record<string, unknown> | null;
};

type DisplayDay = {
  id: string;
  date?: string;
  weekday?: string;
  title?: string;
  is_rest_day?: boolean;
  deload_week?: boolean;
  tags: string[];
  estimated_duration_min?: number | null;
  raw: ProgramDaySummary;
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

function MonthYearSelect({
  value,
  options,
  onChange,
}: {
  value: string;
  options: string[];
  onChange: (next: string) => void;
}) {
  if (Platform.OS === "web") {
    return React.createElement(
      "select",
      {
        value,
        onChange: (event: any) => onChange(event.target.value),
        style: {
          borderWidth: 1,
          borderColor: "#e2e8f0",
          borderRadius: 8,
          padding: "8px 10px",
          backgroundColor: "white",
          fontSize: "14px",
        },
      },
      options.map((opt) =>
        React.createElement(
          "option",
          { key: opt, value: opt },
          opt === "all" ? "Todos los meses" : formatMonthLabel(opt)
        )
      )
    );
  }
  return (
    <TouchableOpacity
      onPress={() => {
        // fallback: no-op for native without picker
      }}
      style={{
        borderWidth: 1,
        borderColor: "#e2e8f0",
        borderRadius: 8,
        paddingHorizontal: 10,
        paddingVertical: 8,
        backgroundColor: "white",
        minWidth: 180,
      }}
    >
      <Text style={{ textAlign: "center" }}>
        {value === "all" ? "Todos los meses" : formatMonthLabel(value)}
      </Text>
    </TouchableOpacity>
  );
}


function formatDuration(value?: number | string | null): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(num)) return "—";
  return String(Math.round(num));
}

function renderMultiline(text?: string) {
  if (!text) return null;
  return text.split("\n").map((line, idx) => (
    <Text key={`line-${idx}`} style={{ marginTop: idx ? 6 : 0, textAlign: "center" }}>
      {line}
    </Text>
  ));
}

function extractText(value?: any): string | null {
  if (!value) return null;
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    const entries = Object.entries(value);
    if (!entries.length) return null;
    if (entries.length === 1) {
      const loneKey = entries[0]?.[0];
      const loneValue = entries[0]?.[1];
      if (typeof loneValue === "string" && loneValue.trim()) {
        return loneValue.trim();
      }
      if ((loneValue === null || loneValue === undefined || loneValue === "") && loneKey?.trim()) {
        return loneKey.trim();
      }
    }
    const structuredLines: string[] = [];
    entries.forEach(([key, entry]) => {
      if (typeof entry === "string" && entry.trim()) {
        structuredLines.push(key ? `${key}: ${entry.trim()}` : entry.trim());
      } else if (entry === null || entry === undefined || entry === "") {
        if (key) structuredLines.push(key);
      } else if (typeof entry === "number" || typeof entry === "boolean") {
        structuredLines.push(`${key}: ${entry}`);
      }
    });
    if (structuredLines.length) return structuredLines.join("\n");
  }
  const parts: string[] = [];
  ["raw_text", "text", "description", "mobility", "activation", "quote", "literal_day_text"].forEach(
    (key) => {
      const entry = value?.[key];
      if (typeof entry === "string" && entry.trim()) {
        parts.push(entry.trim());
      }
    }
  );
  if (parts.length) return parts.join("\n");
  return null;
}

function renderTextBlock(value?: any) {
  const text = extractText(value);
  if (!text) return null;
  return renderMultiline(text);
}

function normalizeValueToLines(value?: any): string[] {
  if (value === null || value === undefined) return [];
  if (typeof value === "string") {
    return value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
  }
  if (Array.isArray(value)) {
    return value.map((entry) => String(entry)).filter(Boolean);
  }
  if (typeof value === "object") {
    try {
      return [JSON.stringify(value)];
    } catch {
      return [String(value)];
    }
  }
  return [String(value)];
}

function WarmupCard({ warmup }: { warmup: any }) {
  if (!warmup) return null;
  const sections: Array<{ label: string; lines: string[] }> = [
    { label: "Quote", lines: normalizeValueToLines(warmup.quote) },
    { label: "Mobility", lines: normalizeValueToLines(warmup.mobility) },
    { label: "Activation", lines: normalizeValueToLines(warmup.activation) },
    { label: "Warm-up", lines: normalizeValueToLines(warmup.raw_text) },
    { label: "Notas", lines: normalizeValueToLines(warmup.literal_day_text) },
  ].filter((section) => section.lines.length > 0);

  if (!sections.length) return null;

  return (
    <View
      style={{
        marginTop: 16,
        backgroundColor: "white",
        padding: 16,
        borderRadius: 12,
        shadowColor: "#000",
        shadowOpacity: 0.05,
        shadowRadius: 6,
        elevation: 2,
      }}
    >
      <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center", marginBottom: 8 }}>
        Warm-up
      </Text>
      {sections.map((section) => (
        <View key={section.label} style={{ marginTop: 8 }}>
          <Text style={{ fontSize: 12, fontWeight: "700", color: "#2563eb", textAlign: "center" }}>
            {section.label.toUpperCase()}
          </Text>
          {section.lines.map((line, idx) => (
            <Text
              key={`${section.label}-${idx}`}
              style={{ marginTop: idx ? 4 : 6, textAlign: "center", color: "#1f2937" }}
            >
              {line}
            </Text>
          ))}
        </View>
      ))}
    </View>
  );
}

function formatLoad(load?: any): string {
  if (!load) return "";
  const parts: string[] = [];
  if (load.prescribed_kg !== null && load.prescribed_kg !== undefined) {
    parts.push(`${load.prescribed_kg}kg`);
  } else if (load.prescribed_kg_min || load.prescribed_kg_max) {
    parts.push(`${load.prescribed_kg_min ?? ""}-${load.prescribed_kg_max ?? ""}kg`);
  }
  if (load.percent_1rm_min || load.percent_1rm_max) {
    parts.push(`${load.percent_1rm_min ?? ""}-${load.percent_1rm_max ?? ""}% 1RM`);
  }
  if (load.rpe) parts.push(`RPE ${load.rpe}`);
  if (load.rir) parts.push(`RIR ${load.rir}`);
  if (load.load_notes) parts.push(load.load_notes);
  return parts.filter(Boolean).join(" ");
}

function formatSetStructure(entry?: any): string {
  if (!entry) return "";
  const parts: string[] = [];
  if (entry.sets) parts.push(`${entry.sets} sets`);
  if (entry.rounds) parts.push(`${entry.rounds} rounds`);
  if (entry.reps) parts.push(`${entry.reps} reps`);
  if (entry.reps_per_side) parts.push(`${entry.reps_per_side} reps/side`);
  if (entry.duration_min) parts.push(`${entry.duration_min} min`);
  if (entry.duration_sec) parts.push(`${entry.duration_sec} sec`);
  if (entry.distance_m) parts.push(`${entry.distance_m} m`);
  if (entry.calories) parts.push(`${entry.calories} cal`);
  if (entry.rest_sec) parts.push(`rest ${entry.rest_sec}s`);
  const loadText = formatLoad(entry.load);
  if (loadText) parts.push(loadText);
  if (entry.tempo) parts.push(`tempo ${entry.tempo}`);
  if (entry.target) parts.push(`target ${entry.target}`);
  if (entry.notes) parts.push(entry.notes);
  return parts.filter(Boolean).join(" · ");
}


function getWeekdayFromDate(dateStr?: string): string {
  if (!dateStr) return "";
  const d = new Date(`${dateStr}T00:00:00`);
  if (Number.isNaN(d.getTime())) return "";
  const names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  return names[d.getDay()] || "";
}


function normalizeBlockText(value?: string | null): string {
  return (value || "").toLowerCase();
}

function normalizeType(value?: string | null): string {
  if (!value) return "";
  return value.trim().toLowerCase();
}

function formatTypeLabel(value?: string | null): string {
  const normalized = normalizeType(value);
  if (!normalized) return "";
  if (normalized === "rest") return "Rest";
  if (normalized === "strength") return "Strength";
  if (normalized === "stamina") return "Stamina";
  if (normalized === "gymnastic") return "Gymnastic";
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function detectTypesFromText(text: string, types: Set<string>) {
  if (!text) return;
  if (text.includes("strength") || text.includes("fuerza") || text.includes("power") || text.includes("weightlifting") || text.includes("halter")) {
    types.add("strength");
  }
  if (text.includes("stamina") || text.includes("endurance") || text.includes("engine") || text.includes("conditioning") || text.includes("aerobic")) {
    types.add("stamina");
  }
  if (text.includes("gymnastic") || text.includes("gymnastics") || text.includes("gimnast") || text.includes("gimnastic")) {
    types.add("gymnastic");
  }
  if (text.includes("rest") || text.includes("descanso") || text.includes("recovery")) {
    types.add("rest");
  }
}

function getProgramDayTypes(programDay: ProgramDaySummary | ProgramDayDetail): string[] {
  const types = new Set<string>();
  if (programDay.is_rest_day) types.add("rest");
  (programDay.session_context?.tags || []).forEach((tag) =>
    detectTypesFromText(normalizeBlockText(tag), types)
  );
  detectTypesFromText(normalizeBlockText(programDay.display_title || ""), types);

  const flow = (programDay as ProgramDayDetail).session_flow as any;
  const variants = flow?.variants || [];
  variants.forEach((variant: any) => {
    detectTypesFromText(normalizeBlockText(variant?.title || ""), types);
    (variant?.blocks || []).forEach((block: any) => {
      detectTypesFromText(normalizeBlockText(block?.title || ""), types);
      detectTypesFromText(normalizeBlockText(block?.block_type || ""), types);
      detectTypesFromText(normalizeBlockText(block?.prescription?.format || ""), types);
      (block?.prescription?.sub_blocks || []).forEach((sub: any) => {
        detectTypesFromText(normalizeBlockText(sub?.title || ""), types);
        detectTypesFromText(normalizeBlockText(sub?.format || ""), types);
        (sub?.exercises || []).forEach((exercise: any) => {
          detectTypesFromText(normalizeBlockText(exercise?.name || ""), types);
        });
      });
    });
  });

  return Array.from(types)
    .map((value) => normalizeType(value))
    .filter(Boolean);
}

function getProgramDayBlockTitles(programDay: ProgramDaySummary | ProgramDayDetail): string[] {
  const flow = (programDay as ProgramDayDetail).session_flow as any;
  if (!flow) return [];
  const titles: string[] = [];
  const sharedBlocks = flow.shared_blocks || [];
  sharedBlocks.forEach((block: any) => {
    if (block?.title) titles.push(block.title);
  });
  (flow.variants || []).forEach((variant: any) => {
    (variant?.blocks || []).forEach((block: any) => {
      titles.push(block?.title || block?.block_id || "Bloque");
    });
  });
  return titles;
}

function toDisplayDayFromProgramDay(programDay: ProgramDaySummary): DisplayDay {
  return {
    id: programDay.id,
    date: programDay.date,
    weekday: programDay.weekday,
    title: programDay.display_title || "Programa del día",
    is_rest_day: programDay.is_rest_day,
    deload_week: programDay.deload_week,
    tags: programDay.session_context?.tags || [],
    estimated_duration_min: programDay.session_context?.estimated_duration_min ?? null,
    raw: programDay,
  };
}

function formatDayLabel(session: { date?: string; weekday?: string }): string {
  if (!session.date) return "Fecha sin definir";
  const parts: string[] = [];
  const weekday = session.weekday || getWeekdayFromDate(session.date);
  if (weekday) parts.push(weekday);
  parts.push(session.date);
  return parts.join(" ");
}

type ListRow =
  | { type: "month"; key: string; label: string }
  | { type: "day"; key: string; label: string }
  | { type: "session"; key: string; session: DisplayDay };


function getMonthLabel(year: number, monthIndex: number): string {
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
  return `${monthNames[monthIndex]} ${year}`;
}

function buildMonthDays(year: number, monthIndex: number) {
  const first = new Date(year, monthIndex, 1);
  const last = new Date(year, monthIndex + 1, 0);
  const daysInMonth = last.getDate();
  const startWeekday = (first.getDay() + 6) % 7; // Monday=0
  const cells: Array<{ day?: number }> = [];
  for (let i = 0; i < startWeekday; i++) cells.push({});
  for (let d = 1; d <= daysInMonth; d++) cells.push({ day: d });
  while (cells.length % 7 !== 0) cells.push({});
  return cells;
}

function toDateKey(year: number, monthIndex: number, day: number): string {
  const mm = String(monthIndex + 1).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${year}-${mm}-${dd}`;
}

function CalendarPicker({
  year,
  monthIndex,
  datesWithSessions,
  selectedDate,
  onSelectDate,
  onChangeMonth,
  size = "normal",
}: {
  year: number;
  monthIndex: number;
  datesWithSessions: Set<string>;
  selectedDate: string;
  onSelectDate: (date: string) => void;
  onChangeMonth: (delta: number) => void;
  size?: "normal" | "compact";
}) {
  const cells = buildMonthDays(year, monthIndex);
  const weekDays = ["L", "M", "X", "J", "V", "S", "D"];
  const isCompact = size === "compact";
  const cellHeight = isCompact ? 26 : 36;
  const circleSize = isCompact ? 20 : 28;
  const headerFont = isCompact ? 14 : 18;
  const weekDayFont = isCompact ? 10 : 12;
  const dayFont = isCompact ? 11 : 14;
  return (
    <View style={{ width: "100%", marginBottom: isCompact ? 8 : 12 }}>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", marginBottom: 8 }}>
        <TouchableOpacity
          onPress={() => onChangeMonth(-1)}
          style={{ paddingHorizontal: 12, paddingVertical: isCompact ? 4 : 6 }}
        >
          <Text style={{ fontSize: headerFont, fontWeight: "700", color: "#2563eb" }}>{"<"}</Text>
        </TouchableOpacity>
        <Text style={{ fontSize: headerFont, fontWeight: "700", textAlign: "center" }}>
          {getMonthLabel(year, monthIndex)}
        </Text>
        <TouchableOpacity
          onPress={() => onChangeMonth(1)}
          style={{ paddingHorizontal: 12, paddingVertical: isCompact ? 4 : 6 }}
        >
          <Text style={{ fontSize: headerFont, fontWeight: "700", color: "#2563eb" }}>{">"}</Text>
        </TouchableOpacity>
      </View>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
        {weekDays.map((d) => (
          <Text
            key={d}
            style={{ width: "14.2%", textAlign: "center", color: "#64748b", fontSize: weekDayFont }}
          >
            {d}
          </Text>
        ))}
      </View>
      <View style={{ flexDirection: "row", flexWrap: "wrap" }}>
        {cells.map((cell, idx) => {
          if (!cell.day) {
            return <View key={`empty-${idx}`} style={{ width: "14.2%", height: cellHeight }} />;
          }
          const dateKey = toDateKey(year, monthIndex, cell.day);
          const hasSession = datesWithSessions.has(dateKey);
          const isSelected = selectedDate === dateKey;
          return (
            <TouchableOpacity
              key={dateKey}
              onPress={() => onSelectDate(dateKey)}
              style={{ width: "14.2%", height: cellHeight, alignItems: "center", justifyContent: "center" }}
            >
              <View
                style={{
                  width: circleSize,
                  height: circleSize,
                  borderRadius: circleSize / 2,
                  backgroundColor: isSelected ? "#2563eb" : hasSession ? "#dbeafe" : "transparent",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Text style={{ color: isSelected ? "#fff" : "#0f172a", fontSize: dayFont }}>
                  {cell.day}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

function SessionListScreen({ navigation, route }: any) {
  const [programDays, setProgramDays] = useState<ProgramDaySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [jumpDate, setJumpDate] = useState("");
  const [filteredDate, setFilteredDate] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [showCalendar, setShowCalendar] = useState(false);
  const initialShowFilters =
    Platform.OS === "web" && Dimensions.get("window").width >= 900;
  const [showFilters, setShowFilters] = useState(initialShowFilters);
  const [selectedMonthKey, setSelectedMonthKey] = useState("all");
  const today = new Date();
  const [calendarYear, setCalendarYear] = useState(today.getFullYear());
  const [calendarMonth, setCalendarMonth] = useState(today.getMonth());
  const { basicAuth, username, logout } = useContext(AuthContext);

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <View style={{ flexDirection: "row", alignItems: "center" }}><TouchableOpacity onPress={() => navigation.push("Calendar")} style={{ paddingHorizontal: 12 }}><Text style={{ color: "#fff", fontWeight: "600" }}>Calendario</Text></TouchableOpacity><TouchableOpacity onPress={logout} style={{ paddingHorizontal: 12 }}>
          <Text style={{ color: "#fff", fontWeight: "600" }}>Salir</Text>
        </TouchableOpacity></View>
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
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const programRes = await fetch(`${API_BASE}/program-days/`, {
          headers: { Authorization: basicAuth },
        });
        if (!programRes.ok) {
          throw new Error(`API error: ${programRes.status}`);
        }
        const data = await programRes.json();
        if (!active) return;
        setProgramDays(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!active) return;
        setProgramDays([]);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [basicAuth]);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12, textAlign: "center" }}>Cargando sesiones...</Text>
      </View>
    );
  }

  const displayDays = programDays.map(toDisplayDayFromProgramDay);

  const monthKeys = Array.from(
    new Set(displayDays.map((s) => getMonthKey(s.date)))
  ).filter(Boolean);
  monthKeys.sort();
  const monthOptions = ["all", ...monthKeys];

  const allTypes = Array.from(
    new Set(
      displayDays
        .flatMap((s) => getProgramDayTypes(s.raw as ProgramDaySummary))
        .filter(Boolean)
    )
  ).sort();

  const filteredByMonth =
    selectedMonthKey === "all"
      ? displayDays
      : displayDays.filter((s) => getMonthKey(s.date) === selectedMonthKey);

  const filteredByDate = filteredDate
    ? filteredByMonth.filter((s) => s.date === filteredDate)
    : filteredByMonth;

  const effectiveSessions = selectedTypes.length
    ? filteredByDate.filter((s) => {
        const types = getProgramDayTypes(s.raw as ProgramDaySummary);
        return types.some((t) => selectedTypes.includes(t));
      })
    : filteredByDate;

  const highlightDates = selectedTypes.length
    ? new Set(
        filteredByMonth
          .filter((s) => {
            const types = getProgramDayTypes(s.raw as ProgramDaySummary);
            return types.some((t) => selectedTypes.includes(t));
          })
          .map((s) => s.date)
          .filter(Boolean) as string[]
      )
    : new Set(filteredByMonth.map((s) => s.date).filter(Boolean) as string[]);

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
      <FlatList
        data={rows}
        keyExtractor={(item) => item.key}
        contentContainerStyle={{ padding: 16, paddingTop: 10 }}
        ListHeaderComponent={
          <View style={{ alignItems: "center", marginBottom: 10 }}>
            <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
              <TouchableOpacity
                onPress={() => setShowFilters((prev) => !prev)}
                style={{
                  backgroundColor: "#0f172a",
                  paddingHorizontal: 12,
                  paddingVertical: 6,
                  borderRadius: 999,
                }}
              >
                <Text style={{ color: "#fff", fontWeight: "700" }}>
                  {showFilters ? "Ocultar filtros" : "Mostrar filtros"}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => {
                  setFilteredDate("");
                  setJumpDate("");
                }}
                style={{
                  backgroundColor: "#eee",
                  paddingHorizontal: 12,
                  paddingVertical: 6,
                  borderRadius: 999,
                  justifyContent: "center",
                }}
              >
                <Text style={{ color: "#333", fontWeight: "600" }}>Ver todo</Text>
              </TouchableOpacity>
            </View>

            {showFilters && (
              <View style={{ marginTop: 8, alignItems: "center" }}>
                <Text style={{ fontSize: 12, color: "#333", marginBottom: 4, textAlign: "center" }}>
                  Filtrar por tipo
                </Text>
                <View style={{ flexDirection: "row", justifyContent: "center", flexWrap: "wrap", marginBottom: 6 }}>
                  {(allTypes.length ? allTypes : ["strength", "rest", "stamina", "gymnastic"]).map((t) => {
                    const active = selectedTypes.includes(t);
                    return (
                      <TouchableOpacity
                        key={t}
                        onPress={() => {
                          setSelectedTypes((prev) =>
                            prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
                          );
                        }}
                        style={{
                          paddingHorizontal: 8,
                          paddingVertical: 4,
                          borderRadius: 999,
                          margin: 3,
                          backgroundColor: active ? "#2563eb" : "#e2e8f0",
                        }}
                      >
                        <Text style={{ color: active ? "#fff" : "#0f172a", fontWeight: "600" }}>
                          {formatTypeLabel(t)}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>
                <View style={{ flexDirection: "row", gap: 8, marginBottom: 6, flexWrap: "wrap", justifyContent: "center" }}>
                  <MonthYearSelect
                    value={selectedMonthKey}
                    options={monthOptions}
                    onChange={(next) => {
                      setSelectedMonthKey(next);
                      setFilteredDate("");
                      if (next !== "all" && next !== "Fecha desconocida") {
                        const [y, m] = next.split("-");
                        const yNum = Number(y);
                        const mNum = Number(m);
                        if (Number.isFinite(yNum) && Number.isFinite(mNum)) {
                          setCalendarYear(yNum);
                          setCalendarMonth(Math.max(0, mNum - 1));
                        }
                      }
                    }}
                  />
                  <TouchableOpacity
                    onPress={() => setSelectedTypes([])}
                    style={{
                      backgroundColor: "#e2e8f0",
                      paddingHorizontal: 12,
                      paddingVertical: 6,
                      borderRadius: 8,
                    }}
                  >
                    <Text style={{ color: "#0f172a", fontWeight: "600" }}>Reset tipos</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => setShowCalendar((prev) => !prev)}
                    style={{
                      backgroundColor: "#0f172a",
                      paddingHorizontal: 12,
                      paddingVertical: 6,
                      borderRadius: 8,
                    }}
                  >
                    <Text style={{ color: "#fff", fontWeight: "600" }}>
                      {showCalendar ? "Ocultar calendario" : "Mostrar calendario"}
                    </Text>
                  </TouchableOpacity>
                </View>
                {showCalendar && (
                  <CalendarPicker
                    year={calendarYear}
                    monthIndex={calendarMonth}
                    datesWithSessions={highlightDates}
                    selectedDate={filteredDate}
                    onSelectDate={(date) => {
                      setFilteredDate(date);
                      setJumpDate(date);
                    }}
                    onChangeMonth={(delta) => {
                      const next = new Date(calendarYear, calendarMonth + delta, 1);
                      setCalendarYear(next.getFullYear());
                      setCalendarMonth(next.getMonth());
                    }}
                    size="compact"
                  />
                )}
              </View>
            )}

            {filteredDate && (
              <Text style={{ color: "#666", marginTop: 6, textAlign: "center" }}>
                Mostrando sesiones del {filteredDate}
              </Text>
            )}
          </View>
        }
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
              <View
                style={{
                  alignSelf: "center",
                  backgroundColor: "#e2e8f0",
                  paddingHorizontal: 14,
                  paddingVertical: 6,
                  borderRadius: 999,
                  marginBottom: 10,
                }}
              >
                <Text style={{ fontSize: 18, fontWeight: "800", color: "#0f172a", textAlign: "center" }}>
                  {item.label}
                </Text>
              </View>
            );
          }
          const session = item.session as DisplayDay;
          const displayTitle = session.title || formatDayLabel(session);
          const displaySubtitle = session.title ? formatDayLabel(session) : "Sesión del día";
          const sessionTypes = getProgramDayTypes(session.raw as ProgramDaySummary).filter(
            (t) => !(session.is_rest_day && t === "rest")
          );
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
              onPress={() => navigation.push("Detail", { sessionId: session.id, kind: "program_day" })}
            >
              <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center" }}>{displayTitle}</Text>
              <Text style={{ color: "#666", marginTop: 4, textAlign: "center" }}>{displaySubtitle}</Text>
              <View style={{ flexDirection: "row", marginTop: 8, flexWrap: "wrap", justifyContent: "center" }}>
                {session.is_rest_day && <Badge label="Rest" />}
                {session.deload_week && <Badge label="Deload" />}
                {sessionTypes.map((t) => (
                  <Badge key={t} label={formatTypeLabel(t)} />
                ))}
                {session.tags.map((tag) => (
                  <Badge key={tag} label={tag} />
                ))}
              </View>
              <Text style={{ marginTop: 8, color: "#333", textAlign: "center" }}>
                Duración estimada: {formatDuration(session.estimated_duration_min)} min
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


function CalendarViewScreen() {
  const { basicAuth } = useContext(AuthContext);
  const [programDays, setProgramDays] = useState<ProgramDaySummary[]>([]);
  const [detailCache, setDetailCache] = useState<Record<string, ProgramDayDetail>>({});
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState("");
  const today = new Date();
  const [calendarYear, setCalendarYear] = useState(today.getFullYear());
  const [calendarMonth, setCalendarMonth] = useState(today.getMonth());

  useEffect(() => {
    if (!basicAuth) return;
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const programRes = await fetch(`${API_BASE}/program-days/`, {
          headers: { Authorization: basicAuth },
        });
        if (!programRes.ok) throw new Error(`API error: ${programRes.status}`);
        const data = await programRes.json();
        if (!active) return;
        setProgramDays(Array.isArray(data) ? data : []);
        if (!selectedDate && Array.isArray(data) && data.length > 0) {
          setSelectedDate(data[0].date || "");
        }
      } catch (err) {
        if (!active) return;
        setProgramDays([]);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [basicAuth]);


  async function fetchDetailsForDate(date: string) {
    const targets = programDays.filter((s) => s.date === date);
    if (targets.length === 0) return;
    const entries = await Promise.all(
      targets.map(async (s) => {
        try {
          const res = await fetch(`${API_BASE}/program-days/${s.id}`, {
            headers: { Authorization: basicAuth },
          });
          if (!res.ok) return [s.id, null] as const;
          const data = await res.json();
          return [s.id, data] as const;
        } catch (err) {
          return [s.id, null] as const;
        }
      })
    );
    const next = { ...detailCache };
    entries.forEach(([id, data]) => {
      if (data) next[String(id)] = data as ProgramDayDetail;
    });
    setDetailCache(next);
  }

  useEffect(() => {
    if (!basicAuth || !selectedDate) return;
    fetchDetailsForDate(selectedDate);
  }, [basicAuth, selectedDate, programDays.length]);

  const displayDays = programDays.map(toDisplayDayFromProgramDay);
  const datesWithSessions = new Set(displayDays.map((s) => s.date).filter(Boolean) as string[]);
  const sessionsForDate = selectedDate
    ? displayDays.filter((s) => s.date === selectedDate)
    : [];

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12, textAlign: "center" }}>Cargando calendario...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f6f6f6" }}>
      <View style={{ paddingHorizontal: 16, paddingTop: 12, alignItems: "center" }}>
        <CalendarPicker
          year={calendarYear}
          monthIndex={calendarMonth}
          datesWithSessions={datesWithSessions}
          selectedDate={selectedDate}
          onSelectDate={(date) => setSelectedDate(date)}
          onChangeMonth={(delta) => {
            const next = new Date(calendarYear, calendarMonth + delta, 1);
            setCalendarYear(next.getFullYear());
            setCalendarMonth(next.getMonth());
          }}
        />
      </View>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {selectedDate ? (
          sessionsForDate.length > 0 ? (
            sessionsForDate.map((session) => {
              const detail = detailCache[session.id] || session.raw;
              const displayTitle = (detail as ProgramDayDetail).display_title || "Programa del día";
              const durationValue = (detail as ProgramDayDetail).session_context?.estimated_duration_min;
              const tags = (detail as ProgramDayDetail).session_context?.tags || [];
              const detailTypes = getProgramDayTypes(detail as ProgramDayDetail).filter(
                (t) => !((detail as ProgramDayDetail).is_rest_day && t === "rest")
              );
              return (
                <View
                  key={session.id}
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
                >
                  <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center" }}>
                    {formatDayLabel(detail as { date?: string; weekday?: string })}
                  </Text>
                  <Text style={{ fontSize: 18, fontWeight: "700", textAlign: "center", marginTop: 4 }}>
                    {displayTitle}
                  </Text>
                  <View style={{ flexDirection: "row", marginTop: 8, flexWrap: "wrap", justifyContent: "center" }}>
                    {detailTypes.map((t) => (
                      <Badge key={t} label={formatTypeLabel(t)} />
                    ))}
                    {tags.map((tag: string) => (
                      <Badge key={tag} label={tag} />
                    ))}
                  </View>
                  <Text style={{ marginTop: 8, color: "#333", textAlign: "center" }}>
                    Duración estimada: {formatDuration(durationValue)} min
                  </Text>
                  {getProgramDayBlockTitles(detail as ProgramDayDetail).length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center" }}>
                        Bloques
                      </Text>
                      {getProgramDayBlockTitles(detail as ProgramDayDetail).map((title, idx) => (
                        <Text
                          key={`${session.id}-block-${idx}`}
                          style={{ marginTop: 4, textAlign: "center", color: "#444" }}
                        >
                          {title}
                        </Text>
                      ))}
                    </View>
                  )}
                </View>
              );
            })
          ) : (
            <Text style={{ textAlign: "center", color: "#666" }}>
              No hay sesiones para esta fecha
            </Text>
          )
        ) : (
          <Text style={{ textAlign: "center", color: "#666" }}>
            Selecciona una fecha en el calendario
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function SessionDetailScreen({ route }: any) {
  const { sessionId } = route.params;
  const [detail, setDetail] = useState<ProgramDayDetail | null>(null);
  const [programDays, setProgramDays] = useState<ProgramDaySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const { basicAuth } = useContext(AuthContext);
  const navigation = useNavigation<any>();

  useEffect(() => {
    if (!basicAuth) {
      return;
    }
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/program-days/${sessionId}`, {
          headers: { Authorization: basicAuth },
        });
        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }
        const data = await res.json();
        if (!active) return;
        setDetail(data);
        const listRes = await fetch(`${API_BASE}/program-days/`, {
          headers: { Authorization: basicAuth },
        });
        if (listRes.ok) {
          const listData = await listRes.json();
          if (Array.isArray(listData)) {
            setProgramDays(listData);
          }
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [sessionId, basicAuth]);

  if (loading || !detail) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12 }}>Cargando detalles...</Text>
      </View>
    );
  }

  const programDay = detail;
  const detailTitleParts: string[] = [];
  if (programDay.weekday) detailTitleParts.push(programDay.weekday);
  if (programDay.date) detailTitleParts.push(programDay.date);
  if (programDay.display_title) detailTitleParts.push(programDay.display_title);
  const detailTitle = detailTitleParts.length ? detailTitleParts.join(" - ") : "Programa del día";
  const sessionFlow = programDay.session_flow as any;
  const variants = sessionFlow?.variants || [];
  const sharedBlocks = sessionFlow?.shared_blocks || [];
  const generalWarmupText = extractText(sessionFlow?.general_warmup);

  const sortedDays = [...programDays].sort((a, b) => {
    const aDate = a.date || "";
    const bDate = b.date || "";
    if (aDate === bDate) return String(a.id).localeCompare(String(b.id));
    return aDate.localeCompare(bDate);
  });
  const currentIndex = sortedDays.findIndex((d) => String(d.id) === String(sessionId));
  const prevDay = currentIndex > 0 ? sortedDays[currentIndex - 1] : null;
  const nextDay = currentIndex >= 0 && currentIndex < sortedDays.length - 1 ? sortedDays[currentIndex + 1] : null;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f5f5f5" }} contentContainerStyle={{ padding: 16 }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 12 }}>
        <TouchableOpacity
          disabled={!prevDay}
          onPress={() => prevDay && navigation.push("Detail", { sessionId: prevDay.id, kind: "program_day" })}
          style={{
            paddingHorizontal: 12,
            paddingVertical: 6,
            borderRadius: 8,
            backgroundColor: prevDay ? "#e2e8f0" : "#f1f5f9",
          }}
        >
          <Text style={{ fontWeight: "700", color: prevDay ? "#0f172a" : "#94a3b8" }}>{"<"} Día anterior</Text>
        </TouchableOpacity>
        <TouchableOpacity
          disabled={!nextDay}
          onPress={() => nextDay && navigation.push("Detail", { sessionId: nextDay.id, kind: "program_day" })}
          style={{
            paddingHorizontal: 12,
            paddingVertical: 6,
            borderRadius: 8,
            backgroundColor: nextDay ? "#e2e8f0" : "#f1f5f9",
          }}
        >
          <Text style={{ fontWeight: "700", color: nextDay ? "#0f172a" : "#94a3b8" }}>Día siguiente {">"}</Text>
        </TouchableOpacity>
      </View>
      <Text style={{ fontSize: 20, fontWeight: "700", textAlign: "center" }}>{detailTitle}</Text>
      <View style={{ flexDirection: "row", marginTop: 8, justifyContent: "center", flexWrap: "wrap" }}>
        {(programDay.session_context?.tags || []).map((tag) => (
          <Badge key={tag} label={tag} />
        ))}
        {programDay.is_rest_day && <Badge label="Descanso" />}
        {programDay.deload_week && <Badge label="Deload" />}
        {getProgramDayTypes(programDay)
          .filter((t) => !(programDay.is_rest_day && t === "rest"))
          .map((t) => (
            <Badge key={t} label={formatTypeLabel(t)} />
          ))}
      </View>
      <Text style={{ marginTop: 8, fontWeight: "600", textAlign: "center" }}>
        Duración estimada: {formatDuration(programDay.session_context?.estimated_duration_min)} min
      </Text>

<<<<<<< HEAD
      {sessionFlow?.general_warmup && <WarmupCard warmup={sessionFlow.general_warmup} />}
=======
      {generalWarmupText && (
        <View style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "600", textAlign: "center" }}>Warm-up</Text>
          {renderMultiline(generalWarmupText)}
        </View>
      )}
>>>>>>> 03408b6d780ec359d5220f84b813e1ed7f20ad0b

      {variants.map((variant: any, idx: number) => (
        <View key={`variant-${idx}`} style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center" }}>
            Variante {variant?.variant_id || idx + 1}
          </Text>
          {variant?.title && (
            <Text style={{ marginTop: 4, textAlign: "center", color: "#444" }}>{variant.title}</Text>
          )}
<<<<<<< HEAD
          {variant?.warmup && <WarmupCard warmup={variant.warmup} />}
=======
          {variant?.warmup && (() => {
            const variantWarmupText = extractText(variant.warmup);
            if (!variantWarmupText) return null;
            if (generalWarmupText && variantWarmupText === generalWarmupText) return null;
            return renderMultiline(variantWarmupText);
          })()}
>>>>>>> 03408b6d780ec359d5220f84b813e1ed7f20ad0b
          {(variant?.blocks || []).map((block: any, bIdx: number) => (
            <View
              key={`variant-${idx}-block-${bIdx}`}
              style={{
                marginTop: 12,
                padding: 16,
                backgroundColor: "white",
                borderRadius: 12,
                shadowColor: "#000",
                shadowOpacity: 0.05,
                shadowRadius: 6,
                elevation: 2,
              }}
            >
              <Text style={{ fontSize: 16, fontWeight: "600", textAlign: "center" }}>
                {block?.title || `Bloque ${bIdx + 1}`}
              </Text>
              {block?.block_type && (
                <Text style={{ color: "#888", marginTop: 2, textAlign: "center" }}>
                  {block.block_type}
                </Text>
              )}
              {block?.coach_notes_literal && (
                <Text style={{ marginTop: 4, fontStyle: "italic", color: "#444", textAlign: "center" }}>
                  {block.coach_notes_literal}
                </Text>
              )}
              {(block?.prescription?.sub_blocks || []).map((sub: any, sIdx: number) => (
                <View key={`sub-${sIdx}`} style={{ marginTop: 8 }}>
                  <Text style={{ fontWeight: "600", textAlign: "center" }}>
                    {sub?.title || `Sub-bloque ${sIdx + 1}`}
                  </Text>
                  {sub?.format && (
                    <Text style={{ color: "#666", textAlign: "center" }}>{sub.format}</Text>
                  )}
                  {renderTextBlock(sub?.description)}
                  {(sub?.exercises || []).map((exercise: any, eIdx: number) => (
                    <View key={`ex-${eIdx}`} style={{ marginTop: 6 }}>
                      <Text style={{ fontWeight: "600", textAlign: "center" }}>{exercise?.name}</Text>
                      {exercise?.format && (
                        <Text style={{ color: "#444", textAlign: "center" }}>{exercise.format}</Text>
                      )}
                      {(exercise?.set_structure || []).map((setEntry: any, sIdx: number) => {
                        const line = formatSetStructure(setEntry);
                        if (!line) return null;
                        return (
                          <Text key={`set-${sIdx}`} style={{ color: "#555", textAlign: "center", marginTop: 2 }}>
                            {line}
                          </Text>
                        );
                      })}
                      {exercise?.notes && renderTextBlock(exercise.notes)}
                    </View>
                  ))}
                </View>
              ))}
            </View>
          ))}
        </View>
      ))}

      {sharedBlocks.length > 0 && (
        <View style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "700", textAlign: "center" }}>Bloques compartidos</Text>
          {sharedBlocks.map((block: any, bIdx: number) => (
            <Text key={`shared-${bIdx}`} style={{ marginTop: 4, textAlign: "center", color: "#444" }}>
              {block?.title || `Bloque ${bIdx + 1}`}
            </Text>
          ))}
        </View>
      )}

      {sessionFlow?.cooldown && (
        <View style={{ marginTop: 16 }}>
          <Text style={{ fontSize: 16, fontWeight: "600", textAlign: "center" }}>Cooldown</Text>
          {renderTextBlock(sessionFlow.cooldown)}
        </View>
      )}
    </ScrollView>
  );
}


function SessionsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: "#0f172a" }, headerTintColor: "#fff" }}>
      <Stack.Screen name="Sessions" component={SessionListScreen} />
      <Stack.Screen name="Calendar" component={CalendarViewScreen} options={{ title: "Calendario" }} />
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
        <View style={{ backgroundColor: "white", padding: 20, borderRadius: 14, maxWidth: 360, width: "100%", alignSelf: "center", shadowColor: "#000", shadowOpacity: 0.08, shadowRadius: 10, elevation: 3 }}><View style={{ alignItems: "center", marginBottom: 12 }}><Image source={{ uri: LOGO_DATA_URI }} style={{ width: 220, height: 64 }} /></View>
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
          screenOptions={({ route }) => ({
            headerStyle: { backgroundColor: "#0f172a" },
            headerTintColor: "#fff",
            tabBarStyle: { backgroundColor: "#fff" },
            tabBarLabelStyle: { fontSize: 12 },
            tabBarIcon: ({ color, size }) => {
              const label =
                route.name === "Sessions"
                  ? "S"
                  : route.name === "WorkoutsDDBB"
                  ? "W"
                  : route.name === "Análisis"
                  ? "A"
                  : "C";
              return (
                <View
                  style={{
                    width: size + 6,
                    height: size + 6,
                    borderRadius: (size + 6) / 2,
                    borderWidth: 2,
                    borderColor: color,
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Text style={{ color, fontWeight: "700", fontSize: 12 }}>{label}</Text>
                </View>
              );
            },
          })}
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


