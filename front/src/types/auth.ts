export type RegisterReq = {
  user_id: string;
  user_name: string;
  user_email: string;
  user_password: string;
};

export type LoginReq = {
  user_id: string;
  user_password: string;
};

export type LoginRes = {
  access_token: string;
  token_type: "bearer";
};

export type MeRes = {
  id: number;
  user_id: string;
  user_name: string;
  user_email: string;
};
