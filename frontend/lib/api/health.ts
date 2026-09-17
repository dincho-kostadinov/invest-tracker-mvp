import { apiGet } from "@/lib/api/client";

export interface HealthStatus {
  status: string;
  database: string;
}

export function getHealth(): Promise<HealthStatus> {
  return apiGet<HealthStatus>("/health");
}
