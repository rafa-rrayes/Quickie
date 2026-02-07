#!/bin/sh
set -e

REPO="https://github.com/rafa-rrayes/quickie.git"

echo "Installing Quickie..."

# Check for uv first (preferred), then pipx, then pip
if command -v uv >/dev/null 2>&1; then
    uv tool install "quickie @ git+${REPO}"
elif command -v pipx >/dev/null 2>&1; then
    pipx install "git+${REPO}"
else
    echo "Error: uv or pipx is required to install Quickie."
    echo ""
    echo "Install uv:   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Install pipx: brew install pipx  (or)  pip install pipx"
    exit 1
fi

echo ""
echo "Quickie installed! Run 'quickie' to start."
