import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import type { Asset, AssetListResponse, Household } from "../api/types";

export function useAssets(
  householdId: string,
  q: string,
  cursor?: string,
  assetType?: string,
  status?: string
) {
  return useQuery<AssetListResponse>({
    queryKey: ["assets", householdId, q, cursor, assetType, status],
    queryFn: () =>
      apiGet<AssetListResponse>("/v1/assets", {
        household_id: householdId,
        q,
        cursor: cursor || "",
        limit: "20",
        ...(assetType ? { asset_type: assetType } : {}),
        ...(status ? { status } : {}),
      }),
    enabled: !!householdId,
  });
}

export function useHouseholds() {
  return useQuery<Household[]>({
    queryKey: ["households"],
    queryFn: () => apiGet<Household[]>("/v1/households"),
  });
}

export function useAsset(householdId: string, assetId: string) {
  return useQuery<Asset>({
    queryKey: ["asset", assetId, householdId],
    queryFn: () => apiGet<Asset>(`/v1/assets/${assetId}`, { household_id: householdId }),
    enabled: !!assetId && !!householdId,
  });
}
