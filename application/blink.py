import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import threading
import random
import datetime
import json
import os
import sqlite3
from queue import Queue
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import ctypes
import threading
from threading import Thread
from flask import request, jsonify
import logging
import asyncio
import ctypes
import threading

import json
import os

CONFIG_FILE = 'blink_config.json'
DEFAULT_THRESHOLD = 34

class ConfigManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_default_config()
        return self._create_default_config()

    def _create_default_config(self):
        config = {
            'threshold': DEFAULT_THRESHOLD
        }
        self._save_config(config)
        return config

    def _save_config(self, config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    def get_threshold(self):
        return self.config.get('threshold', DEFAULT_THRESHOLD)

    def set_threshold(self, threshold):
        self.config['threshold'] = threshold
        self._save_config(self.config)

MOTIVATIONAL_MESSAGES = [
    "Don't forget to blink—your eyes need a break too!",
    "Blink now! Your tears are waiting to refresh your eyes.",
    "Your eyes called—they're thirsty. Blink!",
    "Blinking is your eye's built-in refresh button.",
    "Keep the dryness away—just a blink at a time.",
    "Don't stare too long—remember the blink rule: every 20 minutes!"
    ]

def show_critical_alert(message):
    
    def alert_thread():
        root.mainloop()

    threading.Thread(target=alert_thread, daemon=True).start()


app = Flask(__name__)
cors = CORS(app)

class BlinkDBManager:
    def __init__(self, db_path='blink_data.db'):
        self.db_path = db_path
        self.queue = Queue()
        self.running = True
        self._init_db()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS blink_data (
                            timestamp TEXT PRIMARY KEY,
                            blink_count INTEGER
                        )''')
            conn.commit()

    def _run(self):
        while self.running:
            try:
                timestamp, count = self.queue.get(timeout=1)
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute('''INSERT OR REPLACE INTO blink_data (timestamp, blink_count)
                                 VALUES (?, COALESCE((SELECT blink_count FROM blink_data WHERE timestamp=?), 0) + ?)''',
                              (timestamp, timestamp, count))
                    conn.commit()
            except Exception:
                continue

    def insert_blink(self, timestamp: str, count: int):
        if count <7:
            show_critical_alert(f"Blink count is too low: {count}")
        self.queue.put((timestamp, count))

    def _parse_timestamp(self, ts):
        """Helper method to parse timestamp with or without seconds"""
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None

    def get_today_data(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp LIKE ?''', (f"{today}%",))
            rows = c.fetchall()

        # Filter out any invalid timestamps and sort by time
        valid_rows = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt:
                valid_rows.append((dt, count))
        
        valid_rows.sort()
        total_blinks = sum(count for _, count in valid_rows)
        average = total_blinks / len(valid_rows) if valid_rows else 0
        valid_rows = valid_rows[-20:]
        return {
            "total_blinks": total_blinks,
            "average_blinks": round(average, 1),
            "data": [{
                "time": dt.strftime("%H:%M"),
                "blinks": count
            } for dt, count in valid_rows]
        }

    def get_last_20_minutes_data(self):
        now = datetime.now()
        start_time = now - timedelta(minutes=60)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Get all recent data and filter in Python to handle both timestamp formats
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp >= ?''',
                     (start_time.strftime("%Y-%m-%d %H:%M"),))
            rows = c.fetchall()

        # Process and filter rows
        result = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt and dt >= start_time:
                result.append({
                    'time': dt,
                    'blinks': count
                })
        
        # Sort by time and format the output
        result.sort(key=lambda x: x['time'])
        result = result[-20:]
        return [{
            'time': item['time'].strftime('%H:%M'),
            'blinks': item['blinks']
        } for item in result]

    def get_stats(self):
        today_data = self.get_today_data()
        last_20_data = self.get_last_20_minutes_data()
        last_20_avg = round(sum([x["blinks"] for x in last_20_data]) / len(last_20_data), 1) if last_20_data else 0

        percent_change = ((last_20_avg - today_data["average_blinks"]) / today_data["average_blinks"] * 100) \
            if today_data["average_blinks"] else 0

        return {
            "averageBlinks": today_data["average_blinks"],
            "last20Minutes": last_20_avg,
            "totalToday": today_data["total_blinks"],
            "percentageAbove": round(percent_change, 1)
        }

    def get_last_10_minutes_average(self):
        now = datetime.now()
        start_time = now - timedelta(minutes=10)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp >= ?''',
                     (start_time.strftime("%Y-%m-%d %H:%M"),))
            rows = c.fetchall()
        
        # Process and filter rows
        result = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt and dt >= start_time:
                result.append(count)
        
        avg = round(sum(result) / len(result), 1) if result else 0
        return {"average": avg, "count": len(result)}

    def get_today_entries_and_average(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp LIKE ?''', (f"{today}%",))
            rows = c.fetchall()
        valid_rows = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt:
                valid_rows.append((dt, count))
        valid_rows.sort()
        total_blinks = sum(count for _, count in valid_rows)
        average = total_blinks / len(valid_rows) if valid_rows else 0
        return {
            "entries": [{
                "time": dt.strftime("%H:%M"),
                "blinks": count
            } for dt, count in valid_rows],
            "average": round(average, 1),
            "count": len(valid_rows)
        }

    def get_last_minute_average(self):
        now = datetime.now()
        start_time = now - timedelta(minutes=1)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp >= ?''',
                     (start_time.strftime("%Y-%m-%d %H:%M"),))
            rows = c.fetchall()
        result = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt and dt >= start_time:
                result.append(count)
        avg = round(sum(result) / len(result), 1) if result else 0
        return {"average": avg, "count": len(result)}

    def get_last_entry(self):
        """Fetch the most recently updated blink entry (by timestamp)."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data ORDER BY timestamp DESC LIMIT 1''')
            row = c.fetchone()
        if row:
            ts, count = row
            return {"timestamp": ts, "blink_count": count}
        else:
            return {"timestamp": None, "blink_count": None}

    def get_metrics_by_date(self, date_str):
        """Fetch metrics for a given date: average, highest, and lowest blinks per minute."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data WHERE timestamp LIKE ?''', (f"{date_str}%",))
            rows = c.fetchall()
        valid_counts = []
        for ts, count in rows:
            dt = self._parse_timestamp(ts)
            if dt:
                valid_counts.append(count)
        if valid_counts:
            avg_blinks = round(sum(valid_counts) / len(valid_counts), 1)
            max_blinks = max(valid_counts)
            min_blinks = min(valid_counts)
        else:
            avg_blinks = 0
            max_blinks = 0
            min_blinks = 0
        return {
            "date": date_str,
            "average_blinks": avg_blinks,
            "max_blinks": max_blinks,
            "min_blinks": min_blinks,
            "count": len(valid_counts)
        }

    def stop(self):
        self.running = False
        self.thread.join()

# Main eye tracker logic
class EyeTracker:
    def __init__(self):
        self.running = False
        self.paused = False
        self.start_time = None
        self.last_alert_time = 0
        self.MIN_ALERT_INTERVAL = 1200

        self.NORMAL_BLINK_RATE = 12
        self.LOW_BLINK_RATE = 8

        self.id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        self.L_ratio_list = []
        self.R_ratio_list = []
        self.blink_counter = 0
        self.counter = 0
        self.threshold = config_manager.get_threshold()

        self.cap = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=4)

        self.status = "Not Started"
        self.elapsed_time = 0
        self.blink_rate = 0.0
        self.last_alert = ""
        self.session_data = {}

        self.last_minute = None
        self.blinks_this_minute = 0

    def process_eye_tracking(self, img, faces):
        if faces:
            if self.start_time is None:
                self.start_time = time.time()
                self.status = "Running"

            face = faces[0]
            leftUp = face[159]
            leftDown = face[23]
            leftLeft = face[130]
            leftRight = face[243]
            rightUp = face[386]
            rightDown = face[374]
            rightLeft = face[362]
            rightRight = face[263]

            LlengthHor, _ = self.detector.findDistance(leftLeft, leftRight)
            LlengthVer, _ = self.detector.findDistance(leftUp, leftDown)
            RlengthHor, _ = self.detector.findDistance(rightLeft, rightRight)
            RlengthVer, _ = self.detector.findDistance(rightUp, rightDown)

            Lratio = int((LlengthVer / LlengthHor) * 100)
            self.L_ratio_list.append(Lratio)
            if len(self.L_ratio_list) > 3:
                self.L_ratio_list.pop(0)
            LratioAvg = sum(self.L_ratio_list) / len(self.L_ratio_list)

            Rratio = int((RlengthVer / RlengthHor) * 100)
            self.R_ratio_list.append(Rratio)
            if len(self.R_ratio_list) > 3:
                self.R_ratio_list.pop(0)

            blink_detected = False
            if Lratio > self.threshold:
                if LratioAvg < self.threshold and self.counter == 0:
                    blink_detected = True
            elif Lratio > 29:
                if (LratioAvg - Lratio) > 5 and self.counter == 0:
                    blink_detected = True
            else:
                if (LratioAvg - Lratio) > 2 and self.counter == 0:
                    blink_detected = True

            if blink_detected:
                self.blink_counter += 1
                self.blinks_this_minute += 1
                self.counter = 1
                print("Blink detected")

            if self.counter != 0:
                self.counter += 1
                if self.counter > 10:
                    self.counter = 0

            current_time = time.time()
            self.elapsed_time = current_time - self.start_time if self.start_time else 0

            # Store per-minute blink data
            current_minute = datetime.now().strftime('%Y-%m-%d %H:%M')
            if self.last_minute is None:
                self.last_minute = current_minute
            elif current_minute != self.last_minute:
                db_manager.insert_blink(self.last_minute, self.blinks_this_minute)
                self.last_minute = current_minute
                self.blinks_this_minute = 1  # Count the current blink

            if self.elapsed_time > 30:
                self.blink_rate = self.blink_counter / (self.elapsed_time / 60)
                self.check_blink_rate(self.blink_rate, current_time)

    def update_status(self, blink_rate):
        if blink_rate < self.LOW_BLINK_RATE:
            self.status = "Critical"
        elif blink_rate < self.NORMAL_BLINK_RATE:
            self.status = "Below Average"
        else:
            self.status = "Normal"

    def check_blink_rate(self, blink_rate, current_time):
        if current_time - self.last_alert_time < self.MIN_ALERT_INTERVAL:
            return

        motivational = random.choice(MOTIVATIONAL_MESSAGES)
        if blink_rate < self.LOW_BLINK_RATE:
            self.last_alert = f"Warning: Very low blink rate detected ({blink_rate:.1f} bpm)! Please take a break.\n\n{motivational}"
            self.last_alert_time = current_time
        elif blink_rate < self.NORMAL_BLINK_RATE:
            self.last_alert = f"Your blink rate ({blink_rate:.1f} bpm) is below average. Try the 20-20-20 rule.\n\n{motivational}"
            self.last_alert_time = current_time

        self.update_status(blink_rate)

    def tracking_loop(self):
        while self.running:
            if not self.paused:
                success, img = self.cap.read()
                if not success:
                    self.status = "Camera Error"
                    break
                img, faces = self.detector.findFaceMesh(img, draw=False)
                self.process_eye_tracking(img, faces)
            time.sleep(0.01)

    def start_tracking(self):
        if not self.running:
            self.running = True
            self.status = "Starting"
            self.thread = threading.Thread(target=self.tracking_loop, daemon=True)
            self.thread.start()
            return True
        return False

    def stop_tracking(self):
        if self.running:
            self.running = False
            self.status = "Stopped"
            if self.thread.is_alive():
                self.thread.join(timeout=1.0)
            return True
        return False

    def pause_tracking(self):
        self.paused = True
        self.status = "Paused"

    def resume_tracking(self):
        self.paused = False
        self.status = "Running"

    def save_session(self):
        if self.start_time is None:
            return False

        if not os.path.exists('sessions'):
            os.makedirs('sessions')

        self.session_data = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'duration': self.elapsed_time,
            'total_blinks': self.blink_counter,
            'blink_rate': self.blink_rate,
            'status': self.status
        }

        filename = f"sessions/session_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.session_data, f)

        return True

    def get_status(self):
        return {
            "status": self.status,
            "running": self.running,
            "paused": self.paused,
            "blink_count": self.blink_counter,
            "blink_rate": round(self.blink_rate, 1),
            "elapsed_time": round(self.elapsed_time, 1),
            "last_alert": self.last_alert,
            "threshold": self.threshold
        }

# Create global tracker and DB manager
config_manager = ConfigManager()
tracker = EyeTracker()
db_manager = BlinkDBManager()

# Start tracking by default
tracker.start_tracking()

# Flask endpoints
@app.route('/start', methods=['POST'])
def start_tracking():
    # Tracking is already started by default, but keep endpoint for compatibility
    if tracker.running:
        return jsonify({"status": "Tracking already running"}), 200
    if tracker.start_tracking():
        return jsonify({"status": "Tracking started"}), 200
    return jsonify({"error": "Could not start tracking"}), 400

@app.route('/stop', methods=['POST'])
def stop_tracking():
    if tracker.stop_tracking():
        return jsonify({"status": "Tracking stopped"}), 200
    return jsonify({"error": "Tracking not running"}), 400

@app.route('/pause', methods=['POST'])
def pause_tracking():
    tracker.pause_tracking()
    return jsonify({"status": "Tracking paused"}), 200

@app.route('/resume', methods=['POST'])
def resume_tracking():
    tracker.resume_tracking()
    return jsonify({"status": "Tracking resumed"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(tracker.get_status()), 200

@app.route('/save', methods=['POST'])
def save_session():
    if tracker.save_session():
        return jsonify({"status": "Session saved"}), 200
    return jsonify({"error": "No session to save"}), 400

@app.route('/config', methods=['POST'])
def update_config():
    data = request.json
    if 'threshold' in data:
        new_threshold = max(20, min(50, int(data['threshold'])))
        tracker.threshold = new_threshold
        config_manager.set_threshold(new_threshold)

    return jsonify({
        "threshold": tracker.threshold,
        "normal_blink_rate": tracker.NORMAL_BLINK_RATE,
        "low_blink_rate": tracker.LOW_BLINK_RATE
    }), 200

@app.route('/blinks', methods=['GET'])
def get_blink_data():
    with sqlite3.connect('blink_data.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM blink_data ORDER BY timestamp DESC LIMIT 60")
        rows = c.fetchall()
    return jsonify([{"timestamp": ts, "blink_count": count} for ts, count in rows]), 200

@app.route('/shutdown', methods=['POST'])
def shutdown():
    tracker.stop_tracking()
    db_manager.stop()
    return jsonify({"status": "Shutdown complete"}), 200

@app.route('/api/blink-rate')
def blink_rate():
    return jsonify(db_manager.get_today_data()["data"])

@app.route('/api/recent-activity')
def recent_activity():
    return jsonify(db_manager.get_last_20_minutes_data())

@app.route('/api/stats')
def blink_stats():
    return jsonify(db_manager.get_stats())

@app.route('/api/10min-average')
def ten_min_average():
    return jsonify(db_manager.get_last_10_minutes_average())

@app.route('/api/today-entries')
def today_entries():
    return jsonify(db_manager.get_today_entries_and_average())

@app.route('/api/last-minute-average')
def last_minute_average():
    return jsonify(db_manager.get_last_minute_average())

@app.route('/api/last-entry')
def last_entry():
    return jsonify(db_manager.get_last_entry())

@app.route('/api/metrics-by-date', methods=['POST'])
def metrics_by_date():
    data = request.json
    date_str = data.get('date')  # Expecting 'YYYY-MM-DD'
    if not date_str:
        return jsonify({"error": "Missing date parameter"}), 400
    metrics = db_manager.get_metrics_by_date(date_str)
    return jsonify(metrics)

#@app.route('/api/alert', methods=['POST'])
@app.route('/test-alert', methods=['POST'])
def test_alert():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        motivational = random.choice(MOTIVATIONAL_MESSAGES)

        if not message:
            message = "⚠️ Warning Blink now!"

        full_message = f"{message}\n\n{motivational}"

        logging.info(f"[ALERT_TRIGGERED] Message received: {full_message}")
        show_critical_alert(full_message)

        return jsonify({"status": "Test alert triggered", "message": full_message}), 200

    except Exception as e:
        logging.error(f"[ALERT_FAILED] {str(e)}")
        return jsonify({"status": "Error", "error": str(e)}), 500

if __name__ == '__main__':
    tracker.start_tracking()
    app.run(host='0.0.0.0', port=9783, threaded=True)
