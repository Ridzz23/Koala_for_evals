#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update -y

        sudo apt-get install -y \
            coreutils \
            build-essential \
            git \
            curl \
            wget \
            bzip2 \
            gpg \
            tar \
            coreutils \
            sed \
            gawk \
            git \
            autoconf \
            automake \
            build-essential \
            python3 \
            python3-pip \
            python3-venv \
            ncurses-bin \
            ca-certificates \
            zsh
        ;;
    macos)
        # coreutils/sed/gawk come from the PATH shim (main.sh).
        # ncurses-bin (tput/tic/infocmp) and zsh ship with the base OS already.
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        brew install git curl wget bzip2 gnupg gnu-tar autoconf automake python3 ca-certificates
        ;;
    fedora)
        sudo dnf makecache

        sudo dnf install -y \
            coreutils \
            gcc \
            gcc-c++ \
            make \
            git \
            curl \
            wget \
            bzip2 \
            gpg \
            tar \
            sed \
            gawk \
            autoconf \
            automake \
            python3 \
            python3-pip \
            python3-virtualenv \
            ncurses \
            ca-certificates \
            zsh
        ;;
esac
