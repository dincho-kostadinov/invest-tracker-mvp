export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly path: string,
    public readonly status: number
  ) {
    super(`[api] ${path} failed with status ${status}`);
  }
}

export async function apiGet<T>(path: string, authHeader?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: authHeader ? { Authorization: authHeader } : undefined,
  });
  if (!response.ok) {
    throw new ApiError(path, response.status);
  }
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new ApiError(path, response.status);
  }
  return response.json() as Promise<T>;
}
