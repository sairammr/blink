# Tauri + React

This template should help get you started developing with Tauri and React in Vite.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

---

## Building & Packaging

This project is designed to bundle the Python backend executable (`blink.exe`) into the final installer. The recommended steps are:

1. Build the Python exe and copy into `src-tauri/bin`:
   - `npm run build:py` (cross-platform script; uses PowerShell on Windows and bash on Unix)
2. Build the frontend:
   - `npm run build:frontend`
3. Build Tauri installer:
   - `npm run tauri:build`

There is also a GitHub Actions workflow `.github/workflows/windows-build.yml` that performs these steps on `windows-latest` and uploads the resulting installer artifacts.
