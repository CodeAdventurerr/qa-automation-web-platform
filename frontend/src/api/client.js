import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const apiKey = import.meta.env.VITE_QA_PLATFORM_API_KEY;
  if (apiKey) {
    config.headers["X-API-Key"] = apiKey;
  }
  return config;
});

export async function generateTests(payload) {
  const { data } = await api.post("/generate-tests", payload);
  return data;
}

export async function runTests(projectId, options = {}) {
  const { data } = await api.post("/run-tests", {
    project_id: projectId,
    headless: true,
    demo_mode: true,
    ...options,
  });
  return data;
}

export async function downloadReport(projectId) {
  const response = await api.get(`/reports/${projectId}/download`, {
    responseType: "blob",
  });
  const href = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = href;
  link.download = `${projectId}-report.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(href);
}
