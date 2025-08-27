// api_types.ts
export const JSONAPI = "application/vnd.api+json" as const;
export const PROBLEM = "application/problem+json" as const;

export type ProblemDetails = {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  [k: string]: any;
};

/**
 * JSON:API 문서
 * - 단일(single_doc)과 리스트(list_doc)를 모두 포용
 * - attributes를 소비 쪽에서 그대로 쓰기 쉽게 하기 위해 제네릭 T로 받음
 *   (단, list_doc의 경우 T는 배열 타입이어야 함: 예) T = UserAttr[])
 */
export type JsonApiSingleDoc<T> = {
  data:
    | { type: string; id: string | number; attributes: any }
    | Array<{ type: string; id: string | number; attributes: any }>;
  links?: {
    self?: { href: string };
    next?: { href: string };
    prev?: { href: string };
  };
  meta?: { total?: number; page?: number; size?: number };
};

/** Discriminated Union (ok 기준으로 엄격 분리) */
export type ApiResult<T> =
  | { ok: true; status: number; data: T; raw?: any; problem?: never }
  | {
      ok: false;
      status: number | null;
      problem: ProblemDetails | null;
      raw?: any;
      data?: never;
    };

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

/**
 * 공통 훅/클라이언트 설정
 * - getAccessToken: Authorization 헤더에 넣을 액세스 토큰 조회
 * - setAccessToken: /auth/refresh 응답(access_token) 저장 시 사용 (선택)
 * - onUnauthorized: refresh 실패 시 후처리(로그아웃 등)
 */
export type UseAPIConfig = {
  withCredentials?: boolean;
  base?: string;
  getAccessToken?: () => string | null;
  setAccessToken?: (token: string | null) => void;
  onUnauthorized?: () => void;
};

/** 타입 가드: 실패인지 판별 */
export function isFail<T>(
  r: ApiResult<T> | null
): r is Extract<ApiResult<T>, { ok: false }> {
  return !!r && r.ok === false;
}

/** 타입 가드: 성공인지 판별 */
export function isOk<T>(
  r: ApiResult<T> | null
): r is Extract<ApiResult<T>, { ok: true }> {
  return !!r && r.ok === true;
}

/** 공용 에러 변환 유틸: 호환형 {status, message} 리턴 */
export function toCompatError<T>(r: ApiResult<T> | null) {
  if (!isFail(r)) return null;
  return {
    status: r.status,
    message: r.problem?.detail ?? r.problem?.title ?? "Request failed",
  };
}
