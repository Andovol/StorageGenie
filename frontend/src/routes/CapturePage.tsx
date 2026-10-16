import { useNavigate } from "react-router-dom";
import { useHouseholdContext } from "../hooks/HouseholdContext";
import { AssetForm } from "../components/AssetForm";
import { HouseholdSelector } from "../components/HouseholdSelector";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";

export function CapturePage() {
  // SG-196 G1: selection state lives in the shared context; the household
  // failure branch now reads the context's error state.
  const {
    households,
    isError: householdsIsError,
    error: householdsError,
    householdId,
    setHouseholdId,
  } = useHouseholdContext();
  const navigate = useNavigate();

  const effective = householdId || households?.[0]?.id || "";

  return (
    <PageContainer className="text-foreground">
      <h1 className="page-header text-foreground">Capture — Manual Create</h1>
      <div style={{ marginBottom: 16, display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
        <HouseholdSelector
          value={effective}
          onChange={setHouseholdId}
          households={households}
          labelStyle={{ fontSize: 13 }}
          selectStyle={{ ...CONTROL_STYLE, marginLeft: 6 }}
          selectClassName={THEMED_CONTROL_CLASS}
          emptyOptionLabel=""
        />
      </div>
      {householdsIsError ? (
        <div role="alert">Could not load households: {String(householdsError)}</div>
      ) : !effective ? (
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
