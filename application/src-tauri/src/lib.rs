// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::path::PathBuf;
use once_cell::sync::Lazy;
use tauri::api::path::resource_dir;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

// Global holder for the spawned Python process
static CHILD_PROCESS: Lazy<Mutex<Option<Child>>> = Lazy::new(|| Mutex::new(None));

fn find_blink_exe() -> Option<PathBuf> {
    let exe_name = if cfg!(windows) { "blink.exe" } else { "blink" };

    // 1) Resource dir (when bundled)
    if let Some(dir) = resource_dir() {
        let p = dir.join("bin").join(exe_name);
        if p.exists() {
            return Some(p);
        }
    }

    // 2) Next to the running executable
    if let Ok(cur) = std::env::current_exe() {
        if let Some(parent) = cur.parent() {
            let p = parent.join("bin").join(exe_name);
            if p.exists() {
                return Some(p);
            }
        }
    }

    // 3) Repo layout (useful for dev)
    if let Ok(cur) = std::env::current_dir() {
        let p = cur.join("src-tauri").join("bin").join(exe_name);
        if p.exists() {
            return Some(p);
        }
        let p2 = cur.join("bin").join(exe_name);
        if p2.exists() {
            return Some(p2);
        }
    }

    None
}

#[tauri::command]
fn start_python() -> Result<u32, String> {
    let mut guard = CHILD_PROCESS.lock().map_err(|_| "process lock poisoned".to_string())?;

    if guard.is_some() {
        return Err("Process already running".into());
    }

    let exe = find_blink_exe().ok_or_else(|| "blink executable not found".to_string())?;

    let child = Command::new(exe)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to spawn process: {}", e))?;

    let pid = child.id();
    *guard = Some(child);
    Ok(pid)
}

#[tauri::command]
fn stop_python() -> Result<(), String> {
    let mut guard = CHILD_PROCESS.lock().map_err(|_| "process lock poisoned".to_string())?;

    if let Some(mut child) = guard.take() {
        let pid = child.id();
        // try graceful kill
        if let Err(e) = child.kill() {
            eprintln!("child.kill() failed: {}", e);
        }
        let _ = child.wait();

        // On Windows, ensure entire process tree is terminated as a fallback
        #[cfg(windows)]
        {
            let _ = Command::new("taskkill")
                .args(["/PID", &pid.to_string(), "/T", "/F"])
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn();
        }

        return Ok(());
    }

    Err("Process not running".into())
}

#[tauri::command]
fn get_python_pid() -> Option<u32> {
    CHILD_PROCESS.lock().ok().and_then(|g| g.as_ref().map(|c| c.id()))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, start_python, stop_python, get_python_pid])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
