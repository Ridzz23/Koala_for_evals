#!/bin/sh

TOP=$(git rev-parse --show-toplevel)
OS=$("$TOP/.tools/detect-os.sh")

if [ "$OS" = "fedora" ]; then
    # validate.sh's shasum needs Digest::SHA, missing from Fedora's minimal perl.
    sudo dnf makecache
    sudo dnf install perl-Digest-SHA -y
fi

# This benchmark does not have any other dependencies.
