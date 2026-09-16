#!/bin/sh

TOP="$(git rev-parse --show-toplevel)"
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        pkgs="binutils git build-essential coreutils wget unzip make pbzip2 binutils bzip2 zstd gnupg"

        sudo apt-get update

        for pkg in $pkgs; do
            if ! dpkg -s "$pkg" >/dev/null 2>&1; then
                sudo apt-get install -y --no-install-recommends "$pkg"
            fi
        done
        ;;
    macos)
        # coreutils comes from the PATH shim (main.sh).
        # binutils (ld/as/objdump) is provided by Xcode Command Line Tools.
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        brew install wget unzip pbzip2 zstd gnupg
        ;;
    fedora)
        pkgs="binutils git build-essential coreutils wget unzip make pbzip2 bzip2 zstd gnupg"

        sudo dnf makecache

        for pkg in $pkgs; do
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
        done
        ;;
esac

eval_dir="${TOP}/ci-cd/riker"

min_benchmark="xz-clang"

run_min=false

for arg in "$@"; do
    if [ "$arg" = "--min" ]; then
        run_min=true
        break
    fi
done

if [ "$run_min" = true ]; then
    for bench in $min_benchmark; do
        script_path="$eval_dir/$bench/install.sh"
        if [ -x "$script_path" ]; then
            "$script_path" "$@"
        else
            echo "Error: $script_path not found or not executable."
            exit 1
        fi
    done
    exit 0
fi

for bench in "$eval_dir"/*; do
    "$bench/install.sh" "$@"
done