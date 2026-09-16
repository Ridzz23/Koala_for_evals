#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    fedora)
        PACKAGES="git
            gcc
            make
            ncurses-devel
            libSM-devel
            libICE-devel
            libXt-devel
            libX11-devel
            libXdmcp-devel
            libselinux-devel"
        sudo dnf makecache
        ;;
    macos)
        # git/gcc/make's roles are filled by Xcode Command Line Tools; ncurses
        # headers ship with the Xcode SDK. X11 libs and libselinux have no
        # macOS equivalent; this benchmark builds vim console-only anyway.
        PACKAGES=""
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        ;;
    *)
        PACKAGES="git
            gcc
            make
            libncurses-dev
            libsm-dev
            libice-dev
            libxt-dev
            libx11-dev
            libxdmcp-dev
            libselinux-dev"
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
