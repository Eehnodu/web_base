// auth.types.ts

/** UI에서 사용하던 입력 타입(그대로 유지 가능) */
export type RegisterReqUI = {
  user_id: string;
  user_name: string;
  user_email: string;
  user_password: string;
};

/** 서버 스키마에 맞춘 실제 전송 바디 */
export type RegisterReqAPI = {
  user_id: string;
  user_name: string;
  user_email: string;
  password: string; // ← 서버는 password를 기대한다고 가정
};

export type LoginReq = {
  user_id: string;
  password: string; // ← LoginIn(user_id, password)에 맞춤
};

export type LoginRes = {
  access_token: string; // ← token_type 제거
};

export type MeRes = {
  id: number;
  user_id: string;
  user_name: string;
  user_email: string;
};

/** 로그아웃 응답(JSON:API attributes) */
export type LogoutRes = {
  detail: string; // "logged out"
};
