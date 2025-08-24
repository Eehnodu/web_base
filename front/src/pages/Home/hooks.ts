import { usePost, useGet, baseurl } from "@/common/hooks/useAPI";
import type { RegisterReq, LoginReq, LoginRes, MeRes } from "@/types/auth";

const API = "/api";

const tokenStore = {
  get: () => localStorage.getItem("access_token"),
  set: (t: string) => localStorage.setItem("access_token", t),
  clear: () => localStorage.removeItem("access_token"),
};

/** 회원가입 (쿠키 필요 없으면 기본값) */
export function useRegister() {
  const { request, response, error, loading } = usePost<RegisterReq, void>();
  const register = (body: RegisterReq) => request(`${API}/user/register`, body);
  return { register, response, error, loading };
}

/** 로그인 (세션 쿠키 필요 시 withCredentials 켜기) */
export function useLogin() {
  const { request, response, error, loading } = usePost<LoginReq, LoginRes>({
    withCredentials: true,
  });
  const login = async (body: LoginReq) => {
    const res = await request(`${API}/auth/login`, body);
    const token = res.data?.access_token;
    if (token) tokenStore.set(token);
    return res;
  };
  return { login, response, error, loading };
}

/** 내 정보 조회 (Bearer 토큰 쓰면 credentials 불필요) */
export function useMe() {
  const { request, response, error, loading } = useGet<MeRes>();
  const fetchMe = () =>
    request(`${API}/user/me`, {
      headers: (() => {
        const t = tokenStore.get();
        return t ? { Authorization: `Bearer ${t}` } : {};
      })(),
    });
  return { fetchMe, response, error, loading };
}

/** 로그아웃 (쿠키 세션 끊을 거면 include 필요) */
export function useLogout() {
  const logout = async () => {
    try {
      await fetch(`${baseurl}${API}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } finally {
      tokenStore.clear();
    }
  };
  return { logout };
}
