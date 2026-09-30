import api from "./api";

export const feedbackService = {
  async getSummary(branchId) {
    const params = branchId ? { branch_id: branchId } : {};
    const response = await api.get("/api/feedback/summary", { params });
    return response.data;
  },

  async trackOutcome(payload) {
    // payload: { recommendation_id, action, actual_wait_after_action, actual_queue_after_action, reason }
    const response = await api.post("/api/feedback/recommendation-outcome", payload);
    return response.data;
  },

  async analyzeComment(comment, rating = 3) {
    const response = await api.post("/api/feedback/analyze-comment", null, {
      params: { comment, rating }
    });
    return response.data;
  }
};

export default feedbackService;
