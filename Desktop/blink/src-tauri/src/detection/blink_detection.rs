use tauri::async_runtime;
use opencv::{
    core::{self, Vector},
    objdetect,
    prelude::*,
    imgproc,
    Result,
    videoio
};
use opencv::core::AlgorithmHint;
use chrono::{Utc};
use std::{sync::mpsc, thread, time::{Instant, Duration}};
use std::sync::Arc;
use crate::IntervalEntry;

struct FaceDetector {
    eye_cascade: objdetect::CascadeClassifier,
}
use crate::DBHandler;

impl FaceDetector {
    fn new(cascade_path: &str) -> Result<Self> {
        let eye_cascade = objdetect::CascadeClassifier::new(cascade_path)?;
        Ok(Self { eye_cascade })
    }

    fn detect_eyes(&mut self, frame: &Mat) -> Result<Vector<core::Rect>> {
        let mut gray = Mat::default();
        imgproc::cvt_color(frame, &mut gray, imgproc::COLOR_BGR2GRAY, 0,opencv::core::AlgorithmHint::ALGO_HINT_DEFAULT)?;

        let mut eyes = Vector::new();
        self.eye_cascade.detect_multi_scale(
            &gray,
            &mut eyes,
            1.1,
            3,
            objdetect::CASCADE_SCALE_IMAGE,
            core::Size::new(20, 20),
            core::Size::new(0, 0),
        )?;
        Ok(eyes)
    }
}

#[tauri::command]
pub fn blink_detection(db_handler: Arc<DBHandler>) -> Result<(), String> {
    async_runtime::spawn(async move {
        let mut cap = videoio::VideoCapture::new(0, videoio::CAP_ANY)
            .map_err(|_| opencv::Error::new(core::StsError, "Failed to open webcam"))
            .map_err(|e| e.to_string())?;

        let mut detector = FaceDetector::new("src/detection/models/haarcascade_eye.xml")
            .map_err(|e| e.to_string())?;

        let mut blink_counter = 0;
        let mut prev_eyes_count = 0;
        let mut last_blink_time = Instant::now();
        let mut last_frame_time = Instant::now();
        
        // Track continuous presence
        let mut eyes_present = false;
        let mut presence_duration = Duration::from_secs(0);
        
        // Add frame counting for eye absence
        let mut no_eyes_frame_count = 0;
        const MAX_NO_EYES_FRAMES: i32 = 5;

        // Track interval timestamps
        let mut interval_start_time = Utc::now().naive_utc();

        let (tx, rx): (mpsc::Sender<String>, mpsc::Receiver<String>) = mpsc::channel();
        let alert_thread = thread::spawn(move || {
            while let Ok(message) = rx.recv() {
                println!("Alert: {}", message);
            }
        });

        let mut frame = Mat::default();

        loop {
            cap.read(&mut frame)
                .map_err(|e| e.to_string())?;

            if frame.empty() {
                eprintln!("Empty frame captured. Exiting...");
                break;
            }

            let current_time = Instant::now();
            let frame_duration = current_time.duration_since(last_frame_time);
            last_frame_time = current_time;

            let eyes = detector.detect_eyes(&frame)
                .map_err(|e| e.to_string())?;
            let current_eyes = eyes.len();

            // Update presence tracking with frame counting
            if current_eyes >= 1 {
                no_eyes_frame_count = 0;
                if !eyes_present {
                    eyes_present = true;
                }
                presence_duration += frame_duration;
            } else {
                no_eyes_frame_count += 1;
                if no_eyes_frame_count >= MAX_NO_EYES_FRAMES {
                    eyes_present = false;
                }
            }

            // Blink detection logic
            if prev_eyes_count == 2 && current_eyes < 2 {
                if last_blink_time.elapsed().as_millis() > 100 {
                    blink_counter += 1;
                    last_blink_time = Instant::now();
                }
            }

            if presence_duration >= Duration::from_secs(5) {
                let end_time = Utc::now().naive_utc();
                
                let metrics = IntervalEntry {
                    start_time: interval_start_time,
                    end_time,
                    blink_count: blink_counter,
                    presence_duration,
                };

                // Insert metrics into DB
                if let Err(e) = db_handler.insert_interval(metrics) {
                    eprintln!("Error inserting metrics into DB: {}", e);
                }

                // Reset counters and timers
                interval_start_time = end_time; // Start new interval immediately after previous one
                blink_counter = 0;
                presence_duration = Duration::from_secs(0);
                no_eyes_frame_count = 0;
            }

            prev_eyes_count = current_eyes;
            // println!(
            //     "Blinks: {} | Presence: {:.1}s | Eyes Present: {} | No Eyes Frames: {} | Start Time: {}", 
            //     blink_counter, 
            //     presence_duration.as_secs_f32(),
            //     eyes_present,
            //     no_eyes_frame_count,
            //     interval_start_time
            // );

            thread::sleep(Duration::from_millis(5));
        }

        Ok::<(), String>(())
    });

    Ok(())
}