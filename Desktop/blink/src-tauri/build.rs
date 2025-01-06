fn main() {
    println!("cargo:rustc-link-search=native=C:\\tools\\opencv\\build\\x64\\vc15\\lib"); // Adjust path
    println!("cargo:rustc-link-lib=static=opencv_world4100");
    tauri_build::build()
}
