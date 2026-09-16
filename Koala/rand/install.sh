#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update
        sudo apt-get install -y wget coreutils unzip
        ;;
    macos)
        # coreutils comes from the PATH shim (main.sh)
        brew install wget unzip
        ;;
    fedora)
        sudo dnf makecache
        sudo dnf install -y wget coreutils unzip
        ;;
esac
