import axios from "axios";

// In dev, Vite proxies /api -> localhost:8000 (see vite.config.js).
// In production (Vercel), set VITE_API_URL to the deployed backend's base URL, e.g. https://your-app.onrender.com
const client = axios.create({ baseURL: import.meta.env.VITE_API_URL || "/api" });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;
