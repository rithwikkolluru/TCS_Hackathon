import api from "./api";

export const auditService = {
  async getAuditLogs(action, limit = 50) {
    const params = { limit };
    if (action) params.action = action;
    const response = await api.get("/api/audit/logs", { params });
    return response.data;
  }
};

export default auditService;
