import React, { useState } from "react";
import { useRegister, useLogin, useMe, useLogout } from "./hooks";
import type { RegisterReq, LoginReq } from "@/types/auth";

const Home: React.FC = () => {
  const [tab, setTab] = useState<"login" | "register">("login");

  // 폼 상태(컴포넌트 로컬)
  const [registerForm, setRegisterForm] = useState<RegisterReq>({
    user_id: "",
    user_name: "",
    user_email: "",
    user_password: "",
  });
  const [loginForm, setLoginForm] = useState<LoginReq>({
    user_id: "",
    user_password: "",
  });

  // 액션 훅
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

  // 핸들러
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok =
      registerForm.user_id &&
      registerForm.user_name &&
      registerForm.user_email &&
      registerForm.user_password;
    if (!ok) return;

    const res = await register(registerForm);
    if (res.status && res.status >= 200 && res.status < 300) setTab("login");
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginForm.user_id || !loginForm.user_password) return;
    await login(loginForm);
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 p-4">
      <div className="w-full max-w-md">
        {/* 카드 */}
        <div className="bg-white/90 backdrop-blur rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
          {/* 헤더 */}
          <div className="px-6 pt-6 text-center">
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Welcome
            </h1>
          </div>

          {/* 탭 */}
          <div className="px-3 mt-6">
            <div className="grid grid-cols-2 gap-1 p-1 bg-gray-100 rounded-xl">
              <button
                type="button"
                className={`py-2 rounded-lg text-sm font-semibold transition ${
                  tab === "login"
                    ? "bg-white shadow text-gray-900"
                    : "text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => setTab("login")}
              >
                로그인
              </button>
              <button
                type="button"
                className={`py-2 rounded-lg text-sm font-semibold transition ${
                  tab === "register"
                    ? "bg-white shadow text-gray-900"
                    : "text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => setTab("register")}
              >
                회원가입
              </button>
            </div>
          </div>

          {/* 컨텐츠 */}
          <div className="px-6 pb-6 pt-4">
            {tab === "login" ? (
              <form className="space-y-4" onSubmit={handleLogin}>
                <div className="text-left">
                  <label
                    htmlFor="login-id"
                    className="block text-sm font-medium text-gray-700"
                  >
                    아이디
                  </label>
                  <input
                    id="login-id"
                    type="text"
                    placeholder="user_id"
                    value={loginForm.user_id}
                    onChange={(e) =>
                      setLoginForm((s) => ({ ...s, user_id: e.target.value }))
                    }
                    className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="text-left">
                  <label
                    htmlFor="login-pw"
                    className="block text-sm font-medium text-gray-700"
                  >
                    비밀번호
                  </label>
                  <input
                    id="login-pw"
                    type="password"
                    placeholder="••••••••"
                    value={loginForm.user_password}
                    onChange={(e) =>
                      setLoginForm((s) => ({
                        ...s,
                        user_password: e.target.value,
                      }))
                    }
                    className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loginLoading}
                  className="w-full rounded-xl bg-blue-600 text-white font-semibold py-2.5 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
                >
                  {loginLoading ? "로그인 중..." : "로그인"}
                </button>

                {loginErr && (
                  <p className="text-center text-sm text-red-600">
                    {loginErr.status} · {loginErr.message}
                  </p>
                )}

                <p className="text-center text-xs text-gray-400">
                  계정이 없으신가요?{" "}
                  <button
                    type="button"
                    className="text-blue-600 hover:text-blue-700 font-semibold"
                    onClick={() => setTab("register")}
                  >
                    회원가입
                  </button>
                </p>
              </form>
            ) : (
              <form className="space-y-4" onSubmit={handleRegister}>
                <div className="grid grid-cols-1 gap-4">
                  <div className="text-left">
                    <label
                      htmlFor="reg-id"
                      className="block text-sm font-medium text-gray-700"
                    >
                      아이디
                    </label>
                    <input
                      id="reg-id"
                      type="text"
                      placeholder="user_id"
                      value={registerForm.user_id}
                      onChange={(e) =>
                        setRegisterForm((s) => ({
                          ...s,
                          user_id: e.target.value,
                        }))
                      }
                      className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div className="text-left">
                    <label
                      htmlFor="reg-name"
                      className="block text-sm font-medium text-gray-700"
                    >
                      이름
                    </label>
                    <input
                      id="reg-name"
                      type="text"
                      placeholder="홍길동"
                      value={registerForm.user_name}
                      onChange={(e) =>
                        setRegisterForm((s) => ({
                          ...s,
                          user_name: e.target.value,
                        }))
                      }
                      className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div className="text-left">
                    <label
                      htmlFor="reg-email"
                      className="block text-sm font-medium text-gray-700"
                    >
                      이메일
                    </label>
                    <input
                      id="reg-email"
                      type="email"
                      placeholder="name@example.com"
                      value={registerForm.user_email}
                      onChange={(e) =>
                        setRegisterForm((s) => ({
                          ...s,
                          user_email: e.target.value,
                        }))
                      }
                      className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div className="text-left">
                    <label
                      htmlFor="reg-pw"
                      className="block text-sm font-medium text-gray-700"
                    >
                      비밀번호
                    </label>
                    <input
                      id="reg-pw"
                      type="password"
                      placeholder="최소 8자, 영문/숫자 조합 권장"
                      value={registerForm.user_password}
                      onChange={(e) =>
                        setRegisterForm((s) => ({
                          ...s,
                          user_password: e.target.value,
                        }))
                      }
                      className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={regLoading}
                  className="w-full rounded-xl bg-blue-600 text-white font-semibold py-2.5 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
                >
                  {regLoading ? "가입 중..." : "회원가입"}
                </button>

                {regErr && (
                  <p className="text-center text-sm text-red-600">
                    {regErr.status} · {regErr.message}
                  </p>
                )}

                <p className="text-center text-xs text-gray-400">
                  이미 계정이 있으신가요?{" "}
                  <button
                    type="button"
                    className="text-blue-600 hover:text-blue-700 font-semibold"
                    onClick={() => setTab("login")}
                  >
                    로그인
                  </button>
                </p>
              </form>
            )}
          </div>
        </div>

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

          {meRes.data && (
            <div className="mt-3 text-sm text-gray-700 bg-gray-50 border rounded-lg p-3 text-left">
              <div>id: {meRes.data.id}</div>
              <div>user_id: {meRes.data.user_id}</div>
              <div>user_name: {meRes.data.user_name}</div>
              <div>user_email: {meRes.data.user_email}</div>
            </div>
          )}
          {meErr && (
            <p className="mt-2 text-sm text-red-600">
              {meErr.status} · {meErr.message}
            </p>
          )}
        </div>

        {/* 푸터 */}
        <div className="text-center mt-4 text-xs text-gray-400">
          © Base Project
        </div>
      </div>
    </div>
  );
};

export default Home;
