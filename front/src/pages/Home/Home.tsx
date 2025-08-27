import React, { useState } from "react";
import { useRegister, useLogin, useMe, useLogout } from "./hooks";
import type {
  RegisterReqUI,
  LoginReq,
  LoginRes,
  MeRes,
  LogoutRes,
} from "@/types/auth_type";

const Home: React.FC = () => {
  const [tab, setTab] = useState<"login" | "register">("login");

  const [registerForm, setRegisterForm] = useState<RegisterReqUI>({
    user_id: "",
    user_name: "",
    user_email: "",
    user_password: "",
  });
  const [loginForm, setLoginForm] = useState<LoginReq>({
    user_id: "",
    password: "",
  });

  const {
    register,
    response: regRes,
    error: regErr,
    loading: regLoading,
  } = useRegister();
  const {
    login,
    response: loginRes,
    error: loginErr,
    loading: loginLoading,
  } = useLogin();
  const {
    fetchMe,
    response: meRes,
    error: meErr,
    loading: meLoading,
  } = useMe();
  const { logout } = useLogout();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok =
      registerForm.user_id &&
      registerForm.user_name &&
      registerForm.user_email &&
      registerForm.user_password;
    if (!ok) return;

    const res = await register(registerForm);
    if (res.ok) setTab("login"); // ← ApiResult 방식에 맞춰 ok로 체크
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginForm.user_id || !loginForm.password) return;
    await login(loginForm);
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 p-4">
      <div className="w-full max-w-md">
        {/* 카드 */}
        {/* ...탭/폼 UI는 그대로 */}

        {/* 하단: 내 정보/로그아웃 테스트 */}
        <div className="bg-white/70 rounded-xl shadow border border-gray-100 mt-4 p-4">
          <div className="flex gap-2">
            <button
              onClick={fetchMe}
              disabled={meLoading}
              className="flex-1 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
            >
              {meLoading ? "조회 중..." : "내 정보"}
            </button>
            <button
              onClick={logout}
              className="flex-1 py-2 rounded-lg bg-gray-100 hover:bg-gray-200"
            >
              로그아웃
            </button>
          </div>

          {/* ✅ ApiResult 형태에 맞춰 안전 체크 */}
          {meRes?.ok && meRes.data && (
            <div className="mt-3 text-sm text-gray-700 bg-gray-50 border rounded-lg p-3 text-left">
              <div>id: {meRes.data.id}</div>
              <div>user_id: {meRes.data.user_id}</div>
              <div>user_name: {meRes.data.user_name}</div>
              <div>user_email: {meRes.data.user_email}</div>
            </div>
          )}

          {/* 에러 메시지 (호환용) */}
          {meErr && (
            <p className="mt-2 text-sm text-red-600">
              {meErr.status} · {meErr.message}
            </p>
          )}
        </div>

        <div className="text-center mt-4 text-xs text-gray-400">
          © Base Project
        </div>
      </div>
    </div>
  );
};

export default Home;
