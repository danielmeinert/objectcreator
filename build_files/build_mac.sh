#!/bin/bash
# Builds "Object Creator.app" and a drag-to-install "Object Creator.dmg" for macOS.
#
# Usage (from anywhere):  ./build_files/build_mac.sh
# Requirements: python3 (3.10+) on PATH, or set PYTHON=/path/to/python3
#               The app is built for the architecture of that Python, so an Intel build can be
#               made on Apple Silicon with an x86_64 Python (runs via Rosetta), e.g.
#               PYTHON="$(uv python find cpython-3.13-macos-x86_64-none)" ./build_files/build_mac.sh
# Output:       dist/<arch>/Object Creator.app  and  dist/Object Creator-<version>-macOS-<arch>.dmg

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
ARCH="$("$PYTHON" -c 'import platform; print(platform.machine())')"
BUILD="$REPO/build/mac-$ARCH"
DIST="$REPO/dist"
APP_NAME="Object Creator"
BUNDLE_ID="com.github.danielmeinert.objectcreator"

VERSION="$(sed -n "s/^VERSION = '\(.*\)'/\1/p" "$REPO/editor_app/app.py")"
SHORT_VERSION="${VERSION#v}"

echo "==> Building $APP_NAME $VERSION for $ARCH"
rm -rf "$BUILD" "$DIST/$ARCH/$APP_NAME.app"
mkdir -p "$BUILD" "$DIST/$ARCH"

echo "==> Creating build environment"
"$PYTHON" -m venv "$BUILD/venv"
VENV_PY="$BUILD/venv/bin/python"
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet numpy pyqt5 pillow requests pyinstaller \
    "$REPO/customwidgets" "$REPO/rctobject"

echo "==> Packing path generator templates"
"$VENV_PY" - "$REPO/editor_app/pathgenerator/templates_raw" "$BUILD/templates" <<'EOF'
import os, sys, shutil
raw, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for name in sorted(next(os.walk(raw))[1]):
    if name.endswith('wip'):
        continue
    shutil.make_archive(os.path.join(out, name), 'zip', root_dir=os.path.join(raw, name))
    os.replace(os.path.join(out, f'{name}.zip'), os.path.join(out, f'{name}.template'))
EOF

echo "==> Creating app icon"
ICONSET="$BUILD/icon.iconset"
mkdir -p "$ICONSET"
for size in 16 32 128 256 512; do
    sips -z $size $size "$REPO/editor_app/gui/icon.png" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    double=$((size * 2))
    sips -z $double $double "$REPO/editor_app/gui/icon.png" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$BUILD/icon.icns"

echo "==> Running PyInstaller"
cd "$REPO/editor_app"
"$VENV_PY" -m PyInstaller --noconfirm --clean --windowed \
    --name "$APP_NAME" \
    --icon "$BUILD/icon.icns" \
    --osx-bundle-identifier "$BUNDLE_ID" \
    --workpath "$BUILD/pyinstaller" \
    --specpath "$BUILD" \
    --distpath "$BUILD/dist" \
    --add-data "$REPO/editor_app/gui:gui" \
    --add-data "$REPO/editor_app/res:res" \
    --add-data "$REPO/editor_app/pathgenerator/gui:pathgenerator/gui" \
    --add-data "$REPO/editor_app/pathgenerator/res:pathgenerator/res" \
    --add-data "$BUILD/templates:pathgenerator/templates" \
    --collect-data customwidgets \
    --collect-data rctobject \
    --hidden-import PyQt5.uic \
    --exclude-module tkinter \
    app.py

APP="$BUILD/dist/$APP_NAME.app"
PLIST="$APP/Contents/Info.plist"

echo "==> Updating Info.plist"
plutil -replace CFBundleShortVersionString -string "$SHORT_VERSION" "$PLIST"
plutil -replace CFBundleVersion -string "$SHORT_VERSION" "$PLIST"
plutil -replace NSHighResolutionCapable -bool YES "$PLIST"
# Qt5 renders unreadable light-on-light text in Dark Mode, so always use the light appearance
plutil -replace NSRequiresAquaSystemAppearance -bool YES "$PLIST"
plutil -replace LSMinimumSystemVersion -string "11.0" "$PLIST"
plutil -replace NSHumanReadableCopyright -string "GPL-3.0, see licence.txt" "$PLIST"
# Let Finder open .parkobj files with Object Creator
plutil -replace CFBundleDocumentTypes -json '[{
    "CFBundleTypeName": "OpenRCT2 Object",
    "CFBundleTypeRole": "Editor",
    "LSHandlerRank": "Alternate",
    "CFBundleTypeExtensions": ["parkobj"],
    "CFBundleTypeIconFile": "icon.icns"
}]' "$PLIST"

echo "==> Signing (ad-hoc)"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"

mv "$APP" "$DIST/$ARCH/"

echo "==> Creating disk image"
DMG="$DIST/$APP_NAME-$VERSION-macOS-$ARCH.dmg"
STAGE="$BUILD/dmg"
rm -rf "$STAGE" "$DMG"
mkdir -p "$STAGE"
cp -R "$DIST/$ARCH/$APP_NAME.app" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
cp "$REPO/build_files/mac_first_open.txt" "$STAGE/How to open (read me first).txt"
hdiutil create -quiet -volname "$APP_NAME" -srcfolder "$STAGE" -ov -format UDZO "$DMG"

echo
echo "Done:"
echo "  $DIST/$ARCH/$APP_NAME.app"
echo "  $DMG"
