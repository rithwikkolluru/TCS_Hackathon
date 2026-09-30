import api from "./api";

export const liveService = {
  async ingestEvent(eventData) {
    const response = await api.post("/api/live/events", eventData);
    return response.data;
  },

  async getRecentEvents(branchId, limit = 20) {
    const params = { limit };
    if (branchId) params.branch_id = branchId;
    const response = await api.get("/api/live/events", { params });
    return response.data;
  },

  async simulateSurge(branchId, serviceCategory) {
    const params = {};
    if (branchId) params.branch_id = branchId;
    if (serviceCategory) params.service_category = serviceCategory;
    const response = await api.post("/api/live/simulate-surge", null, { params });
    return response.data;
  }
};

export default liveService;
