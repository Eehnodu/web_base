// hooks.ts
import { baseurl } from "@/common/hooks/useAPI";
import { api, tokenStore } from "@/common/hooks/authClient";
import { toCompatError } from "@/types/api_type";
import type {
  RegisterReqUI,
  LoginReq,
  LoginRes,
  MeRes,
} from "@/types/auth_type";

const API = "/api";

/** 회원가입 (쿠키 불필요하면 api.bearer.post로 바꿔도 OK) */
export function useRegister() {
  const { request, result, loading } = api.cookie.post<RegisterReqUI, void>();
  const register = (body: RegisterReqUI) =>
    request(`${API}/user/register`, body);
  return { register, response: result, error: toCompatError(result), loading };
}

/** 로그인 (쿠키 필요, access_token 저장) */
export function useLogin() {
  const { request, result, loading } = api.cookie.post<LoginReq, LoginRes>();
  const login = async (body: LoginReq) => {
    const res = await request(`${API}/auth/login`, body);
    if (res.ok) tokenStore.set(res.data.access_token); // 최초 로그인 토큰 저장
    return res;
  };
  return { login, response: result, error: toCompatError(result), loading };
}

/** 내 정보 조회
 *  - 자동 refresh 켜고 싶으면 authed.get
 *  - 굳이 자동 refresh 원치 않으면 bearer.get으로 교체
 */
export function useMe() {
  const { request, result, loading } = api.authed.get<MeRes>();
  const fetchMe = () => request(`${API}/user/me`);
  return { fetchMe, response: result, error: toCompatError(result), loading };
}

/** 로그아웃 (쿠키 필요) */
export function useLogout() {
  const logout = async () => {
    try {
      await fetch(`${baseurl}${API}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: { Accept: "application/vnd.api+json" },
      });
    } finally {
      tokenStore.clear();
    }
  };
  return { logout };
}
