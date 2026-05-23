import api from "./api";

export async function loginUser(email, password) {
  const response = await api.post("/users/login/", { email, password });
  return response.data;
}

export async function registerUser(name, email, password) {
  const response = await api.post("/users/register/", { name, email, password });
  return response.data;
}
