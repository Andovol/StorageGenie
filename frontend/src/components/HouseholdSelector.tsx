import type { CSSProperties } from "react";
import type { Household } from "../api/types";

export interface HouseholdSelectorProps {
  value: string;
  onChange: (value: string) => void;
  households?: Household[];
  showLabel?: boolean;
  labelStyle?: CSSProperties;
  selectStyle?: CSSProperties;
  emptyOptionLabel?: string;
  id?: string;
}

export function HouseholdSelector({
  value,
  onChange,
  households,
  showLabel = true,
  labelStyle,
  selectStyle,
  emptyOptionLabel = "Select household",
  id,
}: HouseholdSelectorProps) {
  const selectElement = (
    <select
      id={id}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      style={selectStyle}
    >
      {emptyOptionLabel ? <option value="">{emptyOptionLabel}</option> : null}
      {households?.map((household) => (
        <option key={household.id} value={household.id}>
          {household.name}
        </option>
      ))}
    </select>
  );

  if (!showLabel) {
    return selectElement;
  }

  return (
    <label style={labelStyle}>
      Household {selectElement}
    </label>
  );
}
