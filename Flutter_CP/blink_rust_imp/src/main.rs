use opencv::{
    core::{self, Vector},
    objdetect,
    prelude::*,
    videoio,
    imgproc,
    Result,
};
use std::{sync::mpsc, thread, time::Instant};

struct FaceDetector {
    eye_cascade: objdetect::CascadeClassifier,
}

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

fn main() -> Result<()> {
    let mut cap = videoio::VideoCapture::new(0, videoio::CAP_ANY)
        .map_err(|_| opencv::Error::new(opencv::core::StsError, "Failed to open webcam"))?;
    let mut detector = FaceDetector::new("src/haarcascade_eye.xml")?;

    let mut blink_counter = 0;
    let mut prev_eyes_count = 0;
    let start_time = Instant::now();
    let mut last_blink_time = Instant::now();

    let (tx, rx): (mpsc::Sender<String>, mpsc::Receiver<String>) = mpsc::channel();
    let alert_thread = thread::spawn(move || {
        while let Ok(message) = rx.recv() {
            println!("Alert: {}", message);
        }
    });

    let mut frame = Mat::default(); // Reusable frame buffer

    loop {
        cap.read(&mut frame)?;
        if frame.empty() {
            eprintln!("Empty frame captured. Exiting...");
            break;
        }

        let eyes = detector.detect_eyes(&frame)?;
        let current_eyes = eyes.len();

        // Blink detection logic
        if prev_eyes_count == 2 && current_eyes < 2 {
            if last_blink_time.elapsed().as_millis() > 100 {
                blink_counter += 1;
                last_blink_time = Instant::now();
            }
        }
        prev_eyes_count = current_eyes;

        let elapsed_secs = start_time.elapsed().as_secs();
        println!("Blinks: {} | Time: {}s", blink_counter, elapsed_secs);
    }

    drop(tx);
    alert_thread.join().unwrap();

    Ok(())
}
