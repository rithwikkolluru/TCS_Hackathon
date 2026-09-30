import api from "./api";

export const authService = {
  async login(email, password) {
    const response = await api.post("/api/auth/login", { email, password });
    return response.data;
  },

  async register(data) {
    const response = await api.post("/api/auth/register", data);
    return response.data;
  },

  async getProfile() {
    const response = await api.get("/api/auth/me");
    return response.data;
  },

  async refresh() {
    const response = await api.post("/api/auth/refresh");
    return response.data;
  },

  async logout() {
    try {
      const response = await api.post("/api/auth/logout");
      return response.data;
    } catch (e) {
      // Clear token even if network fails
      return { success: true };
    }
  }
};

export default authService;
