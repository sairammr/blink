#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod detection;
use detection::blink_detection::blink_detection;

fn main() {
    tauri::Builder::default()
        .setup(|_app| {
            // Execute blink_detection in the background
            std::thread::spawn(move || {
                if let Err(e) = blink_detection() {
                    eprintln!("Error in blink_detection: {}", e);
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![blink_detection]) // Still expose the command for frontend use if needed
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}
