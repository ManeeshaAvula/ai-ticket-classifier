// Small wrapper around the FastAPI backend.
// Override the base URL with the VITE_API_URL environment variable if the
// API runs somewhere other than http://localhost:8000.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export function classifyTicket(text) {
  return request("/classify", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function fetchTickets(limit = 20) {
  return request(`/tickets?limit=${limit}`);
}

export function fetchStats() {
  return request("/stats");
}
