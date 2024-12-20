use opencv::{
    core::{self, Vector},
    objdetect,
    prelude::*,
    videoio,
    imgproc,
    Result,
};
use std::time::Instant;
use std::sync::mpsc;
use std::thread;

struct FaceDetector {
    eye_cascade: objdetect::CascadeClassifier,
}

impl FaceDetector {
    fn new() -> Result<Self> {
        let mut eye_cascade = objdetect::CascadeClassifier::new("src/haarcascade_eye.xml")?;
        eye_cascade.load("src/haarcascade_eye.xml")?;
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

fn main() -> Result<()> {
    let mut cap = videoio::VideoCapture::new(0, videoio::CAP_ANY)?;
    let mut detector = FaceDetector::new()?;

    let mut blink_counter = 0;
    let mut prev_eyes_count = 0;
    let start_time = Instant::now();
    let mut last_blink_time = Instant::now();

    let (tx, rx) = mpsc::channel();

    loop {
        let mut frame = Mat::default();
        cap.read(&mut frame)?;

        if frame.empty() {
            break;
        }

        let eyes = detector.detect_eyes(&frame)?;

        // Blink detection logic
        let current_eyes = eyes.len();
        if prev_eyes_count == 2 && current_eyes < 2 {
            if last_blink_time.elapsed().as_millis() > 100 {
                // Debounce blinks
                blink_counter += 1;
                last_blink_time = Instant::now();
            }
        }
        prev_eyes_count = current_eyes;

        // Display logs
        let elapsed_secs = start_time.elapsed().as_secs();
        println!("Blinks: {} | Time: {}s", blink_counter, elapsed_secs);

        // Calculate and check blink rate
        if elapsed_secs >= 60 {
            let blink_rate = blink_counter as f64 / (elapsed_secs as f64 / 60.0);
            if blink_rate < 17.0 {
                let message = format!("Your blink rate is too low: {:.2} blinks per minute!", blink_rate);
                tx.send(message).unwrap();
            }
        }

        // Check for alert messages
        if let Ok(message) = rx.try_recv() {
            thread::spawn(move || {
                println!("Alert: {}",message);
            });
        }

        // Stop after 2 minutes
        if elapsed_secs >= 120 {
            println!("Session completed! You blinked {} times in {} seconds!", blink_counter, elapsed_secs);
            break;
        }
    }

    Ok(())
}
