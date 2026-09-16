#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update
        sudo apt-get install -y \
            dc \
            coreutils \
            gawk \
            libfuse3-dev \
            fuse3 \
            pkg-config

        cd /tmp || exit 1
        if [ ! -d unionfs-fuse ]; then
            git clone https://github.com/rpodgorny/unionfs-fuse.git
        fi
        cd /tmp/unionfs-fuse || exit 1
        make -j"$(nproc)"
        sudo make install
        ;;
    macos)
        # coreutils/gawk come from the PATH shim (main.sh); dc ships with the
        # base OS. fuse packages are only for try.sh, which is Linux-only.
        brew install pkg-config
        ;;
    fedora)
        sudo dnf makecache
        sudo dnf install -y \
            dc \
            coreutils \
            gawk \
            fuse3-devel \
            fuse3 \
            pkg-config

        cd /tmp || exit 1
        if [ ! -d unionfs-fuse ]; then
            git clone https://github.com/rpodgorny/unionfs-fuse.git
        fi
        cd /tmp/unionfs-fuse || exit 1
        make -j"$(nproc)"
        sudo make install
        ;;
esac
