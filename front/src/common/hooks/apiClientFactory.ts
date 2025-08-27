// apiClientFactory.ts
import { useGet, usePost } from "@/common/hooks/useAPI";
import type { UseAPIConfig } from "@/types/api_type";

/**
 * 공용 API 클라이언트 팩토리
 * - baseConfig에 토큰 전략/에러 핸들링 등을 정의해두면
 *   도메인별로 bearer/authed/cookie 프리셋 훅을 즉시 사용 가능
 */
export function createApiClient(baseConfig: UseAPIConfig) {
  return {
    /** Authorization: Bearer <access_token> 만 사용하는 클라이언트 (쿠키 전송 X) */
    bearer: {
      get: <T>() => useGet<T>({ ...baseConfig, withCredentials: false }),
      post: <TReq, TRes>() =>
        usePost<TReq, TRes>({ ...baseConfig, withCredentials: false }),
    },

    /** Bearer + 401시 자동 refresh 시도 (쿠키 필요) */
    authed: {
      get: <T>() => useGet<T>({ ...baseConfig, withCredentials: true }),
      post: <TReq, TRes>() =>
        usePost<TReq, TRes>({ ...baseConfig, withCredentials: true }),
    },

    /** 쿠키 기반 호출용 (login/refresh/logout 등, Authorization 불필요) */
    cookie: {
      post: <TReq, TRes>() => usePost<TReq, TRes>({ withCredentials: true }),
    },
  };
}
