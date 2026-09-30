import api from "./api";

export const recommendationService = {
  async getRecommendations(branchId, statusFilter) {
    const params = {};
    if (branchId) params.branch_id = branchId;
    if (statusFilter && statusFilter !== "ALL") params.status_filter = statusFilter;
    const response = await api.get("/api/recommendations", { params });
    return response.data;
  },

  async generateRecommendations(branchId) {
    const response = await api.post("/api/recommendations/generate", {
      branch_id: branchId || null
    });
    return response.data;
  },

  async acceptRecommendation(id, payload = {}) {
    // payload: { reason, actual_wait_after_action, actual_queue_after_action }
    const response = await api.post(`/api/recommendations/${id}/accept`, payload);
    return response.data;
  },

  async rejectRecommendation(id, payload = {}) {
    // payload: { reason, actual_wait_after_action, actual_queue_after_action }
    const response = await api.post(`/api/recommendations/${id}/reject`, payload);
    return response.data;
  },

  async modifyRecommendation(id, payload = {}) {
    const response = await api.post(`/api/recommendations/${id}/modify`, payload);
    return response.data;
  },

  async getDigitalRedirection(serviceCategory, customerType = "Regular") {
    const response = await api.get("/api/recommendations/digital-redirection", {
      params: {
        service_category: serviceCategory,
        customer_type: customerType
      }
    });
    return response.data;
  }
};

export default recommendationService;
