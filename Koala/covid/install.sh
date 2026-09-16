#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        pkgs="coreutils curl gzip gawk sed git"

        sudo apt-get update

        for pkg in $pkgs; do
            if ! dpkg -s "$pkg" >/dev/null 2>&1; then
                sudo apt-get install --no-install-recommends -y "$pkg"
            fi
        done
        ;;
    macos)
        # coreutils/gawk/sed come from the PATH shim (main.sh)
        brew install curl gzip git
        ;;
    fedora)
        pkgs="coreutils curl gzip gawk sed git"

        sudo dnf makecache

        for pkg in $pkgs; do
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
        done
        ;;
esac
