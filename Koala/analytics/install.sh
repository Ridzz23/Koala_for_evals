#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")
eval_dir="$TOP/analytics"

case "$OS" in
    debian)
        sudo apt-get update

        sudo apt-get install -y --no-install-recommends \
          tcpdump curl wget coreutils diffutils gzip bcftools gawk unzip git \
          jq \
          coreutils \
          gawk \
          cmake \
          build-essential \
          libjansson-dev \
          libpcap-dev \
          tar \
          git \
          python3 \
          q-text-as-data \
          grep \
          sed

        # Set GO_VERSION *before* using it
        GO_VERSION=1.24.2
        echo "Installing Go $GO_VERSION"

        go_install_dir="${eval_dir}/go_install"

        mkdir -p "$go_install_dir"
        curl -LO "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
        tar -C "$go_install_dir" -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
        rm -f "go${GO_VERSION}.linux-amd64.tar.gz"

        export GOROOT="$go_install_dir/go"
        export PATH="$GOROOT/bin:$PATH"
        ;;
    macos)
        # coreutils/gawk/grep/sed come from the PATH shim (main.sh). q-text-as-data
        # has no brew formula; every call to `q` in ray-tracing.sh is already
        # commented out, so nothing depends on it.
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        brew install tcpdump curl wget diffutils bcftools unzip git jq cmake jansson libpcap gnu-tar python3 go
        ;;
    fedora)
        sudo dnf makecache

        sudo dnf install -y \
          tcpdump curl wget coreutils diffutils gzip gawk unzip git \
          jq \
          cmake \
          gcc \
          gcc-c++ \
          jansson-devel \
          libpcap-devel \
          tar \
          python3 \
          grep \
          sed \
          bc \
          bcftools

        # Set GO_VERSION *before* using it
        GO_VERSION=1.24.2
        echo "Installing Go $GO_VERSION"

        go_install_dir="${eval_dir}/go_install"

        mkdir -p "$go_install_dir"
        curl -LO "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
        tar -C "$go_install_dir" -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
        rm -f "go${GO_VERSION}.linux-amd64.tar.gz"

        export GOROOT="$go_install_dir/go"
        export PATH="$GOROOT/bin:$PATH"
        ;;
esac

export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# Confirm Go is now working
go version || { echo "Go installation failed"; exit 1; }

# Install zannotate
go install github.com/zmap/zannotate/cmd/zannotate@latest

# Confirm zannotate is now on PATH
command -v zannotate || { echo "zannotate not found on PATH after go install"; exit 1; }
