import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useHouseholds } from "../hooks/useAssets";
import { AssetForm } from "../components/AssetForm";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";

export function CapturePage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(() => localStorage.getItem("household_id") || "");
  const navigate = useNavigate();

  useEffect(() => {
    if (households && households.length && !householdId) {
      const first = households[0].id;
      setHouseholdId(first);
      localStorage.setItem("household_id", first);
    }
  }, [households, householdId]);

  const effective = householdId || households?.[0]?.id || "";

  return (
    <PageContainer className="text-foreground">
      <h1 className="page-header text-foreground">Capture — Manual Create</h1>
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center" }}>
        <label style={{ fontSize: 13 }}>
          Household{" "}
          <select
            className={THEMED_CONTROL_CLASS}
            value={effective}
            onChange={(e) => {
              setHouseholdId(e.target.value);
              localStorage.setItem("household_id", e.target.value);
            }}
            style={{ ...CONTROL_STYLE, marginLeft: 6 }}
          >
            {(households || []).map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {!effective ? (
        <div className="text-muted-foreground">No household available — seed the database first.</div>
      ) : (
        <PageContainer variant="form">
          <AssetForm
            householdId={effective}
            onCreated={(id) => navigate(`/assets/${id}?household_id=${effective}`)}
          />
        </PageContainer>
      )}
    </PageContainer>
  );
}
