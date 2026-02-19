// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::path::PathBuf;
use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader};

//PID file

use std::fs;
use serde_json::Value;

fn get_config_path() -> PathBuf {
    #[cfg(target_os = "windows")]
    {
        let app_data = std::env::var("APPDATA").unwrap_or_else(|_| ".".to_string());
        PathBuf::from(app_data).join("blink").join("blink_config.json")
    }
    #[cfg(not(target_os = "windows"))]
    {
        let home = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
        PathBuf::from(home).join(".config").join("blink").join("blink_config.json")
    }
}

fn pid_file_path() -> PathBuf {
    std::env::temp_dir().join("tauri_blink.pid")
}

fn save_pid(pid: u32) {
    let _ = fs::write(pid_file_path(), pid.to_string());
}

fn load_pid() -> Option<u32> {
    fs::read_to_string(pid_file_path())
        .ok()
        .and_then(|s| s.trim().parse().ok())
}

fn clear_pid() {
    let _ = fs::remove_file(pid_file_path());
}


#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

// Global holder for the spawned Python process
static CHILD_PROCESS: Lazy<Mutex<Option<Child>>> = Lazy::new(|| Mutex::new(None));

fn find_blink_exe() -> Option<PathBuf> {
    let exe_name = if cfg!(windows) { "blink.exe" } else { "blink" };

    // 1) Next to the running executable (when bundled, resources are next to exe)
    if let Ok(cur) = std::env::current_exe() {
        if let Some(parent) = cur.parent() {
            let p = parent.join("bin").join(exe_name);
            if p.exists() {
                return Some(p);
            }
            // Also check directly in parent (for resources)
            let p2 = parent.join(exe_name);
            if p2.exists() {
                return Some(p2);
            }
        }
    }

    // 2) Repo layout (useful for dev)
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

//crash handling in case app crashes while and pid remains

fn is_process_alive(pid: u32) -> bool {
    #[cfg(windows)]
    {
        Command::new("tasklist")
            .arg("/FI")
            .arg(format!("PID eq {}", pid))
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).contains(&pid.to_string()))
            .unwrap_or(false)
    }

    #[cfg(unix)]
    {
        Command::new("kill")
            .arg("-0")
            .arg(pid.to_string())
            .status()
            .map(|s| s.success())
            .unwrap_or(false)
    }
}


#[tauri::command]
fn start_python() -> Result<u32, String> {
    let mut guard = CHILD_PROCESS
        .lock()
        .map_err(|_| "process lock poisoned".to_string())?;

    // Prevent double spawn (in-memory)
    if guard.is_some() {
        return Err("Process already running".into());
    }

    // Prevent double spawn (from stored PID)
    if let Some(pid) = load_pid() {
        if is_process_alive(pid) {
            return Err(format!("Process already running with PID {}", pid));
        } else {
            clear_pid(); // stale corpse removed
        }
    }


    let python_exe = find_python_exe()
        .ok_or_else(|| "Embedded Python executable not found".to_string())?;

    let blink_script = find_blink_py()
        .ok_or_else(|| "blink.py not found".to_string())?;

    let working_dir = blink_script
        .parent()
        .ok_or_else(|| "Could not determine blink.py directory".to_string())?;

    eprintln!("[DEBUG] Python exe: {}", python_exe.display());
    eprintln!("[DEBUG] blink.py script: {}", blink_script.display());
    eprintln!("[DEBUG] Working directory: {}", working_dir.display());

    let mut cmd = Command::new(&python_exe);
    cmd.arg(&blink_script)
        .current_dir(working_dir)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Hide console window on Windows
    #[cfg(windows)]
    {
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;

    let pid = child.id();

    // 🧠 Persist the PID
    save_pid(pid);

    // Drain stdout
    if let Some(stdout) = child.stdout.take() {
        std::thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines().flatten() {
                eprintln!("[Python stdout] {}", line);
            }
        });
    }

    // Drain stderr
    if let Some(stderr) = child.stderr.take() {
        std::thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().flatten() {
                eprintln!("[Python stderr] {}", line);
            }
        });
    }

    *guard = Some(child);

    Ok(pid)
}


#[tauri::command]
fn stop_python() -> Result<(), String> {
    // First try in-memory process
    if let Ok(mut guard) = CHILD_PROCESS.lock() {
        if let Some(mut child) = guard.take() {
            let pid = child.id();
            let _ = child.kill();
            let _ = child.wait();
            clear_pid();
            return Ok(());
        }
    }

    // Fallback: kill from stored PID
    if let Some(pid) = load_pid() {
        #[cfg(windows)]
        {
            Command::new("taskkill")
                .args(["/PID", &pid.to_string(), "/T", "/F"])
                .spawn()
                .map_err(|e| e.to_string())?;
        }

        #[cfg(unix)]
        {
            Command::new("kill")
                .arg("-9")
                .arg(pid.to_string())
                .spawn()
                .map_err(|e| e.to_string())?;
        }

        clear_pid();
        return Ok(());
    }

    Err("No running Python process found".into())
}


#[tauri::command]
fn get_python_pid() -> Option<u32> {
    if let Ok(guard) = CHILD_PROCESS.lock() {
        if let Some(child) = guard.as_ref() {
            return Some(child.id());
        }
    }
    load_pid()
}


#[tauri::command]
fn debug_paths() -> String {
    let mut info = String::new();
    
    info.push_str("=== Path Debug Info ===\n\n");
    
    if let Ok(cur_exe) = std::env::current_exe() {
        info.push_str(&format!("Current executable: {}\n", cur_exe.display()));
        if let Some(parent) = cur_exe.parent() {
            info.push_str(&format!("Executable parent: {}\n", parent.display()));
            let python_path = parent.join("python-3.10.4-embed-amd64").join("python.exe");
            info.push_str(&format!("Python path (exe parent): {} (exists: {})\n", 
                python_path.display(), python_path.exists()));
            let python_path_up = parent.join("_up_").join("python-3.10.4-embed-amd64").join("python.exe");
            info.push_str(&format!("Python path (exe parent/_up_): {} (exists: {})\n", 
                python_path_up.display(), python_path_up.exists()));
        }
    }
    
    if let Ok(cur_dir) = std::env::current_dir() {
        info.push_str(&format!("\nCurrent directory: {}\n", cur_dir.display()));
        let python_path1 = cur_dir.join("python-3.10.4-embed-amd64").join("python.exe");
        info.push_str(&format!("Python path (cur dir): {} (exists: {})\n", 
            python_path1.display(), python_path1.exists()));
        let python_path2 = cur_dir.join("application").join("python-3.10.4-embed-amd64").join("python.exe");
        info.push_str(&format!("Python path (application): {} (exists: {})\n", 
            python_path2.display(), python_path2.exists()));
    }
    
    info.push_str(&format!("\nFound Python: {:?}\n", find_python_exe()));
    info.push_str(&format!("Found blink.py: {:?}\n", find_blink_py()));
    
    info
}

fn find_python_exe() -> Option<PathBuf> {
    let exe_name = if cfg!(windows) { "python.exe" } else { "python3" };
    let dir_name = "python-3.10.4-embed-amd64";

    // 1) Next to the running executable (when bundled, resources are next to exe)
    if let Ok(cur) = std::env::current_exe() {
        if let Some(parent) = cur.parent() {
            let p: PathBuf = parent.join(dir_name).join(exe_name);
            if p.exists() {
                return Some(p);
            }
            // Check in _up_ directory (NSIS/AppImage/etc specific)
            let p_up: PathBuf = parent.join("_up_").join(dir_name).join(exe_name);
            if p_up.exists() {
                return Some(p_up);
            }
        }
    }

    // 2) Current working directory (for dev mode)
    if let Ok(cur) = std::env::current_dir() {
        // Check directly in current dir
        let p: PathBuf = cur.join(dir_name).join(exe_name);
        if p.exists() {
            return Some(p);
        }
        // Check in application subdirectory
        let p2: PathBuf = cur.join("application").join(dir_name).join(exe_name);
        if p2.exists() {
            return Some(p2);
        }
        // Check if we're in src-tauri, go up to application
        if cur.ends_with("src-tauri") {
            let p3: PathBuf = cur.parent()
                .and_then(|p| Some(p.join(dir_name).join(exe_name)))
                .unwrap_or_default();
            if p3.exists() {
                return Some(p3);
            }
        }
        // Check if we're in application/src-tauri
        if cur.ends_with("application/src-tauri") || cur.ends_with("application\\src-tauri") {
            let p4: PathBuf = cur.parent()
                .and_then(|p| p.parent())
                .and_then(|p| Some(p.join(dir_name).join(exe_name)))
                .unwrap_or_default();
            if p4.exists() {
                return Some(p4);
            }
        }
    }

    None
}

fn find_blink_py() -> Option<PathBuf> {
    let script_name = "blink.py";

    // 1) Next to the running executable (when bundled, resources are next to exe)
    if let Ok(cur) = std::env::current_exe() {
        if let Some(parent) = cur.parent() {
            let p: PathBuf = parent.join(script_name);
            if p.exists() {
                return Some(p);
            }
            // Check in _up_ directory
            let p_up: PathBuf = parent.join("_up_").join(script_name);
            if p_up.exists() {
                return Some(p_up);
            }
        }
    }

    // 2) Current working directory (for dev mode)
    if let Ok(cur) = std::env::current_dir() {
        // Check directly in current dir
        let p: PathBuf = cur.join(script_name);
        if p.exists() {
            return Some(p);
        }
        // Check in application subdirectory
        let p2: PathBuf = cur.join("application").join(script_name);
        if p2.exists() {
            return Some(p2);
        }
        // Check if we're in src-tauri, go up to application
        if cur.ends_with("src-tauri") || cur.ends_with("src-tauri\\") || cur.ends_with("src-tauri/") {
            if let Some(parent) = cur.parent() {
                let p3: PathBuf = parent.join(script_name);
                if p3.exists() {
                    return Some(p3);
                }
            }
        }
        // Check if we're in application/src-tauri
        if cur.ends_with("application/src-tauri") || cur.ends_with("application\\src-tauri") {
            if let Some(app_dir) = cur.parent().and_then(|p| p.parent()) {
                let p4: PathBuf = app_dir.join(script_name);
                if p4.exists() {
                    return Some(p4);
                }
            }
        }
    }

    None
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonExecutionResult {
    pub success: bool,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
}

#[tauri::command]
fn run_python_file(
    file_path: String,
    args: Option<Vec<String>>,
) -> Result<PythonExecutionResult, String> {
    let python_exe = find_python_exe()
        .ok_or_else(|| "Embedded Python executable not found".to_string())?;

    let script_path = PathBuf::from(&file_path);
    if !script_path.exists() {
        return Err(format!("Python file not found: {}", file_path));
    }

    let mut cmd = Command::new(python_exe);
    cmd.arg(&script_path);

    if let Some(ref script_args) = args {
        cmd.args(script_args);
    }

    let output = cmd
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    Ok(PythonExecutionResult {
        success: output.status.success(),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code: output.status.code(),
    })
}

#[tauri::command]
fn run_python_code(code: String) -> Result<PythonExecutionResult, String> {
    let python_exe = find_python_exe()
        .ok_or_else(|| "Embedded Python executable not found".to_string())?;

    let mut cmd = Command::new(python_exe);
    cmd.arg("-c").arg(&code);

    let output = cmd
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to execute Python code: {}", e))?;

    Ok(PythonExecutionResult {
        success: output.status.success(),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code: output.status.code(),
    })
}

#[tauri::command]
fn update_sensitivity(value: u32) -> Result<(), String> {
    // 1. If backend is running, persist threshold to MongoDB via POST /config
    let body = serde_json::json!({ "threshold": value });
    let _ = reqwest::blocking::Client::new()
        .post("http://127.0.0.1:9783/config")
        .json(&body)
        .send();

    // 2. Stop the Python process
    let _ = stop_python();

    // 3. Restart Python process (will load threshold from Mongo on startup)
    start_python().map_err(|e| format!("Failed to restart Python: {}", e))?;

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            start_python,
            stop_python,
            get_python_pid,
            run_python_file,
            run_python_code,
            debug_paths,
            update_sensitivity
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
