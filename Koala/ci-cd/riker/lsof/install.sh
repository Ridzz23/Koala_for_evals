#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    fedora)
        PACKAGES="gcc
libtirpc-devel"
        sudo dnf makecache
        ;;
    macos)
        # libtirpc is glibc-specific; macOS's BSD libc ships its own rpc
        # headers natively. gcc's role is filled by Xcode Command Line Tools.
        PACKAGES=""
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        ;;
    *)
        PACKAGES="gcc
libtirpc-dev"
        sudo apt-get update
        ;;
esac

for pkg in $PACKAGES; do
    case "$OS" in
        fedora)
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
            ;;
        macos)
            brew install "$pkg"
            ;;
        *)
            if ! dpkg -l | grep -q "^ii\s\+$pkg\s"; then
                sudo apt-get install -y --no-install-recommends "$pkg"
            fi
            ;;
    esac
done
