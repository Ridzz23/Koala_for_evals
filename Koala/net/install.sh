#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

case "$OS" in
    debian)
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --yes --dearmor -o /etc/apt/keyrings/charm.gpg
        echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list

        sudo apt-get update -y

        sudo apt-get install -y \
            build-essential \
            git \
            curl \
            wget \
            gpg \
            automake \
            flex \
            tar \
            libpq-dev \
            libpcre3-dev \
            libssl-dev \
            libpcap-dev \
            libltdl-dev \
            bison \
            python3 \
            python3-pip \
            python3-venv \
            net-tools \
            xsltproc \
            bind9-dnsutils \
            netcat-traditional

        sudo apt-get install -y \
            nmap \
            lolcat \
            masscan \
            bind9-host \
            geoip-bin \
            hwinfo \
            autoconf \
            iproute2 \
            iptables \
            ipset \
            masscan \
            postgresql \
            postgresql-contrib \
            check \
            iputils-ping
        ;;
    macos)
        # net/execute.sh manipulates firewall/NAT rules and Linux network
        # namespaces directly, with no macOS equivalent. ipset/iproute2/
        # net-tools/hwinfo/geoip-bin have no brew formula either; omitted.
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Xcode Command Line Tools required: run 'xcode-select --install' first." >&2
            exit 1
        fi
        brew install git curl wget gnupg automake flex gnu-tar libpq pcre openssl libpcap \
            libtool bison python3 libxslt bind netcat nmap lolcat masscan postgresql \
            check iputils
        ;;
    fedora)
        sudo dnf makecache

        sudo dnf install -y \
            gcc \
            gcc-c++ \
            make \
            git \
            curl \
            wget \
            gpg \
            automake \
            flex \
            tar \
            postgresql-devel \
            pcre-devel \
            openssl-devel \
            libpcap-devel \
            libtool-ltdl-devel \
            bison \
            python3 \
            python3-pip \
            python3-virtualenv \
            net-tools \
            libxslt \
            bind-utils \
            nc \
            nmap \
            lolcat \
            masscan \
            bind \
            geoip \
            hwinfo \
            autoconf \
            iproute \
            iptables \
            ipset \
            postgresql-server \
            postgresql-contrib \
            check \
            iputils
        ;;
esac
