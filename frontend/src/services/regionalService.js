import api from "./api";

export const regionalService = {
  async getBranches() {
    const response = await api.get("/api/regional/branches");
    return response.data;
  },

  async getLoad() {
    const response = await api.get("/api/regional/load");
    return response.data;
  },

  async getBottlenecks() {
    const response = await api.get("/api/regional/bottlenecks");
    return response.data;
  },

  async getStaffing() {
    const response = await api.get("/api/regional/staffing");
    return response.data;
  }
};

export default regionalService;
