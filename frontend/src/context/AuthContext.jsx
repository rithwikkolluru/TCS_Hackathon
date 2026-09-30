import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { authService } from "../services/authService";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem("bank_user");
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (e) {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem("bank_auth_token") || null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Validate active session on mount
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem("bank_auth_token");
      if (savedToken) {
        try {
          const profileRes = await authService.getProfile();
          if (profileRes?.data) {
            setUser(profileRes.data);
            localStorage.setItem("bank_user", JSON.stringify(profileRes.data));
          }
        } catch (err) {
          console.warn("[Auth] Session validation failed, clearing token", err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const response = await authService.login(email, password);
      if (response && response.success && response.data) {
        const { access_token, user: userData } = response.data;
        
        localStorage.setItem("bank_auth_token", access_token);
        localStorage.setItem("bank_user", JSON.stringify(userData));
        
        setToken(access_token);
        setUser(userData);
        setLoading(false);

        // Role-based redirect
        if (userData.role === "manager") {
          navigate("/manager", { replace: true });
        } else if (userData.role === "employee") {
          navigate("/employee", { replace: true });
        } else if (userData.role === "regional_ops") {
          navigate("/regional", { replace: true });
        } else {
          navigate("/", { replace: true });
        }

        return { success: true, user: userData };
      } else {
        const msg = response?.explanation || "Login failed. Please check credentials.";
        setAuthError(msg);
        setLoading(false);
        return { success: false, error: msg };
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.error?.message || "Invalid email or password credentials.";
      setAuthError(msg);
      setLoading(false);
      return { success: false, error: msg };
    }
  };

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem("bank_auth_token");
      localStorage.removeItem("bank_user");
      setToken(null);
      setUser(null);
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const getCurrentUser = () => user;
  const isAuthenticated = () => !!token && !!user;

  const value = {
    user,
    role: user?.role || null,
    branchId: user?.branch_id || (user?.role === "manager" ? "BR001" : null),
    token,
    loading,
    authError,
    setAuthError,
    login,
    logout,
    getCurrentUser,
    isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
