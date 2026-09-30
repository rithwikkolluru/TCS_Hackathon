import api from "./api";

export const branchService = {
  async getAllBranches() {
    const response = await api.get("/api/branches");
    return response.data;
  },

  async getBranch(branchCode) {
    const response = await api.get(`/api/branches/${branchCode}`);
    return response.data;
  },

  async getBranchStaff(branchCode) {
    const response = await api.get(`/api/branches/${branchCode}/staff`);
    return response.data;
  }
};

export default branchService;
