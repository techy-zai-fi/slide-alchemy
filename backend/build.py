"""Build the FastAPI backend into a standalone binary using PyInstaller."""
import platform
import subprocess
import sys

def build():
    system = platform.system().lower()
    binary_name = "slide-alchemy-backend"
    if system == "windows":
        binary_name += ".exe"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", binary_name,
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "app.routers.resources",
        "--hidden-import", "app.routers.chat",
        "--hidden-import", "app.routers.settings",
        "--hidden-import", "app.routers.research",
        "--hidden-import", "app.routers.slides",
        "--hidden-import", "app.routers.notebooklm",
        "--hidden-import", "app.routers.feedback",
        "--collect-all", "notebooklm",
        "app/main.py",
    ]

    print(f"Building {binary_name} for {system}...")
    subprocess.run(cmd, check=True)
    print(f"Build complete: dist/{binary_name}")

if __name__ == "__main__":
    build()
