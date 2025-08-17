import { apiFetch } from "@/api/client";
import type { RegisterRequest, RegisterResponse } from "@/types/register";


export const AuthApi = {
  register(payload: RegisterRequest) {
    return apiFetch<RegisterResponse>("users/register", {
      method: "POST",
      json: payload,
    });
  },
};
