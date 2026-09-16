#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        pkgs="wget bsdmainutils file dos2unix grep findutils mawk"

        sudo apt-get update

        for pkg in $pkgs; do
            if ! dpkg -s "$pkg" >/dev/null 2>&1; then
                sudo apt-get install -y --no-install-recommends "$pkg"
            fi
        done
        ;;
    macos)
        # grep/findutils come from the PATH shim (main.sh); bsdmainutils tools
        # ship natively on macOS.
        brew install wget file dos2unix mawk
        ;;
    fedora)
        pkgs="wget util-linux file dos2unix grep findutils mawk perl-Digest-SHA"

        sudo dnf makecache

        for pkg in $pkgs; do
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
        done
        ;;
esac
