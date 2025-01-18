use std::{sync::{Arc, atomic::{AtomicBool, Ordering}}};
mod detection;
mod db;
use db::init::{DBHandler, IntervalEntry};
use detection::blink_detection::blink_detection;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct AvgEntryResponse {
    start_time: String,
    end_time: String,
    avg_value: i32,
}


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
        .invoke_handler(tauri::generate_handler![get_avg])
        .on_window_event(move |_app_handle, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                should_stop.store(true, Ordering::SeqCst);
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}

#[tauri::command]
async fn get_avg(db_handler: tauri::State<'_, Arc<DBHandler>>) -> Result<String, String> {
    match db_handler.calculate_avg() {
        Ok(entries) => {
            let response = entries
                .iter()
                .map(|entry| AvgEntryResponse {
                    start_time: entry.start_time.clone().to_string(),
                    end_time: entry.end_time.clone().to_string(),
                    avg_value: entry.avg_value,
                })
                .collect::<Vec<AvgEntryResponse>>();

            match serde_json::to_string(&response) {
                Ok(json) => Ok(json),
                Err(e) => Err(format!("Failed to serialize data: {}", e)),
            }
        }
        Err(e) => {
            Err(format!("Failed to fetch average data: {}", e))
        }
    }
}