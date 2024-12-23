use std::{sync::{Arc, atomic::{AtomicBool, Ordering}}};
mod detection;
mod db;
use db::init::{DBHandler, IntervalEntry, LogEntry, AvgEntry};
use detection::blink_detection::blink_detection;
fn main() {
    let db_path = "../../../../agarwal.sqlite"; // Path to SQLite database file
    let db_handler = Arc::new(DBHandler::new(db_path));

    let should_stop = Arc::new(AtomicBool::new(false)); 
    let stop_signal = should_stop.clone();

    tauri::Builder::default()
        .manage(db_handler.clone())
        .setup(move |_app| {
            std::thread::spawn(move || {
                while !stop_signal.load(Ordering::SeqCst) {
                    if let Err(e) = blink_detection(db_handler.clone()) {
                        eprintln!("Error in blink_detection: {}", e);
                    }
                    std::thread::sleep(std::time::Duration::from_secs(1)); // Sleep for 1 second before retrying
                }
                println!("Background task stopped.");
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![])
        .on_window_event(move |_app_handle, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                should_stop.store(true, Ordering::SeqCst);
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}
