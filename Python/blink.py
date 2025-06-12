import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import threading
import datetime
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

class EyeTracker:
    def __init__(self):
        # Initialize tracking variables
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
        self.threshold = 34
        
        # Initialize camera and detection
        self.cap = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=4)
        
        # State variables for API
        self.status = "Not Started"
        self.elapsed_time = 0
        self.blink_rate = 0.0
        self.last_alert = ""
        self.session_data = {}

    def process_eye_tracking(self, img, faces):
        if faces:
            if self.start_time is None:
                self.start_time = time.time()
                self.status = "Running"
                
            face = faces[0]
            
            # Extract eye points
            leftUp = face[159]
            leftDown = face[23]
            leftLeft = face[130]
            leftRight = face[243]
            
            rightUp = face[386]
            rightDown = face[374]
            rightLeft = face[362]
            rightRight = face[263]
            
            # Calculate distances
            LlengthHor, _ = self.detector.findDistance(leftLeft, leftRight)
            LlengthVer, _ = self.detector.findDistance(leftUp, leftDown)
            RlengthHor, _ = self.detector.findDistance(rightLeft, rightRight)
            RlengthVer, _ = self.detector.findDistance(rightUp, rightDown)
            
            # Calculate ratios
            Lratio = int((LlengthVer / LlengthHor) * 100)
            self.L_ratio_list.append(Lratio)
            if len(self.L_ratio_list) > 3:
                self.L_ratio_list.pop(0)
            LratioAvg = sum(self.L_ratio_list) / len(self.L_ratio_list)
            
            Rratio = int((RlengthVer / RlengthHor) * 100)
            self.R_ratio_list.append(Rratio)
            if len(self.R_ratio_list) > 3:
                self.R_ratio_list.pop(0)
            
            # Blink detection
            if Lratio > self.threshold:
                if LratioAvg < self.threshold and self.counter == 0:
                    self.blink_counter += 1
                    print("Blink detected")
                    self.counter = 1
            elif Lratio > 29:
                if (LratioAvg - Lratio) > 5 and self.counter == 0:
                    self.blink_counter += 1
                    print("Blink detected")
                    self.counter = 1
            else:
                if (LratioAvg - Lratio) > 2 and self.counter == 0:
                    self.blink_counter += 1
                    print("Blink detected")
                    self.counter = 1
                    
            if self.counter != 0:
                self.counter += 1
                if self.counter > 10:
                    self.counter = 0
                    
            # Update status
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time if self.start_time else 0
            
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
                
            time.sleep(0.01)  # Reduce CPU usage
            
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

# Create tracker instance
tracker = EyeTracker()

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
        tracker.threshold = max(20, min(50, int(data['threshold'])))
    if 'normal_rate' in data:
        tracker.NORMAL_BLINK_RATE = max(1, int(data['normal_rate']))
    if 'low_rate' in data:
        tracker.LOW_BLINK_RATE = max(1, int(data['low_rate']))
        
    return jsonify({
        "threshold": tracker.threshold,
        "normal_blink_rate": tracker.NORMAL_BLINK_RATE,
        "low_blink_rate": tracker.LOW_BLINK_RATE
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)