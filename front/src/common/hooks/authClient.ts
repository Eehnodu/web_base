// authClient.ts
import { createApiClient } from "@/common/hooks/apiClientFactory";

/** access_token 저장/조회 공용 스토어 */
export const tokenStore = {
  get: () => localStorage.getItem("access_token"),
  set: (t: string | null) => {
    if (!t) return localStorage.removeItem("access_token");
    localStorage.setItem("access_token", t);
  },
  clear: () => localStorage.removeItem("access_token"),
};

/**
 * 인증 공통 설정:
 * - getAccessToken: 매 요청 직전 Authorization에 붙일 토큰
 * - setAccessToken: /auth/refresh 성공 시 새 토큰 저장
 * - onUnauthorized: refresh 실패 시 후처리(로그아웃 등)
 */
export const api = createApiClient({
  getAccessToken: () => tokenStore.get(),
  setAccessToken: (t) => tokenStore.set(t),
  onUnauthorized: () => tokenStore.clear(),
});

/**
 * 사용 예:
 * - api.bearer.get<T>()
 * - api.bearer.post<Req, Res>()
 * - api.authed.get<T>()    // 401 → 자동 refresh
 * - api.authed.post<Req, Res>()
 * - api.cookie.post<Req, Res>() // 로그인/리프레시/로그아웃 등 쿠키 기반
 */
