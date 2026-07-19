import React, { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const email = localStorage.getItem("email");
    const role = localStorage.getItem("role");
    return email ? { email, role } : null;
  });

  const login = (email, role, token) => {
    localStorage.setItem("email", email);
    localStorage.setItem("role", role);
    localStorage.setItem("token", token);
    setUser({ email, role });
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
