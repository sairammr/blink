# Blink: Real-Time Eye Blink Analytics Desktop App

## Overview

**Blink** is a cross-platform desktop application for real-time eye blink detection and analytics. It combines a modern React-based dashboard (via Tauri and Vite) with a robust Python backend leveraging computer vision to track and analyze eye blinks using your webcam. The system is designed for productivity, health monitoring, or research, providing detailed visualizations, statistics, and user-adjustable sensitivity.

---

## Features

- **Real-Time Blink Detection:** Uses your webcam and advanced facial landmark detection to monitor blinks.
- **Analytics Dashboard:** Visualizes blink rate, trends, and recent activity with interactive charts.
- **User Controls:** Start/stop tracking, adjust sensitivity, and save session data from an intuitive UI.
- **Configurable Sensitivity:** Fine-tune blink detection threshold for individual needs.
- **MongoDB Data Storage:** Blink data and sensitivity (threshold) are stored in MongoDB, keyed by a unique device ID (e.g. MAC-derived). Optional env `MONGODB_URI` overrides the default URI; if the network fails, threshold falls back to 34.
- **Cross-Platform:** Desktop app powered by Tauri, React, and Vite.

---

## Architecture

### 1. Frontend (`/application`)
- **Tech:** React, Tauri, Vite, TailwindCSS, Recharts, Lucide.
- **UI:** Provides a dashboard with real-time stats, charts, and controls.
- **Communication:** Sends HTTP requests to the backend for tracking control, analytics, and configuration.

### 2. Backend (`/application/blink.py`)
- **Tech:** Python, Flask, OpenCV, cvzone (FaceMeshModule), MongoDB (pymongo).
- **Detection:** Captures webcam frames, detects blinks using FaceMesh, and logs data.
- **Data Management:** Stores blink events and stats in MongoDB per device; sensitivity (threshold) is stored in MongoDB and applied on each restart (fallback 34 if network fails). Mongo URI from env `MONGODB_URI` or hardcoded default.
- **API:** Exposes endpoints for all frontend operations (start, stop, status, analytics, config, device-id, etc.).

---

## How It Works

1. **Start the App:** Launch the desktop application.
2. **Begin Tracking:** Start blink detection from the dashboard. The backend activates your webcam and begins processing frames in real time.
3. **Blink Detection:** The backend uses FaceMesh to identify eye landmarks and applies a configurable threshold to detect blinks. Each blink is timestamped and saved.
4. **Analytics & Control:** The frontend fetches statistics (blink rates, averages, trends) and displays them. Users can adjust sensitivity, pause/resume tracking, or save sessions.
5. **Persistence:** Blink data and sensitivity are stored in MongoDB per device; on each restart the app registers the device (by device ID) and loads threshold from Mongo (fallback 34 if unreachable).

---

## Installation & Setup

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Rust toolchain** (for Tauri)
- **Webcam**


### For LINUX

### 1. Backend Setup
```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python blink.py
```
This will start the Flask server on `localhost:5000`.

### 2. Frontend Setup
```bash
cd application
npm install
npm run tauri dev
```
This will launch the Tauri desktop app.

### For WINDOWS

### 1. Backend Setup
```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python blink.py
```
This will start the Flask server on `localhost:5000`.

### 2. Frontend Setup
```bash
cd application
npm install
npm install @tauri-apps/cli
npm run tauri dev
```
### If needed
```bash
powershell -c "irm bun.sh/install.ps1 | iex"
Invoke-WebRequest https://win.rustup.rs -UseBasicParsing -OutFile rustup-init.exe
.\rustup-init.exe
```

This will launch the Tauri desktop app.

---

## Configuration
- **MongoDB:** Set `MONGODB_URI` in the environment to override the default connection string (default: `mongodb://localhost:27017`). Used for blink data and sensitivity (threshold) per device.
- **Sensitivity (Threshold):** Stored per device in MongoDB and applied on each server restart. If the network or MongoDB is unreachable, threshold **34** is used.
- **Session Data:** Saved in the `sessions/` directory as JSON files.

---

## API Endpoints (Backend)
- `POST /start` – Start blink tracking
- `POST /stop` – Stop blink tracking
- `POST /pause` – Pause tracking
- `POST /resume` – Resume tracking
- `GET /status` – Get current tracker status
- `POST /save` – Save current session
- `POST /config` – Update sensitivity/config
- `GET /blinks` – Get recent blink data
- `GET /api/blink-rate` – Get today's blink rate data
- `GET /api/recent-activity` – Get last 20 minutes activity
- `GET /api/stats` – Get blink statistics
- `GET /api/device-id` – Get current device ID (MongoDB per-device data)
- `POST /test-alert` – To trigger an alert 
- `POST /test-alert` (To trigger a custom alert )
  ```json
  {
    "message": "Your custom test message"
  } 

---

## Technical Details
- **Blink Detection:** Uses OpenCV for video capture and cvzone's FaceMeshModule for facial landmark detection. Blinks are detected by monitoring the vertical distance between eyelid landmarks, compared against a user-configurable threshold.
- **Data Processing:** Blink events are queued and written to MongoDB (per device) asynchronously. Statistics are computed on demand for analytics.
- **Threshold:** Sensitivity is stored in MongoDB per device and loaded on startup; fallback 34 on network failure. Updated via `POST /config`.
- **Frontend-Backend Communication:** All control and data flows use HTTP APIs over `localhost`.

---

## Stability & Robustness
- **Threading:** Backend uses threading and queues to ensure non-blocking video processing and database writes.
- **Persistence:** Data and configuration are safely persisted locally.
- **Validation:** Sensitivity and config updates are validated before being applied.
- **Privacy:** Blink data and threshold are stored in your MongoDB instance (local or Atlas); device is identified by a stable device ID (e.g. MAC-derived).

---

## Credits
- Built with [Tauri](https://tauri.app/), [React](https://react.dev/), [Vite](https://vitejs.dev/), [OpenCV](https://opencv.org/), [cvzone](https://www.cvzone.com/), and [Flask](https://flask.palletsprojects.com/).

---

## License
MIT (or specify your license here)
