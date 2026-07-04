# Appointment Booking — React Frontend

A React (Vite) frontend for the FastAPI appointment-booking backend (`main.py`).

## Features

- **Login page** — username/password auth against `POST /login`.
- **Booking page** — book a time slot (free-text string, e.g. `10am-11am`),
  plus inline edit and delete.
- **Authorization** — admins see **all** bookings; regular users see and manage
  **only their own** (enforced by the backend, reflected in the UI).
- Session (token) persisted in `localStorage`; protected routes redirect to login;
  expired/invalid tokens (`401`) log the user out automatically.

## Prerequisites

Run the backend first (from the repo root):

```bash
./setup.sh
./run.sh        # serves FastAPI on http://localhost:8000
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
```

The backend already enables CORS for all origins, so no proxy is needed.

## Demo accounts

| Username | Password   | Role  |
| -------- | ---------- | ----- |
| `admin`  | `admin123` | admin |
| `user`   | `user123`  | user  |

## Configuration

The backend URL defaults to `http://localhost:8000`. Override it with an env var:

```bash
echo "VITE_API_BASE=http://localhost:8000" > .env
```
