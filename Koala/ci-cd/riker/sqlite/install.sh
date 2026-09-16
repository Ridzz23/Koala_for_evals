#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    fedora)
        PACKAGES="git
            gcc
            tcl
            libtool
            readline-devel
            tcl-devel"
        sudo dnf makecache
        ;;
    macos)
        # git/gcc's roles are filled by Xcode Command Line Tools. readline
        # headers ship with the Xcode SDK too.
        PACKAGES="tcl-tk
            libtool"
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        ;;
    *)
        PACKAGES="git
            gcc
            tcl8.6
            libtool
            libreadline-dev
            tcl8.6-dev"
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
