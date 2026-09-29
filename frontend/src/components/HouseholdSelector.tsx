import type { CSSProperties } from "react";
import type { Household } from "../api/types";

export interface HouseholdSelectorProps {
  value: string;
  onChange: (value: string) => void;
  households?: Household[];
  showLabel?: boolean;
  labelStyle?: CSSProperties;
  selectStyle?: CSSProperties;
  selectClassName?: string;
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
  selectClassName,
  emptyOptionLabel = "Select household",
  id,
}: HouseholdSelectorProps) {
  const selectElement = (
    <select
      id={id}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      style={selectStyle}
      className={selectClassName}
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
