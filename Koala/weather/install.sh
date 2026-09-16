#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update

        pkgs="curl wget unzip coreutils gzip gawk sed findutils git python3 python3-pip python3-venv"

        for pkg in $pkgs; do
            if ! dpkg -l | grep -q "$pkg"; then
                sudo apt-get install -y --no-install-recommends "$pkg"
            fi
        done
        ;;
    macos)
        # coreutils/gawk/sed/findutils come from the PATH shim (main.sh)
        brew install curl wget unzip gzip git python3
        ;;
    fedora)
        sudo dnf makecache

        # python3-venv is included with python3 on Fedora
        pkgs="curl wget unzip coreutils gzip gawk sed findutils git python3 python3-pip"

        for pkg in $pkgs; do
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
        done
        ;;
esac

pip install --break-system-packages --upgrade pip

pip install --break-system-packages \
    numpy \
    matplotlib