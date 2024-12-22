use std::{sync::{Arc, atomic::{AtomicBool, Ordering}}};

mod detection;
use detection::blink_detection::blink_detection;

fn main() {
    let should_stop = Arc::new(AtomicBool::new(false)); // make it truee to stop cv detection 
    let stop_signal = should_stop.clone();

    tauri::Builder::default()
    .setup(move |_app| {
        std::thread::spawn(move || {
            while !stop_signal.load(Ordering::SeqCst) {
                if let Err(e) = blink_detection() {
                    eprintln!("Error in blink_detection: {}", e);
                }
                std::thread::sleep(std::time::Duration::from_secs(1));
            }
            println!("Background task stopped.");
        });

        Ok(())
    })
    .invoke_handler(tauri::generate_handler![])
    .on_window_event(move |_app_handle, event| {
        if let tauri::WindowEvent::CloseRequested { .. } = event {
            should_stop.store(true, std::sync::atomic::Ordering::SeqCst);
        }
    })
    .run(tauri::generate_context!())
    .expect("error while running Tauri application");

}
