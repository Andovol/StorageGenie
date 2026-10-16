import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { Household } from "../api/types";
import { useHouseholds } from "./useAssets";

export interface HouseholdContextValue {
  households: Household[] | undefined;
  isError: boolean;
  error: unknown;
  householdId: string;
  setHouseholdId: (id: string) => void;
}

const HouseholdContext = createContext<HouseholdContextValue | null>(null);

/**
 * SG-196 G1: the one household read for the whole shell. Every route selector
 * consumes this context instead of running its own useHouseholds query, so one
 * fetch serves the list and a change made anywhere (nav selector included)
 * reaches every route in the same session, no reload.
 */
export function HouseholdProvider({ children }: { children: ReactNode }) {
  const { data: households, isError, error } = useHouseholds();
  const [householdId, setHouseholdIdState] = useState(() =>
    typeof localStorage !== "undefined" ? localStorage.getItem("household_id") || "" : ""
  );

  // Behavior-preservation rail (every route did this for itself): localStorage
  // first, else the first household, with the fallback auto-persisted.
  useEffect(() => {
    if (!householdId && households?.[0]) {
      setHouseholdIdState(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const setHouseholdId = useCallback((id: string) => {
    setHouseholdIdState(id);
    localStorage.setItem("household_id", id);
  }, []);

  const value = useMemo(
    () => ({ households, isError, error, householdId, setHouseholdId }),
    [households, isError, error, householdId, setHouseholdId]
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
