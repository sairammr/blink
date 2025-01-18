fn main() {
    println!("cargo:rustc-link-search=nativeC:/tools/opencv/build/x64/vc16/bin");
    tauri_build::build()
}
