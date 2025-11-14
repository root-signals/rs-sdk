#!/bin/sh
#
# Installer for the Judge CLI
#
# This script downloads and installs the cli.py script as an executable
# command named 'scorable'.
#
# Usage:
#   curl -sSL https:/scorable.ai/cli/install.sh | sh
#

set -e

# --- Configuration ---
SOURCE_URL="https://sdk.scorable.ai/cli/cli.py"
INSTALL_NAME="scorable"
INSTALL_DIR="/usr/local/bin"
INSTALL_PATH="$INSTALL_DIR/$INSTALL_NAME"

# --- Helper Functions ---
command_exists() {
  command -v "$@" >/dev/null 2>&1
}

# --- Main Installation Logic ---
main() {
  # Check for a supported operating system
  OS=$(uname -s)
  case "$OS" in
    Linux|Darwin)
      # Supported OS, continue
      ;;
    *)
      echo "Error: Unsupported operating system '$OS'." >&2
      echo "This installer script is designed for Linux and macOS." >&2
      exit 1
      ;;
  esac

  echo "Starting installation of the Judge CLI..."

  # Check for sudo access if we need to write to /usr/local/bin
  if [ -w "$INSTALL_DIR" ]; then
    SUDO=""
  else
    SUDO="sudo"
    echo "Sudo privileges will be required to install to $INSTALL_DIR."
  fi

  # Check for curl
  if ! command_exists curl; then
    echo "Error: curl is not installed. Please install curl to continue." >&2
    exit 1
  fi

  # Check for uv
  if ! command_exists uv; then
    echo "Error: uv is not installed. Please install uv to continue." >&2
    echo "Installation instructions: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
  fi

  # Download the script to a temporary location
  TMP_FILE=$(mktemp)
  echo "Downloading script from $SOURCE_URL..."
  if ! curl -fsSL "$SOURCE_URL" -o "$TMP_FILE"; then
    echo "Error: Failed to download the script from $SOURCE_URL" >&2
    echo "Please check the URL and your network connection." >&2
    rm -f "$TMP_FILE"
    exit 1
  fi

  # Make the script executable
  chmod +x "$TMP_FILE"

  # Move the script to the installation directory
  echo "Installing to $INSTALL_PATH..."
  if ! $SUDO mv "$TMP_FILE" "$INSTALL_PATH"; then
    echo "Error: Failed to move script to $INSTALL_PATH." >&2
    echo "Please check your permissions or run the script with sudo." >&2
    rm -f "$TMP_FILE"
    exit 1
  fi

  echo
  echo "Judge CLI installed successfully!"
  echo "You can now run it with the command: SCORABLE_API_KEY=<your-api-key> $INSTALL_NAME judge list"
  echo
  echo "To uninstall, run: $SUDO rm $INSTALL_PATH"
}

# --- Run ---
main