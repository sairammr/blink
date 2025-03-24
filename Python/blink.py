import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
from PIL import Image, ImageTk

class EyeTrackingApp:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Eye Health Monitor")
        self.root.geometry("1280x720")
        self.root.minsize(1024, 700)  # Minimum window size for responsive layout
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'))
        self.style.configure('Stats.TLabel', font=('Helvetica', 12))
        self.style.configure('Alert.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Control.TButton', font=('Helvetica', 11))
        self.style.configure('Switch.TCheckbutton', font=('Helvetica', 11))
        
        # Initialize tracking variables
        self.running = False
        self.paused = False
        self.start_time = None
        self.first_60_seconds_passed = False
        self.last_alert_time = 0
        self.MIN_ALERT_INTERVAL = 5
        
        self.NORMAL_BLINK_RATE = 12
        self.LOW_BLINK_RATE = 8
        
        self.id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        self.L_ratio_list = []
        self.R_ratio_list = []
        self.blink_counter = 0
        self.counter = 0
        self.color = (255, 0, 255)
        self.ratio_avg = 0
        self.threshold = 34
        
        # Add notification control variable
        self.notifications_enabled = tk.BooleanVar(value=True)
        
        # Initialize UI label references to None before setup
        self.normal_value_label = None
        self.low_value_label = None
        self.threshold_value_label = None
        
        # Initialize camera and detection
        self.cap = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=4)
        self.plot_y = LivePlot(640, 360, [0, 50], invert=False)
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Eye Health Monitor", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Create main content frame
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1, minsize=350)  # Controls column
        content_frame.columnconfigure(1, weight=3, minsize=600)  # Video column
        content_frame.rowconfigure(0, weight=1)
        
        # Left column - Controls and Stats
        left_column = ttk.Frame(content_frame, padding="10")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Statistics Panel
        stats_panel = ttk.LabelFrame(left_column, text="Real-time Statistics", padding="10")
        stats_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Stats grid layout
        stats_panel.columnconfigure(0, weight=1)
        stats_panel.columnconfigure(1, weight=1)
        
        self.blink_label = ttk.Label(stats_panel, text="Total Blinks:", style='Stats.TLabel')
        self.blink_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.blink_value = ttk.Label(stats_panel, text="0", style='Stats.TLabel')
        self.blink_value.grid(row=0, column=1, sticky=tk.E)
        
        self.rate_label = ttk.Label(stats_panel, text="Blink Rate:", style='Stats.TLabel')
        self.rate_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.rate_value = ttk.Label(stats_panel, text="0.0 bpm", style='Stats.TLabel')
        self.rate_value.grid(row=1, column=1, sticky=tk.E)
        
        self.status_label = ttk.Label(stats_panel, text="Status:", style='Stats.TLabel')
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.status_value = ttk.Label(stats_panel, text="Normal", style='Alert.TLabel', foreground="green")
        self.status_value.grid(row=2, column=1, sticky=tk.E)
        
        self.time_label = ttk.Label(stats_panel, text="Session Time:", style='Stats.TLabel')
        self.time_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.time_value = ttk.Label(stats_panel, text="0:00", style='Stats.TLabel')
        self.time_value.grid(row=3, column=1, sticky=tk.E)
        
        # Settings Panel
        settings_panel = ttk.LabelFrame(left_column, text="Settings", padding="10")
        settings_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Blink Rate Threshold Slider
        blink_rate_frame = ttk.Frame(settings_panel)
        blink_rate_frame.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(blink_rate_frame, text="Blink Rate Thresholds:", style='Stats.TLabel').pack(anchor=tk.W)
        
        # Normal threshold slider
        normal_frame = ttk.Frame(settings_panel)
        normal_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(normal_frame, text="Normal:", style='Stats.TLabel', width=10).pack(side=tk.LEFT)
        
        # Create the normal_value_label before setting up the scale that uses it
        self.normal_value_label = ttk.Label(normal_frame, text=f"{self.NORMAL_BLINK_RATE} bpm", style='Stats.TLabel', width=7)
        
        self.normal_scale = ttk.Scale(normal_frame, from_=8, to=20, orient=tk.HORIZONTAL, 
                                     command=self.update_normal_threshold)
        self.normal_scale.set(self.NORMAL_BLINK_RATE)
        self.normal_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.normal_value_label.pack(side=tk.LEFT)
        
        # Low threshold slider
        low_frame = ttk.Frame(settings_panel)
        low_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(low_frame, text="Warning:", style='Stats.TLabel', width=10).pack(side=tk.LEFT)
        
        # Create the low_value_label before setting up the scale
        self.low_value_label = ttk.Label(low_frame, text=f"{self.LOW_BLINK_RATE} bpm", style='Stats.TLabel', width=7)
        
        self.low_scale = ttk.Scale(low_frame, from_=4, to=15, orient=tk.HORIZONTAL, 
                                  command=self.update_low_threshold)
        self.low_scale.set(self.LOW_BLINK_RATE)
        self.low_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.low_value_label.pack(side=tk.LEFT)
        
        # Blink Detection Sensitivity section
        ttk.Separator(settings_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        sensitivity_frame = ttk.Frame(settings_panel)
        sensitivity_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(sensitivity_frame, text="Blink Detection Sensitivity:", style='Stats.TLabel').pack(anchor=tk.W)
        
        sensitivity_scale_frame = ttk.Frame(settings_panel)
        sensitivity_scale_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(sensitivity_scale_frame, text="Low", style='Stats.TLabel').pack(side=tk.LEFT)
        
        # Create the threshold_value_label before setting up the scale
        self.threshold_value_label = ttk.Label(settings_panel, text=f"Threshold: {self.threshold}", style='Stats.TLabel')
        
        self.sensitivity_scale = ttk.Scale(sensitivity_scale_frame, from_=20, to=50, orient=tk.HORIZONTAL, 
                                           command=self.update_threshold)
        self.sensitivity_scale.set(self.threshold)
        self.sensitivity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(sensitivity_scale_frame, text="High", style='Stats.TLabel').pack(side=tk.LEFT)
        
        self.threshold_value_label.pack(anchor=tk.E, pady=(0, 10))
        
        # Notification Toggle Switch
        ttk.Separator(settings_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        notification_frame = ttk.Frame(settings_panel)
        notification_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(notification_frame, text="Notifications:", style='Stats.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.notification_toggle = ttk.Checkbutton(notification_frame, text="Enabled", 
                                                  variable=self.notifications_enabled, 
                                                  style='Switch.TCheckbutton')
        self.notification_toggle.pack(side=tk.LEFT)
        
        # Controls Panel
        controls_panel = ttk.LabelFrame(left_column, text="Controls", padding="10")
        controls_panel.pack(fill=tk.X)
        
        self.start_button = ttk.Button(controls_panel, text="Start Monitoring", style='Control.TButton',command=self.toggle_tracking)
        self.start_button.pack(fill=tk.X, pady=(0, 10))
        
        self.save_button = ttk.Button(controls_panel, text="Save Session", style='Control.TButton',command=self.save_session)
        self.save_button.pack(fill=tk.X)
        
        # Right column - Video Feed & Graphs in a Grid
        right_column = ttk.Frame(content_frame)
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.columnconfigure(0, weight=1)
        right_column.rowconfigure(0, weight=2)  # Video takes more space
        right_column.rowconfigure(1, weight=1)  # Graphs take less space
        
        # Video panel
        video_panel = ttk.LabelFrame(right_column, text="Video Feed", padding="10")
        video_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.video_canvas = tk.Canvas(video_panel, bg='black')
        self.video_canvas.pack(expand=True, fill=tk.BOTH)
        
        # Graphs panel
        graph_panel = ttk.LabelFrame(right_column, text="Eye Tracking Graphs", padding="10")
        graph_panel.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        graph_panel.columnconfigure(0, weight=1)
        graph_panel.columnconfigure(1, weight=1)
        
        # Left eye graph
        left_graph_frame = ttk.Frame(graph_panel)
        left_graph_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ttk.Label(left_graph_frame, text="Left Eye", style='Stats.TLabel').pack(anchor=tk.W)
        self.left_graph_canvas = tk.Canvas(left_graph_frame, bg='black')
        self.left_graph_canvas.pack(expand=True, fill=tk.BOTH)
        
        # Right eye graph
        right_graph_frame = ttk.Frame(graph_panel)
        right_graph_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        ttk.Label(right_graph_frame, text="Right Eye", style='Stats.TLabel').pack(anchor=tk.W)
        self.right_graph_canvas = tk.Canvas(right_graph_frame, bg='black')
        self.right_graph_canvas.pack(expand=True, fill=tk.BOTH)

    def update_normal_threshold(self, value):
        self.NORMAL_BLINK_RATE = int(float(value))
        if self.normal_value_label:
            self.normal_value_label.configure(text=f"{self.NORMAL_BLINK_RATE} bpm")
        # Ensure low threshold doesn't exceed normal threshold
        if self.LOW_BLINK_RATE >= self.NORMAL_BLINK_RATE:
            self.LOW_BLINK_RATE = self.NORMAL_BLINK_RATE - 1
            if hasattr(self, 'low_scale') and self.low_scale:
                self.low_scale.set(self.LOW_BLINK_RATE)
            if self.low_value_label:
                self.low_value_label.configure(text=f"{self.LOW_BLINK_RATE} bpm")

    def update_low_threshold(self, value):
        self.LOW_BLINK_RATE = int(float(value))
        if self.low_value_label:
            self.low_value_label.configure(text=f"{self.LOW_BLINK_RATE} bpm")
        # Ensure normal threshold isn't below low threshold
        if self.NORMAL_BLINK_RATE <= self.LOW_BLINK_RATE:
            self.NORMAL_BLINK_RATE = self.LOW_BLINK_RATE + 1
            if hasattr(self, 'normal_scale') and self.normal_scale:
                self.normal_scale.set(self.NORMAL_BLINK_RATE)
            if self.normal_value_label:
                self.normal_value_label.configure(text=f"{self.NORMAL_BLINK_RATE} bpm")

    def update_threshold(self, value):
        self.threshold = int(float(value))
        if self.threshold_value_label:
            self.threshold_value_label.configure(text=f"Threshold: {self.threshold}")

    def update_status(self, blink_rate):
        if blink_rate < self.LOW_BLINK_RATE:
            self.status_value.configure(text="Critical", foreground="red")
        elif blink_rate < self.NORMAL_BLINK_RATE:
            self.status_value.configure(text="Below Average", foreground="orange")
        else:
            self.status_value.configure(text="Normal", foreground="green")

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def update_stats(self, elapsed_time):
        self.blink_value.configure(text=str(self.blink_counter))
        
        if elapsed_time > 30:
            blink_rate = self.blink_counter / (elapsed_time / 60)
            self.rate_value.configure(text=f"{blink_rate:.1f} bpm")
            self.update_status(blink_rate)
            self.check_blink_rate(blink_rate)
        
        self.time_value.configure(text=self.format_time(elapsed_time))

    def check_blink_rate(self, blink_rate):
        # Check if notifications are disabled
        if not self.notifications_enabled.get():
            return
            
        current_time = time.time()
        if current_time - self.last_alert_time < self.MIN_ALERT_INTERVAL:
            return  # Don't show alerts too frequently
            
        message = None
        if blink_rate < self.LOW_BLINK_RATE:
            message = f"Warning: Very low blink rate detected ({blink_rate:.1f} bpm)!\nPlease take a break and rest your eyes."
        elif blink_rate < self.NORMAL_BLINK_RATE:
            message = f"Your blink rate ({blink_rate:.1f} bpm) is below average.\nTry the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds."
            
        if message:
            self.show_alert(message)
            self.last_alert_time = current_time

    def show_alert(self, message):
        def alert():
            alert_window = tk.Toplevel(self.root)
            alert_window.title("Blink Alert")
            alert_window.geometry("400x200")
            alert_window.transient(self.root)
            alert_window.grab_set()  # Prevent interactions with the main window
            alert_window.attributes("-topmost", True)  # Keep the alert on top

            style = ttk.Style()
            style.configure('Alert.TLabel', font=('Helvetica', 11))

            frame = ttk.Frame(alert_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="⚠️ Attention", font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))
            ttk.Label(frame, text=message, style='Alert.TLabel', wraplength=350).pack(pady=(0, 20))

            ttk.Button(frame, text="OK", command=alert_window.destroy).pack()

            # Center the window
            alert_window.update_idletasks()
            width = alert_window.winfo_width()
            height = alert_window.winfo_height()
            x = (alert_window.winfo_screenwidth() // 2) - (width // 2)
            y = (alert_window.winfo_screenheight() // 2) - (height // 2)
            alert_window.geometry(f'{width}x{height}+{x}+{y}')

            alert_window.focus_force()  # Force focus to the alert window

        threading.Thread(target=alert).start()

    def process_eye_tracking(self, img, faces):
        if faces:
            if self.start_time is None:
                self.start_time = time.time()
                
            face = faces[0]
            for id in self.id_list:
                cv2.circle(img, face[id], 5, (255, 0, 255), cv2.FILLED)
                
            # Extract eye points
            leftUp = face[159]
            leftDown = face[23]
            leftLeft = face[130]
            leftRight = face[243]
            
            # Check if rightUp and other right eye points are available
            # If not available, use default points or handle appropriately
            if len(face) > 386:
                rightUp = face[386]
                rightDown = face[374]
                rightLeft = face[362]
                rightRight = face[263]
                
                # Calculate distances
                LlengthHor, _ = self.detector.findDistance(leftLeft, leftRight)
                LlengthVer, _ = self.detector.findDistance(leftUp, leftDown)
                RlengthHor, _ = self.detector.findDistance(rightLeft, rightRight)
                RlengthVer, _ = self.detector.findDistance(rightUp, rightDown)
                
                # Draw lines
                cv2.line(img, leftUp, leftDown, self.color, 3)
                cv2.line(img, leftLeft, leftRight, self.color, 3)
                cv2.line(img, rightUp, rightDown, self.color, 3)
                cv2.line(img, rightLeft, rightRight, self.color, 3)
                
                # Calculate ratios
                if LlengthHor > 0:
                    Lratio = int((LlengthVer / LlengthHor) * 100)
                    self.L_ratio_list.append(Lratio)
                    if len(self.L_ratio_list) > 3:
                        self.L_ratio_list.pop(0)
                    LratioAvg = sum(self.L_ratio_list) / len(self.L_ratio_list)
                    
                    if RlengthHor > 0:
                        Rratio = int((RlengthVer / RlengthHor) * 100)
                        self.R_ratio_list.append(Rratio)
                        if len(self.R_ratio_list) > 3:
                            self.R_ratio_list.pop(0)
                        RratioAvg = sum(self.R_ratio_list) / len(self.R_ratio_list)
                    else:
                        Rratio = 0
                        RratioAvg = 0
                    
                    # Blink detection
                    if Lratio > self.threshold:
                        if LratioAvg < self.threshold and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                    elif Lratio > 29:
                        if (LratioAvg - Lratio) > 5 and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                    else:
                        if (LratioAvg - Lratio) > 2 and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                            
                    if self.counter != 0:
                        self.counter += 1
                        if self.counter > 10:
                            self.counter = 0
                            self.color = (255, 0, 255)
                else:
                    LratioAvg = 0
                    RratioAvg = 0
            else:
                # Handle case where right eye points aren't available
                LlengthHor, _ = self.detector.findDistance(leftLeft, leftRight)
                LlengthVer, _ = self.detector.findDistance(leftUp, leftDown)
                
                # Draw lines for left eye only
                cv2.line(img, leftUp, leftDown, self.color, 3)
                cv2.line(img, leftLeft, leftRight, self.color, 3)
                
                # Calculate ratio for left eye only
                if LlengthHor > 0:
                    Lratio = int((LlengthVer / LlengthHor) * 100)
                    self.L_ratio_list.append(Lratio)
                    if len(self.L_ratio_list) > 3:
                        self.L_ratio_list.pop(0)
                    LratioAvg = sum(self.L_ratio_list) / len(self.L_ratio_list)
                    
                    # Blink detection with left eye only
                    if Lratio > self.threshold:
                        if LratioAvg < self.threshold and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                    elif Lratio > 29:
                        if (LratioAvg - Lratio) > 5 and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                    else:
                        if (LratioAvg - Lratio) > 2 and self.counter == 0:
                            self.blink_counter += 1
                            self.counter = 1
                            self.color = (0, 255, 0)
                            
                    if self.counter != 0:
                        self.counter += 1
                        if self.counter > 10:
                            self.counter = 0
                            self.color = (255, 0, 255)
                else:
                    LratioAvg = 0
                
                # Set right eye ratio to same as left for simplicity
                RratioAvg = LratioAvg
                
            # Add blink counter to image
            cvzone.putTextRect(img, f'Blink Counter: {self.blink_counter}', (50, 100), colorR=self.color)
            
            # Create plots
            LimgPlot = self.plot_y.update(LratioAvg, self.color)
            RimgPlot = self.plot_y.update(RratioAvg, self.color)
            
            return img, LimgPlot, RimgPlot
        else:
            # Empty plots
            imgPlot = self.plot_y.update(self.ratio_avg, self.color)
            return img, imgPlot, imgPlot
            
    def tracking_loop(self):
        while self.running:
            if not self.paused:
                success, img = self.cap.read()
                if not success:
                    break
                    
                img, faces = self.detector.findFaceMesh(img, draw=False)
                img, left_plot, right_plot = self.process_eye_tracking(img, faces)
                
                # Update video display
                video_img = cv2.resize(img, (640, 480))
                video_img = cv2.cvtColor(video_img, cv2.COLOR_BGR2RGB)
                video_photo = ImageTk.PhotoImage(image=Image.fromarray(video_img))
                self.video_canvas.create_image(0, 0, image=video_photo, anchor=tk.NW)
                self.video_canvas.image = video_photo
                
                # Update left eye graph
                left_plot = cv2.cvtColor(left_plot, cv2.COLOR_BGR2RGB)
                left_photo = ImageTk.PhotoImage(image=Image.fromarray(left_plot))
                self.left_graph_canvas.create_image(0, 0, image=left_photo, anchor=tk.NW)
                self.left_graph_canvas.image = left_photo
                
                # Update right eye graph
                right_plot = cv2.cvtColor(right_plot, cv2.COLOR_BGR2RGB)
                right_photo = ImageTk.PhotoImage(image=Image.fromarray(right_plot))
                self.right_graph_canvas.create_image(0, 0, image=right_photo, anchor=tk.NW)
                self.right_graph_canvas.image = right_photo
                
                # Update statistics
                if self.start_time is not None:
                    elapsed_time = int(time.time() - self.start_time)
                    self.update_stats(elapsed_time)
                                
            self.root.update()
            
    def toggle_tracking(self):
        if not self.running:
            self.running = True
            self.start_button.configure(text="Stop Monitoring")
            threading.Thread(target=self.tracking_loop, daemon=True).start()
        else:
            self.running = False
            self.start_button.configure(text="Start Monitoring")
            
    def save_session(self):
        if self.start_time is None:
            messagebox.showwarning("Warning", "No session data to save!")
            return
            
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
            
        elapsed_time = int(time.time() - self.start_time)
        blink_rate = self.blink_counter / (elapsed_time / 60) if elapsed_time > 0 else 0
        
        data = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'duration': elapsed_time,
            'total_blinks': self.blink_counter,
            'blink_rate': blink_rate,
            'threshold_setting': self.threshold,
            'normal_blink_rate': self.NORMAL_BLINK_RATE,
            'low_blink_rate': self.LOW_BLINK_RATE,
            'notifications_enabled': self.notifications_enabled.get()
        }
        
        filename = f"sessions/session_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
            
        messagebox.showinfo("Success", "Session data saved successfully!")
        
    def run(self):
        # Make the window responsive
        for i in range(3):
            self.root.columnconfigure(i, weight=1)
            self.root.rowconfigure(i, weight=1)
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.running = False
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    app = EyeTrackingApp()
    app.run()