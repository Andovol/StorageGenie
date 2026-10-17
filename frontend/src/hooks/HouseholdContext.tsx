import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { Household } from "../api/types";
import { useHouseholds } from "./useAssets";

export interface HouseholdContextValue {
  households: Household[] | undefined;
  isError: boolean;
  error: unknown;
  householdId: string;
}

const HouseholdContext = createContext<HouseholdContextValue | null>(null);

/**
 * SG-196 G1: the one household read for the whole shell. Every route consumes
 * this context instead of running its own useHouseholds query, so one fetch
 * serves the list. SG-208/D-13: the context only RESOLVES the household
 * (stored id else first household, auto-persisted) — it exposes no setter and
 * drives no switching UI.
 */
export function HouseholdProvider({ children }: { children: ReactNode }) {
  const { data: households, isError, error } = useHouseholds();
  const [householdId, setResolvedHouseholdId] = useState(() =>
    typeof localStorage !== "undefined" ? localStorage.getItem("household_id") || "" : ""
  );

  // Behavior-preservation rail (every route did this for itself): localStorage
  // first, else the first household, with the fallback auto-persisted. D-13:
  // the user cannot hold several households, so nothing can switch it later.
  useEffect(() => {
    if (!householdId && households?.[0]) {
      setResolvedHouseholdId(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const value = useMemo(
    () => ({ households, isError, error, householdId }),
    [households, isError, error, householdId]
  );

  return <HouseholdContext.Provider value={value}>{children}</HouseholdContext.Provider>;
}

export function useHouseholdContext(): HouseholdContextValue {
  const value = useContext(HouseholdContext);
  if (!value) {
    throw new Error("useHouseholdContext must be used within a HouseholdProvider");
  }
  return value;
}
