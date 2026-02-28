#!/bin/bash
set -e

echo "=== SlideAlchemy Full Build ==="

PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
echo "Platform: $PLATFORM"

# Step 1: Build Python backend
echo ""
echo "--- Building Python backend ---"
cd backend
python build.py
cd ..

# Step 2: Copy binary to Tauri sidecar location
echo ""
echo "--- Copying backend binary to Tauri ---"
mkdir -p src-tauri/binaries

ARCH=$(uname -m)
case "$PLATFORM" in
    darwin)
        if [ "$ARCH" = "arm64" ]; then
            TARGET="aarch64-apple-darwin"
        else
            TARGET="x86_64-apple-darwin"
        fi
        cp backend/dist/slide-alchemy-backend "src-tauri/binaries/slide-alchemy-backend-$TARGET"
        ;;
    linux)
        TARGET="x86_64-unknown-linux-gnu"
        cp backend/dist/slide-alchemy-backend "src-tauri/binaries/slide-alchemy-backend-$TARGET"
        ;;
    *)
        TARGET="x86_64-pc-windows-msvc"
        cp backend/dist/slide-alchemy-backend.exe "src-tauri/binaries/slide-alchemy-backend-$TARGET.exe"
        ;;
esac

echo "Backend binary: src-tauri/binaries/slide-alchemy-backend-$TARGET"

# Step 3: Build Tauri app
echo ""
echo "--- Building Tauri app ---"
npm run tauri build

echo ""
echo "=== Build complete! ==="
echo "Check src-tauri/target/release/bundle/ for the installer."
