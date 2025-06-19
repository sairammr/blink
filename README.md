# Blink: Real-Time Eye Blink Analytics Desktop App

## Overview

**Blink** is a cross-platform desktop application for real-time eye blink detection and analytics. It combines a modern React-based dashboard (via Tauri and Vite) with a robust Python backend leveraging computer vision to track and analyze eye blinks using your webcam. The system is designed for productivity, health monitoring, or research, providing detailed visualizations, statistics, and user-adjustable sensitivity.

---

## Features

- **Real-Time Blink Detection:** Uses your webcam and advanced facial landmark detection to monitor blinks.
- **Analytics Dashboard:** Visualizes blink rate, trends, and recent activity with interactive charts.
- **User Controls:** Start/stop tracking, adjust sensitivity, and save session data from an intuitive UI.
- **Configurable Sensitivity:** Fine-tune blink detection threshold for individual needs.
- **Local Data Storage:** All data is stored locally for privacy (SQLite for blink data, JSON for config).
- **Cross-Platform:** Desktop app powered by Tauri, React, and Vite.

---

## Architecture

### 1. Frontend (`/application`)
- **Tech:** React, Tauri, Vite, TailwindCSS, Recharts, Lucide.
- **UI:** Provides a dashboard with real-time stats, charts, and controls.
- **Communication:** Sends HTTP requests to the backend for tracking control, analytics, and configuration.

### 2. Backend (`/server`)
- **Tech:** Python, Flask, OpenCV, cvzone (FaceMeshModule), SQLite.
- **Detection:** Captures webcam frames, detects blinks using FaceMesh, and logs data.
- **Data Management:** Stores blink events and stats in SQLite; manages sensitivity/configuration via JSON.
- **API:** Exposes endpoints for all frontend operations (start, stop, status, analytics, config, etc).

---

## How It Works

1. **Start the App:** Launch the desktop application.
2. **Begin Tracking:** Start blink detection from the dashboard. The backend activates your webcam and begins processing frames in real time.
3. **Blink Detection:** The backend uses FaceMesh to identify eye landmarks and applies a configurable threshold to detect blinks. Each blink is timestamped and saved.
4. **Analytics & Control:** The frontend fetches statistics (blink rates, averages, trends) and displays them. Users can adjust sensitivity, pause/resume tracking, or save sessions.
5. **Persistence:** Data is stored locally (SQLite for events, JSON for config), ensuring privacy and offline access.

---

## Installation & Setup

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Rust toolchain** (for Tauri)
- **Webcam**

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

---

## Configuration
- **Sensitivity Threshold:**
  - Adjust from the dashboard UI.
  - Value is stored in `server/blink_config.json` and applied in real time.
- **Database:**
  - Blink events are stored in `server/blink_data.db` (SQLite).
- **Session Data:**
  - Saved in the `sessions/` directory as JSON files.

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

---

## Technical Details
- **Blink Detection:** Uses OpenCV for video capture and cvzone's FaceMeshModule for facial landmark detection. Blinks are detected by monitoring the vertical distance between eyelid landmarks, compared against a user-configurable threshold.
- **Data Processing:** Blink events are queued and written to SQLite asynchronously for stability. Statistics are computed on demand for analytics.
- **Config Management:** Sensitivity and other parameters are managed via a JSON config file, updated via API.
- **Frontend-Backend Communication:** All control and data flows use HTTP APIs over `localhost`.

---

## Stability & Robustness
- **Threading:** Backend uses threading and queues to ensure non-blocking video processing and database writes.
- **Persistence:** Data and configuration are safely persisted locally.
- **Validation:** Sensitivity and config updates are validated before being applied.
- **Privacy:** No data leaves your device; all processing and storage are local.

---

## Credits
- Built with [Tauri](https://tauri.app/), [React](https://react.dev/), [Vite](https://vitejs.dev/), [OpenCV](https://opencv.org/), [cvzone](https://www.cvzone.com/), and [Flask](https://flask.palletsprojects.com/).

---

## License
MIT (or specify your license here)
