import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import threading
import datetime
import json
import os
import sqlite3
from queue import Queue
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
from config_manager import ConfigManager

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
    def insert_mock_data(self, count=50):
        """
        Inserts `count` number of mock blink entries between 30 and 20 minutes ago from current time.
        """
        now = datetime.now()
        earliest = now - timedelta(minutes=30)
        latest = now - timedelta(minutes=20)

        for _ in range(count):
            # Generate a timestamp between earliest and latest
            delta_seconds = random.randint(0, int((latest - earliest).total_seconds()))
            timestamp = earliest + timedelta(seconds=delta_seconds)
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            blink_count = random.randint(1, 5)
            self.insert_blink(timestamp_str, blink_count)
            print(f"Inserted {blink_count} blinks at {timestamp_str}")

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
        self.queue.put((timestamp, count))

    def get_today_data(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp LIKE ?''', (f"{today}%",))
            rows = c.fetchall()

        total_blinks = sum([r[1] for r in rows])
        average = total_blinks / len(rows) if rows else 0

        return {
            "total_blinks": total_blinks,
            "average_blinks": round(average, 1),
            "data": [{
                "time": datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                "blinks": count
            } for ts, count in sorted(rows)]
        }

    def get_last_20_minutes_data(self):
        now = datetime.now()
        start_time = now - timedelta(minutes=60)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT timestamp, blink_count FROM blink_data 
                         WHERE timestamp BETWEEN ? AND ?''',
                      (start_time.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")))
            rows = c.fetchall()

        return [{
            "time": datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
            "blinks": count
        } for ts, count in sorted(rows)]

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
        self.MIN_ALERT_INTERVAL = 5

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
            current_minute = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
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

        if blink_rate < self.LOW_BLINK_RATE:
            self.last_alert = f"Warning: Very low blink rate detected ({blink_rate:.1f} bpm)! Please take a break."
            self.last_alert_time = current_time
        elif blink_rate < self.NORMAL_BLINK_RATE:
            self.last_alert = f"Your blink rate ({blink_rate:.1f} bpm) is below average. Try the 20-20-20 rule."
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
db_manager.insert_mock_data()

# Flask endpoints
@app.route('/start', methods=['POST'])
def start_tracking():
    if tracker.start_tracking():
        return jsonify({"status": "Tracking started"}), 200
    return jsonify({"error": "Tracking already running"}), 400

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
