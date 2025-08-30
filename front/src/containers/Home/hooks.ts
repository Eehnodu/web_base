// hooks.ts
import { api } from "@/hooks/auth/authClient";
import { toCompatError } from "@/types/api_type";
import type { RegisterReqUI } from "@/types/auth_type";

const API = "/api";

/** 회원가입 (쿠키 불필요하면 api.bearer.post로 바꿔도 OK) */
export function useRegister() {
  const { request, result, loading } = api.cookie.post<RegisterReqUI, void>();
  const register = (body: RegisterReqUI) =>
    request(`${API}/user/register`, body);
  return { register, response: result, error: toCompatError(result), loading };
}
