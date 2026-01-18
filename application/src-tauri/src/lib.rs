// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::path::PathBuf;
use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader};

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

#[tauri::command]
fn start_python() -> Result<u32, String> {
    let mut guard = CHILD_PROCESS.lock().map_err(|_| "process lock poisoned".to_string())?;

    if guard.is_some() {
        return Err("Process already running".into());
    }

    let python_exe = find_python_exe()
        .ok_or_else(|| {
            let mut msg = "Embedded Python executable not found. Searched in:\n".to_string();
            if let Ok(cur) = std::env::current_exe() {
                if let Some(parent) = cur.parent() {
                    msg.push_str(&format!("  - {}\n", parent.join("python-3.10.4-embed-amd64").join("python.exe").display()));
                    msg.push_str(&format!("  - {}\n", parent.join("_up_").join("python-3.10.4-embed-amd64").join("python.exe").display()));
                }
            }
            if let Ok(cur) = std::env::current_dir() {
                msg.push_str(&format!("  - {}\n", cur.join("python-3.10.4-embed-amd64").join("python.exe").display()));
                msg.push_str(&format!("  - {}\n", cur.join("application").join("python-3.10.4-embed-amd64").join("python.exe").display()));
            }
            msg.push_str(&format!("Current dir: {:?}\n", std::env::current_dir()));
            msg.push_str(&format!("Current exe: {:?}", std::env::current_exe()));
            msg
        })?;
    
    let blink_script = find_blink_py()
        .ok_or_else(|| {
            let mut msg = "blink.py not found. Searched in:\n".to_string();
            if let Ok(cur) = std::env::current_exe() {
                if let Some(parent) = cur.parent() {
                    msg.push_str(&format!("  - {}\n", parent.join("blink.py").display()));
                    msg.push_str(&format!("  - {}\n", parent.join("_up_").join("blink.py").display()));
                }
            }
            if let Ok(cur) = std::env::current_dir() {
                msg.push_str(&format!("  - {}\n", cur.join("blink.py").display()));
                msg.push_str(&format!("  - {}\n", cur.join("application").join("blink.py").display()));
            }
            msg.push_str(&format!("Current dir: {:?}\n", std::env::current_dir()));
            msg
        })?;

    // Get the directory containing blink.py for working directory
    let working_dir = blink_script.parent()
        .ok_or_else(|| "Could not determine blink.py directory".to_string())?;

    // Debug logging
    eprintln!("[DEBUG] Python exe: {}", python_exe.display());
    eprintln!("[DEBUG] blink.py script: {}", blink_script.display());
    eprintln!("[DEBUG] Working directory: {}", working_dir.display());

    let mut cmd = Command::new(&python_exe);
    cmd.arg(&blink_script)
        .current_dir(working_dir)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // On Windows, hide the console window
    #[cfg(windows)]
    {
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn Python process: {} (Python: {}, Script: {})", e, python_exe.display(), blink_script.display()))?;

    let pid = child.id();

    // Consume stdout and stderr in background threads to prevent pipe blocking
    if let Some(stdout) = child.stdout.take() {
        std::thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(line) = line {
                    eprintln!("[Python stdout] {}", line);
                }
            }
        });
    }

    if let Some(stderr) = child.stderr.take() {
        std::thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines() {
                if let Ok(line) = line {
                    eprintln!("[Python stderr] {}", line);
                }
            }
        });
    }

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
            debug_paths
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
