#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo apt-get update

        pkgs="bash curl grep gawk iptables ufw procps net-tools fail2ban iproute2 git patch time"

        for pkg in $pkgs; do
            if ! dpkg -l | grep -q "^ii  $pkg "; then
                sudo apt-get install -y --no-install-recommends "$pkg"
            fi
        done
        ;;
    macos)
        # grep/gawk come from the PATH shim (main.sh). iptables/ufw/procps/
        # net-tools/fail2ban/iproute2 are only for vps-audit.sh, which is
        # Linux-only; git-workflow.sh just needs bash/git/patch/time.
        brew install bash curl git gpatch gnu-time
        ;;
    fedora)
        sudo dnf makecache

        pkgs="bash curl grep gawk iptables procps-ng net-tools fail2ban iproute git patch time"

        for pkg in $pkgs; do
            if ! rpm -q "$pkg" >/dev/null 2>&1; then
                sudo dnf install -y "$pkg"
            fi
        done
        ;;
esac
