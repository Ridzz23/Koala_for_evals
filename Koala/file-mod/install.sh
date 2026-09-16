#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update

        sudo apt-get install -y \
          sudo \
          coreutils \
          wget \
          unzip \
          gzip \
          gawk \
          sed \
          git \
          openssl \
          curl wget unzip gzip coreutils ffmpeg unrtf imagemagick zstd git xz-utils
        ;;
    macos)
        # coreutils/gawk/sed come from the PATH shim (main.sh)
        brew install wget unzip gzip git openssl curl ffmpeg unrtf imagemagick zstd xz
        ;;
    fedora)
        sudo dnf makecache

        sudo dnf install -y \
          sudo \
          coreutils \
          wget \
          unzip \
          gzip \
          gawk \
          sed \
          git \
          openssl \
          curl \
          ffmpeg \
          unrtf \
          zstd \
          ImageMagick \
          xz
        ;;
esac
