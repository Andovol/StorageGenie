export function SettingsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>Settings</h1>
      <p style={{ color: "#6b7280", fontSize: 13 }}>
        Phase 0 — household and connection settings. API base: {import.meta.env.VITE_API_BASE || "http://localhost:8000"}
      </p>
      <div style={{ marginTop: 16 }}>
        <button
          onClick={() => {
            localStorage.removeItem("household_id");
            window.location.reload();
          }}
          style={{ padding: "6px 12px", borderRadius: 6, border: "1px solid #d1d5db" }}
        >
          Clear household selection
        </button>
      </div>
    </div>
  );
}
