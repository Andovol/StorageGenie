import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, buildUrl } from "../api/client";
import type {
  Asset,
  AssetListResponse,
  Household,
  ReviewTaskListResponse,
  SavedSearch,
  SavedSearchListResponse,
  SavedSearchQuery,
  TaxonomyResponse,
} from "../api/types";

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

export type AssetFacets = {
  asset_type: Record<string, number>;
  status: Record<string, number>;
  has_evidence: Record<string, number>;
};

export function useFacets(householdId: string, q: string) {
  return useQuery<AssetFacets>({
    queryKey: ["asset-facets", householdId, q],
    queryFn: () =>
      apiGet<AssetFacets>("/v1/assets/facets", {
        household_id: householdId,
        q,
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

/**
 * SG-196 G3: one shared review-task read. The nav badge and InboxPage both use
 * this so they share the ["review-tasks", household] cache entry — no new
 * endpoint, no second fetch shape.
 */
export function useReviewTasks(householdId: string) {
  return useQuery<ReviewTaskListResponse>({
    queryKey: ["review-tasks", householdId],
    queryFn: () =>
      apiGet<ReviewTaskListResponse>("/v1/review-tasks", { household_id: householdId }),
    enabled: !!householdId,
  });
}

/**
 * The served plugin taxonomy (SG-065). Dropdown options come from the backend
 * descriptor, never a hardcoded frontend list. Descriptors are immutable, so
 * the query never needs to revalidate within a session.
 */
export function useTaxonomy() {
  return useQuery<TaxonomyResponse>({
    queryKey: ["taxonomy"],
    queryFn: () => apiGet<TaxonomyResponse>("/v1/taxonomy"),
    staleTime: Infinity,
  });
}

export function useAsset(householdId: string, assetId: string) {
  return useQuery<Asset>({
    queryKey: ["asset", assetId, householdId],
    queryFn: () => apiGet<Asset>(`/v1/assets/${assetId}`, { household_id: householdId }),
    enabled: !!assetId && !!householdId,
  });
}

export function useSavedSearches(householdId: string) {
  return useQuery<SavedSearchListResponse>({
    queryKey: ["saved-searches", householdId],
    queryFn: () =>
      apiGet<SavedSearchListResponse>("/v1/saved-searches", { household_id: householdId }),
    enabled: !!householdId,
  });
}

export function useSaveSearch(householdId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name: string; query: SavedSearchQuery }) =>
      apiPost<SavedSearch>("/v1/saved-searches", payload, { household_id: householdId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-searches", householdId] });
    },
  });
}

export function useDeleteSavedSearch(householdId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    // DELETE has no `apiDelete` helper in `api/client.ts` (outside this
    // slice's scope ceiling), so the request is issued directly here.
    mutationFn: async (id: string): Promise<{ status: string; id: string }> => {
      const response = await fetch(
        buildUrl(`/v1/saved-searches/${encodeURIComponent(id)}`, { household_id: householdId }),
        { method: "DELETE" }
      );
      if (!response.ok) {
        throw new Error(`DELETE /v1/saved-searches failed: ${response.status}`);
      }
      return response.json() as Promise<{ status: string; id: string }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-searches", householdId] });
    },
  });
}
