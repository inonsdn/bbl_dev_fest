// Central place for backend calls. Point this at your FastAPI server.
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Raised when the backend responds with a non-2xx status so callers can show
// the message returned in FastAPI's `detail` field.
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, { method = "GET", token, body } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new ApiError(data.detail || `Request failed (${res.status})`, res.status);
  }

  return data;
}

export const api = {
  // Returns { token, user_id, username, is_admin }
  login(username, password) {
    return request("/login", { method: "POST", body: { username, password } });
  },
  // Returns [{ appointmentId, user, slot }]
  listAppointments(token) {
    return request("/appointments", { token });
  },
  createAppointment(token, slot) {
    return request("/appointments", { method: "POST", token, body: { slot } });
  },
  updateAppointment(token, appointmentId, slot) {
    return request(`/appointments/${appointmentId}`, {
      method: "PUT",
      token,
      body: { slot },
    });
  },
  deleteAppointment(token, appointmentId) {
    return request(`/appointments/${appointmentId}`, { method: "DELETE", token });
  },
};
