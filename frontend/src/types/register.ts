export interface RegisterRequest {
  user_name: string;
  password: string;
  first_name: string;
  last_name: string;
  middle_name: string;
  phone: string;
  dsh: string;
}

export interface RegisterResponse {
  access_token: string;
  refresh_token: string;
}