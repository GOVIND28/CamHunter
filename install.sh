#!/bin/bash

# ╔════════════════════════════════╗
# ║        🎯 CamHunter Setup       ║
# ║  Automated installation script  ║
# ╚════════════════════════════════╝

# Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
  echo "❌ This script is intended for Linux systems only."
  exit 1
fi

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv || {
    echo "❌ Failed to create virtual environment."
    exit 1
}

# Activate virtual environment
source venv/bin/activate || {
    echo "❌ Failed to activate virtual environment."
    exit 1
}

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python requirements..."
pip install -r requirements.txt || {
    echo "❌ Failed to install Python packages."
    deactivate
    exit 1
}

# Install Cloudflare Tunnel
echo "🌐 Installing Cloudflare Tunnel (cloudflared)..."
sudo dpkg -i install/cloudflared.deb || {
    echo "⚠️ dpkg failed. Attempting to fix broken dependencies..."
    sudo apt-get install -f -y
}

# Verify cloudflared installation
if command -v cloudflared &> /dev/null
then
    echo "✅ Cloudflared installed successfully."
else
    echo "❌ Cloudflared installation failed."
    deactivate
    exit 1
fi

# Success message
echo ""
echo "🎯 Setup completed successfully!"
echo "✅ Python virtual environment created: 'venv/'"
echo "✅ Dependencies installed"
echo "✅ Cloudflared installed"

