import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Household } from "../api/types";
import { HouseholdSelector } from "../components/HouseholdSelector";
import { useHouseholds } from "../hooks/useAssets";
import { AssetForm } from "../components/AssetForm";

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
    <div style={{ padding: 24 }}>
      <h1>Capture — Manual Create</h1>
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center" }}>
        <HouseholdSelector
          value={effective}
          onChange={(id) => {
            setHouseholdId(id);
            localStorage.setItem("household_id", id);
          }}
          households={households as Household[] | undefined}
          showLabel={true}
          labelStyle={{ fontSize: 13 }}
          selectStyle={{ padding: 6, borderRadius: 6, marginLeft: 6 }}
          emptyOptionLabel=""
        />
      </div>
      {!effective ? (
        <div style={{ color: "#6b7280" }}>No household available — seed the database first.</div>
      ) : (
        <AssetForm
          householdId={effective}
          onCreated={(id) => navigate(`/assets/${id}?household_id=${effective}`)}
        />
      )}
    </div>
  );
}
