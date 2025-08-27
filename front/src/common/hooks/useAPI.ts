// useAPI.ts
import { useState, useCallback, useRef } from "react";
import {
  JSONAPI,
  PROBLEM,
  ProblemDetails,
  ApiResult,
  HttpMethod,
  UseAPIConfig,
  JsonApiSingleDoc,
} from "@/types/api_type";

// =======================
//  기본 서버 주소 정의
// =======================
export const baseurl =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000" // 개발 환경(local)
    : "https://your-production-domain.com"; // 배포 환경(prod)

/** ===== Utils ===== */

/** JSON 문자열을 안전하게 파싱 (실패시 null) */
function safeJson<T = any>(text: string | null): T | null {
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

/** 서버 응답이 RFC7807 Problem Details 타입인지 확인 */
function isProblemResponse(ct?: string | null) {
  return !!ct && ct.includes(PROBLEM);
}

/** 서버 응답이 JSON:API 타입인지 확인 */
function isJsonApiResponse(ct?: string | null) {
  return !!ct && ct.includes(JSONAPI);
}

/**
 * JSON:API 문서에서 attributes 추출
 * - single_doc: attributes → T
 * - list_doc:   attributes[] → T (T는 배열 타입이어야)
 */
function unwrapJsonApi<T>(doc: JsonApiSingleDoc<T>): T {
  const d: any = doc?.data;
  if (Array.isArray(d)) {
    return d.map((r: any) => r?.attributes) as unknown as T;
  }
  return d?.attributes as T;
}

// =========================================================
// 공통 fetch 함수 (401 자동 리프레시, JSON:API/RFC7807 처리)
// =========================================================
async function coreRequest<T>(
  method: HttpMethod,
  url: string,
  body: any | undefined,
  cfg: Required<UseAPIConfig>,
  retrying = false
): Promise<ApiResult<T>> {
  // 기본 헤더 설정
  const headers: Record<string, string> = {
    Accept: `${JSONAPI}, ${PROBLEM}`, // 서버에 JSON:API, ProblemDetails 응답을 기대한다고 알림
    ...(method !== "GET" ? { "Content-Type": JSONAPI } : {}), // GET 외에는 Content-Type 지정
  };

  // 액세스 토큰이 있으면 Authorization 헤더에 추가
  const token = cfg.getAccessToken?.();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    // 실제 fetch 요청
    res = await fetch(`${cfg.base}${url}`, {
      method,
      credentials: cfg.withCredentials ? "include" : "same-origin", // refresh 쿠키 사용 여부
      headers,
      ...(method !== "GET" ? { body: JSON.stringify(body ?? {}) } : {}),
    });
  } catch (e: any) {
    // 네트워크 에러 (서버에 도달조차 못한 경우)
    return {
      ok: false,
      status: null,
      problem: {
        title: "Network error",
        detail: e?.message ?? "Network error",
      },
    };
  }

  // 응답 파싱
  const ct = res.headers.get("content-type"); // Content-Type 확인
  const rawText = await res.text().catch(() => null); // 원문 텍스트
  const json = safeJson<any>(rawText); // JSON 파싱 시도

  // ---------------------------------------------------------
  // 401 Unauthorized 처리 (refresh 토큰으로 1번만 재시도)
  // ---------------------------------------------------------
  if (res.status === 401 && cfg.withCredentials && !retrying) {
    const refreshed = await tryRefresh(cfg);
    if (refreshed) {
      // refresh 성공 → 원 요청 재시도
      return coreRequest<T>(method, url, body, cfg, true);
    }
    // refresh 실패 → onUnauthorized 콜백 실행 (로그아웃 처리 등)
    cfg.onUnauthorized?.();
    return {
      ok: false,
      status: 401,
      problem:
        json && isProblemResponse(ct)
          ? (json as ProblemDetails)
          : { title: "Unauthorized", status: 401 },
      raw: json ?? rawText,
    };
  }

  // ---------------------------------------------------------
  // 에러 응답 (RFC7807 ProblemDetails 표준화)
  // ---------------------------------------------------------
  if (!res.ok) {
    const problem: ProblemDetails =
      isProblemResponse(ct) && json
        ? json
        : {
            title: "HTTP Error",
            status: res.status,
            detail:
              typeof json === "string" ? json : JSON.stringify(json ?? rawText),
          };
    return { ok: false, status: res.status, problem, raw: json ?? rawText };
  }

  // ---------------------------------------------------------
  // 성공 응답
  // ---------------------------------------------------------

  // 204 No Content
  if (res.status === 204) {
    return { ok: true, status: res.status, data: undefined as T, raw: null };
  }

  // JSON:API → attributes / attributes[]로 변환
  if (isJsonApiResponse(ct) && json) {
    return {
      ok: true,
      status: res.status,
      data: unwrapJsonApi<T>(json),
      raw: json,
    };
  }

  // 그 외 (본문이 비었거나 JSON:API 아님 → 유연하게 처리)
  return {
    ok: true,
    status: res.status,
    data: (json ?? (rawText as any)) as T,
    raw: json ?? rawText,
  };
}

// =========================================================
// refresh 토큰으로 액세스 토큰 재발급 시도
// (쿠키 기반, /api/auth/refresh 엔드포인트 호출)
// - 새 access_token이 오면 setAccessToken으로 저장
// =========================================================
async function tryRefresh(cfg: Required<UseAPIConfig>): Promise<boolean> {
  try {
    const res = await fetch(`${cfg.base}/api/auth/refresh`, {
      method: "POST",
      credentials: "include", // 쿠키 포함
      headers: { Accept: `${JSONAPI}, ${PROBLEM}` },
    });
    if (!res.ok) return false;

    // 새 토큰 파싱 & 저장
    const ct = res.headers.get("content-type");
    const raw = await res.text().catch(() => null);
    const json = raw ? safeJson<any>(raw) : null;

    if (ct?.includes(JSONAPI) && json) {
      const d = json?.data;
      const token = Array.isArray(d)
        ? null
        : (d?.attributes?.access_token as string | undefined);
      if (token && cfg.setAccessToken) {
        cfg.setAccessToken(token); // 새 토큰 저장
      }
    }
    return true;
  } catch {
    return false;
  }
}

// =========================================================
// React Hook 인터페이스
// =========================================================

/**
 * 공통 useAPI 훅
 * - method: GET/POST/PUT/PATCH/DELETE
 * - config: withCredentials, base, getAccessToken, setAccessToken, onUnauthorized
 */
export function useAPI<TReq = unknown, TRes = unknown>(
  method: HttpMethod,
  config?: UseAPIConfig
) {
  const [result, setResult] = useState<ApiResult<TRes> | null>(null); // 응답 상태
  const [loading, setLoading] = useState(false); // 로딩 상태

  // config를 ref에 보관 (매 렌더링마다 최신화)
  const cfgRef = useRef<Required<UseAPIConfig>>({
    withCredentials: !!config?.withCredentials,
    base: config?.base ?? baseurl,
    getAccessToken: config?.getAccessToken ?? (() => null),
    setAccessToken: config?.setAccessToken ?? (() => {}),
    onUnauthorized: config?.onUnauthorized ?? (() => {}),
  });
  cfgRef.current = {
    withCredentials: !!config?.withCredentials,
    base: config?.base ?? baseurl,
    getAccessToken: config?.getAccessToken ?? (() => null),
    setAccessToken: config?.setAccessToken ?? (() => {}),
    onUnauthorized: config?.onUnauthorized ?? (() => {}),
  };

  /**
   * 실제 요청 실행 함수
   * - url: 요청 경로
   * - body: 요청 바디 (GET 제외)
   */
  const request = useCallback(
    async (url: string, body?: TReq) => {
      setLoading(true);
      try {
        const r = await coreRequest<TRes>(method, url, body, cfgRef.current);
        setResult(r);
        return r;
      } finally {
        setLoading(false);
      }
    },
    [method]
  );

  return { request, result, loading };
}

// =========================================================
// 전용 시그니처 래퍼 (GET, POST 전용 훅)
// =========================================================

/** GET 전용 훅 (body 없음) */
export function useGet<TRes = unknown>(config?: UseAPIConfig) {
  const { request, result, loading } = useAPI<void, TRes>("GET", config);
  const get = useCallback((url: string) => request(url, undefined), [request]);
  return { request: get, result, loading };
}

/** POST 전용 훅 (body/response 제네릭 지정 가능) */
export function usePost<TReq = unknown, TRes = unknown>(config?: UseAPIConfig) {
  return useAPI<TReq, TRes>("POST", config);
}
