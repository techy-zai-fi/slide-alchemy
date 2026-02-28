use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use std::sync::Mutex;

struct BackendState {
    port: u16,
}

#[tauri::command]
fn get_backend_port(state: tauri::State<Mutex<BackendState>>) -> u16 {
    state.lock().unwrap().port
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port: u16 = portpicker::pick_unused_port().unwrap_or(8741);

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Mutex::new(BackendState { port }))
        .setup(move |app| {
            // Spawn the Python backend sidecar
            let shell = app.shell();
            let sidecar = shell
                .sidecar("slide-alchemy-backend")
                .expect("failed to create sidecar")
                .args(&[
                    "--port", &port.to_string(),
                    "--host", "127.0.0.1",
                ]);

            let (mut _rx, _child) = sidecar.spawn().expect("failed to spawn sidecar");

            println!("Backend started on port {}", port);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_backend_port])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
