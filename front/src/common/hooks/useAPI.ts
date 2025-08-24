// useAPI.ts
import { useState, useCallback } from "react";

/** 다른 파일에서도 재사용할 수 있게 export */
export const baseurl =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://your-production-domain.com";

export type ApiResponse<T> = { status: number | null; data: T | null };
export type ApiError = { status: number | null; message: string | null };
type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type UseAPIConfig = {
  /** 쿠키/세션이 필요한 요청에서만 true로 켜세요 */
  withCredentials?: boolean;
  /** 기본값은 위의 baseurl, 필요 시 덮어쓰기 */
  base?: string;
};

function parseJsonSafe<T>(text: string | null): T | null {
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

function stringifyErrorMessage(data: any, fallback = "Request failed") {
  if (!data) return fallback;

  // FastAPI/Pydantic v2: {"detail": [{ type, loc, msg, input, ... }, ... ]}
  if (Array.isArray(data.detail)) {
    const msgs = data.detail
      .map((d) => (typeof d?.msg === "string" ? d.msg : JSON.stringify(d)))
      .join("; ");
    return msgs || fallback;
  }

  if (typeof data.detail === "string") return data.detail;
  if (typeof data.message === "string") return data.message;
  if (typeof data === "object") return JSON.stringify(data);
  return String(data) || fallback;
}

export function useAPI<TReq = unknown, TRes = unknown>(
  method: HttpMethod,
  config?: UseAPIConfig
) {
  const [response, setResponse] = useState<ApiResponse<TRes>>({
    status: null,
    data: null,
  });
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  const withCredentials = !!config?.withCredentials;
  const base = config?.base ?? baseurl;

  const request = useCallback(
    async (
      url: string,
      body?: TReq,
      options?: RequestInit
    ): Promise<ApiResponse<TRes>> => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${base}${url}`, {
          method,
          credentials: withCredentials ? "include" : "same-origin",
          headers: {
            ...(method !== "GET" ? { "Content-Type": "application/json" } : {}),
            ...(options?.headers || {}),
          },
          ...(method !== "GET" ? { body: JSON.stringify(body ?? {}) } : {}),
          ...options,
        });

        // 안전 파싱 (텍스트 → JSON 시도)
        const raw = await res
          .clone()
          .text()
          .catch(() => null);
        const data = parseJsonSafe<TRes>(raw);

        if (!res.ok) {
          const message = stringifyErrorMessage(
            parseJsonSafe<any>(raw),
            `HTTP ${res.status}`
          );
          const err = { status: res.status, message };
          setError(err);
          const resp = { status: res.status, data: null } as ApiResponse<TRes>;
          setResponse(resp);
          return resp;
        }

        const resp = { status: res.status, data } as ApiResponse<TRes>;
        setResponse(resp);
        return resp;
      } catch (e: any) {
        const err = { status: null, message: e?.message || "Network error" };
        setError(err);
        const resp = { status: null, data: null } as ApiResponse<TRes>;
        setResponse(resp);
        return resp;
      } finally {
        setLoading(false);
      }
    },
    [method, withCredentials, base]
  );

  return { request, response, error, loading };
}

/** ✅ GET: body 인자를 아예 받지 않도록 request 시그니처 고정 + withCredentials 전달 */
export function useGet<TRes = unknown>(config?: UseAPIConfig) {
  const baseHook = useAPI<void, TRes>("GET", config);
  const request = useCallback(
    (url: string, options?: RequestInit) =>
      baseHook.request(url, undefined as void, options),
    [baseHook]
  );
  return { ...baseHook, request }; // request(url, options?)만 허용
}

/** ✅ POST: body와 response를 제네릭으로 지정 + withCredentials 전달 */
export function usePost<TReq = unknown, TRes = unknown>(config?: UseAPIConfig) {
  return useAPI<TReq, TRes>("POST", config); // request(url, body, options?)
}
