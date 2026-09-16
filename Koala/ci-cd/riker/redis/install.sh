#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    fedora)
        PACKAGES="git
            gcc
            make
            pkgconf
            tcl"
        sudo dnf makecache
        ;;
    macos)
        # git/gcc/make's roles are filled by Xcode Command Line Tools.
        PACKAGES="pkg-config
            tcl-tk"
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        ;;
    *)
        PACKAGES="git
            gcc
            make
            pkg-config
            tcl"
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
