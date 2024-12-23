use tauri::async_runtime;
use opencv::{
    core::{self, Vector},
    objdetect,
    prelude::*,
    imgproc,
    Result,
};
use chrono::{NaiveDateTime, Utc};
use std::{sync::mpsc, thread, time::Instant};
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
        imgproc::cvt_color(frame, &mut gray, imgproc::COLOR_BGR2GRAY, 0)?;

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
        use std::{sync::mpsc, thread, time::Instant};
        use opencv::{prelude::*, videoio, core};

        let mut cap = videoio::VideoCapture::new(0, videoio::CAP_ANY)
            .map_err(|_| opencv::Error::new(core::StsError, "Failed to open webcam"))
            .map_err(|e| e.to_string())?;

        let mut detector = FaceDetector::new("src/detection/models/haarcascade_eye.xml")
            .map_err(|e| e.to_string())?;

        let mut blink_counter = 0;
        let mut prev_eyes_count = 0;
        let mut start_time = Instant::now();
        let mut last_blink_time = Instant::now();

        let (tx, rx): (mpsc::Sender<String>, mpsc::Receiver<String>) = mpsc::channel();
        let alert_thread = thread::spawn(move || {
            while let Ok(message) = rx.recv() {
                println!("Alert: {}", message);
            }
        });

        let mut frame = Mat::default(); // Reusable frame buffer

        loop {
            cap.read(&mut frame)
                .map_err(|e| e.to_string())?;

            if frame.empty() {
                eprintln!("Empty frame captured. Exiting...");
                break;
            }

            let eyes = detector.detect_eyes(&frame)
                .map_err(|e| e.to_string())?;
            let current_eyes = eyes.len();

            // Blink detection logic
            if prev_eyes_count == 2 && current_eyes < 2 {
                if last_blink_time.elapsed().as_millis() > 100 {
                    blink_counter += 1;
                    last_blink_time = Instant::now();
                }
            }

            if start_time.elapsed().as_secs() >= 10 {
                let blink_entry = IntervalEntry {
                    blink_count: blink_counter,
                    timestamp: chrono::Utc::now().naive_utc(),
                };

                // Insert blink data into DB
                if let Err(e) = db_handler.insert_interval(blink_entry) {
                    eprintln!("Error inserting blink data into DB: {}", e);
                }

                start_time = Instant::now();
                blink_counter = 0;
            }

            prev_eyes_count = current_eyes;
            println!("Blinks: {} | Time: {}s", blink_counter, start_time.elapsed().as_secs());
        }

        Ok::<(), String>(())
    });

    Ok(())
}
