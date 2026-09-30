import api from "./api";

export const dashboardService = {
  async getSummary(branchId) {
    const params = branchId ? { branch_id: branchId } : {};
    const response = await api.get("/api/dashboard/summary", { params });
    return response.data;
  },

  async getBottlenecks(branchId) {
    const params = branchId ? { branch_id: branchId } : {};
    const response = await api.get("/api/dashboard/bottlenecks", { params });
    return response.data;
  },

  async getServiceLoad(branchId) {
    const params = branchId ? { branch_id: branchId } : {};
    const response = await api.get("/api/dashboard/service-load", { params });
    return response.data;
  }
};

export default dashboardService;
