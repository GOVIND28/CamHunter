# 📸 CamHunter


A **Flask-based tool** for **educational and ethical testing purposes only**. CamHunter captures real-time photos and browser/device information from connected clients (based on IP) and organizes them in a neat, per-IP folder structure. It's built for simplicity and works seamlessly across PC and mobile browsers.

> **⚠️ Disclaimer:** This tool is intended solely for authorized and ethical use. Unauthorized access, monitoring, or data collection from any device without explicit, informed consent is illegal in many jurisdictions and is strictly prohibited. The creators and contributors of this project are not responsible for any misuse or illegal activities conducted with this software. By using this tool, you agree to assume all responsibility and liability for your actions.

---

## 🚀 Key Features

- **🧠 Smart Detection:** Automatically captures device and browser information every 10 seconds.
- **📷 Real-time Photo Capture:** Snaps a camera photo every 2 seconds.
- **🌍 IP-based Organization:** Organizes all captured data into neatly structured folders for each connected IP address.
- **💻 Cross-Platform Compatible:** Works flawlessly on both mobile and desktop browsers.
- **🔒 Secure Deployment:** Designed to run securely via a Cloudflare Tunnel for private and remote access.
- **⚙️ Admin Dashboard:** A dedicated dashboard to view captured data (default port: `5001`).
- **🧪 Local Preview:** A local preview of the capture page (default port: `5000`).
- **🧩 Lightweight:** Built with a single HTML template and Bootstrap for a clean interface.

---

## 🔧 Installation

Before you begin, ensure you have **Python 3** and `pip` installed.

1.  **Clone the Repository:**
    ```sh
    git clone https://github.com/GOVIND28/CamHunter.git
    ```
    ```sh
    cd CamHunter
    ```
    ```sh
    chmod +x install.sh
    ```
    ```sh
    chmod +x run.sh
    ```    

2.  **Run the Installation Script:**
    This script will install all the necessary dependencies. **It requires `sudo` permissions.**
    ```sh
    sudo ./install.sh
    ```

---

## ⚙️ Usage

Once installed, you can start the CamHunter server with a single command. **This script does not require `sudo`.**

* **To start the server:**
    ```sh
    ./run.sh
    ```
    This will start the Flask server. You can then access:
    - **Local Preview:** `http://127.0.0.1:5000`
    - **Admin Dashboard:** `http://127.0.0.1:5001`

* **For Secure Remote Access:**
    The `run.sh` script is configured to help you set up a **Cloudflare Tunnel**, which is the recommended way to securely expose your server to the internet.

---

## 🙏 Contributing

We welcome contributions! If you have suggestions for new features or improvements, feel free to open an issue or submit a pull request. Please ensure your contributions align with the ethical and educational focus of this project.

---

## 📝 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

## 👤 Author

* **Govind Ambade** - [LinkedIn](https://www.linkedin.com/in/govind-ambade)
