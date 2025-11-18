#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PKGDIR="$ROOT_DIR/dist/svt-deb"
rm -rf "$PKGDIR"
mkdir -p "$PKGDIR/DEBIAN" "$PKGDIR/usr/share/svt"
cp -R "$ROOT_DIR" "$PKGDIR/usr/share/svt"
cat > "$PKGDIR/DEBIAN/control" <<'CTRL'
Package: svt
Version: 1.0
Section: sound
Priority: optional
Architecture: amd64
Maintainer: SVT Team <support@example.com>
Description: Semantic Voice Transcriber (local-first build)
CTRL
cat > "$PKGDIR/DEBIAN/postinst" <<'POST'
#!/bin/bash
cd /usr/share/svt
./svt_env/bin/python3 scripts/setup_local_stack.py --env /usr/share/svt/.env --overwrite-env || true
POST
chmod 755 "$PKGDIR/DEBIAN/postinst"
echo "Run dpkg-deb --build dist/svt-deb to create package"
