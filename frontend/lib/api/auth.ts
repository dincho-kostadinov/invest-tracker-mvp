import { apiGet, apiPost } from "@/lib/api/client";

export interface TokenResponse {
  access_token: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
}

export function signup(email: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/signup", { email, password });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/login", { email, password });
}

export function exchangeGoogleCode(code: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/exchange", { code });
}

export function getMe(authHeader: string): Promise<User> {
  return apiGet<User>("/me", authHeader);
}
