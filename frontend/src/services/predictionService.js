import api from "./api";

export const predictionService = {
  async predictFootfall(payload) {
    // payload: { branch_id, date, start_time, end_time }
    const response = await api.post("/api/predictions/footfall", payload);
    return response.data;
  },

  async predictWaitTime(payload) {
    // payload: { branch_id, service_category, queue_length, staff_available, recent_arrivals }
    const response = await api.post("/api/predictions/wait-time", payload);
    return response.data;
  },

  async predictStaffRequirement(payload) {
    // payload: { branch_id, date, start_time, end_time, expected_customers, service_category }
    const response = await api.post("/api/predictions/staff-requirement", payload);
    return response.data;
  }
};

export default predictionService;
