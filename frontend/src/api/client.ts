const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export function buildUrl(path: string, params: Record<string, string> = {}): string {
  const u = new URL(BASE + path);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
  });
  return u.toString();
}

function parseRfc9457(body: unknown, fallback: string): string {
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    if (typeof b.detail === "string" && b.detail) return b.detail;
    if (typeof b.title === "string" && b.title) {
      const detail = typeof b.detail === "string" ? `: ${b.detail}` : "";
      return `${b.title}${detail}`;
    }
  }
  return fallback;
}

export async function apiGet<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const r = await fetch(buildUrl(path, params));
  if (!r.ok) {
    const body = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(body, `GET ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  params: Record<string, string> = {},
  headers: Record<string, string> = {}
): Promise<T> {
  const r = await fetch(buildUrl(path, params), {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `POST ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiPatch<T>(
  path: string,
  body: unknown,
  params: Record<string, string> = {},
  headers: Record<string, string> = {}
): Promise<T> {
  const r = await fetch(buildUrl(path, params), {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `PATCH ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function uploadEvidence(
  householdId: string,
  file: File
): Promise<{ id: string; sha256: string; storage_key: string; size_bytes: number }> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(buildUrl("/v1/evidence", { household_id: householdId }), {
    method: "POST",
    body: fd,
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `Upload failed: ${r.status}`));
  }
  return r.json();
}
