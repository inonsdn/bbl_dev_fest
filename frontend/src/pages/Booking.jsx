import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Booking() {
  const { auth, logout } = useAuth();
  const { token, username, isAdmin } = auth;

  const [appointments, setAppointments] = useState([]);
  const [slot, setSlot] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editingSlot, setEditingSlot] = useState("");

  // A 401 means the token is gone or expired — drop the session.
  const handleError = useCallback(
    (err) => {
      if (err instanceof ApiError && err.status === 401) {
        logout();
        return;
      }
      setError(err.message);
    },
    [logout]
  );

  const loadAppointments = useCallback(async () => {
    setError("");
    try {
      const data = await api.listAppointments(token);
      setAppointments(data);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [token, handleError]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    const value = slot.trim();
    if (!value) return;
    try {
      await api.createAppointment(token, value);
      setSlot("");
      await loadAppointments();
    } catch (err) {
      handleError(err);
    }
  }

  function startEdit(appt) {
    setEditingId(appt.appointmentId);
    setEditingSlot(appt.slot);
  }

  function cancelEdit() {
    setEditingId(null);
    setEditingSlot("");
  }

  async function saveEdit(appointmentId) {
    const value = editingSlot.trim();
    if (!value) return;
    try {
      await api.updateAppointment(token, appointmentId, value);
      cancelEdit();
      await loadAppointments();
    } catch (err) {
      handleError(err);
    }
  }

  async function handleDelete(appointmentId) {
    if (!window.confirm("Delete this booking?")) return;
    try {
      await api.deleteAppointment(token, appointmentId);
      await loadAppointments();
    } catch (err) {
      handleError(err);
    }
  }

  return (
    <div className="card booking-card">
      <header className="booking-header">
        <div>
          <h1>Book an Appointment</h1>
          <p className="subtitle">
            Signed in as <strong>{username}</strong>
            <span className={`badge ${isAdmin ? "badge-admin" : ""}`}>
              {isAdmin ? "admin" : "user"}
            </span>
          </p>
        </div>
        <button className="secondary" onClick={logout}>
          Log Out
        </button>
      </header>

      <form className="slot-form" onSubmit={handleCreate}>
        <input
          value={slot}
          onChange={(e) => setSlot(e.target.value)}
          placeholder="e.g. 10am-11am"
          aria-label="Time slot"
        />
        <button type="submit">Book Slot</button>
      </form>

      {error && <p className="error">{error}</p>}

      <h2>{isAdmin ? "All Bookings" : "My Bookings"}</h2>

      {loading ? (
        <p className="muted">Loading…</p>
      ) : appointments.length === 0 ? (
        <p className="muted">No bookings yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Owner</th>
              <th>Slot</th>
              <th className="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((appt) => {
              const isEditing = editingId === appt.appointmentId;
              return (
                <tr key={appt.appointmentId}>
                  <td>{appt.user}</td>
                  <td>
                    {isEditing ? (
                      <input
                        value={editingSlot}
                        onChange={(e) => setEditingSlot(e.target.value)}
                        aria-label="Edit time slot"
                      />
                    ) : (
                      appt.slot
                    )}
                  </td>
                  <td className="actions-col">
                    {isEditing ? (
                      <>
                        <button
                          className="row-btn"
                          onClick={() => saveEdit(appt.appointmentId)}
                        >
                          Save
                        </button>
                        <button className="row-btn secondary" onClick={cancelEdit}>
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button className="row-btn" onClick={() => startEdit(appt)}>
                          Edit
                        </button>
                        <button
                          className="row-btn danger"
                          onClick={() => handleDelete(appt.appointmentId)}
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
