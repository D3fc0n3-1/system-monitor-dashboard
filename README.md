# System Monitor Dashboard

## Description

A simple web-based dashboard that displays real-time resource usage (CPU, Memory, Disk I/O, Network I/O) from multiple servers running the [Glances](https://github.com/nicolargo/glances) system monitoring tool. It fetches data from the Glances REST API and presents it in an easy-to-read, auto-refreshing interface with a theme toggle.

## Features

*   Monitors multiple servers configured in a simple YAML file.
*   Displays CPU usage, Memory usage, Disk I/O rate (MB/s), and Network I/O rate (Mbps).
*   Shows server status (Online, Offline, Error).
*   Automatically refreshes data every 5 seconds.
*   Light and Dark theme toggle with preference saved in local storage.
*   Simple, dependency-light frontend (HTML, CSS, Vanilla JS).
*   Python FastAPI backend to aggregate data.

## Getting Started

### Prerequisites

*   **Python:** Version 3.8 or higher.
*   **pip:** Python package installer (usually comes with Python).
*   **Git:** For cloning the repository.
*   **Glances:** Installed and running on each server you want to monitor.
    *   Glances must be started with its REST API / Web UI enabled. The recommended way is using the `-w` flag (e.g., `glances -w -B 0.0.0.0`). The `-B 0.0.0.0` binds it to all network interfaces, making it accessible over the network.
    *   Ensure the Glances API port (default: 61208) is accessible from the machine where you run the backend service (check firewalls).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/D3fc0n3-1/system-monitor-dashboard
    cd system-monitor-dashboard
    ```

2.  **Set up a Python virtual environment (Recommended):**
    ```bash
    # Linux/macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows (cmd)
    python -m venv .venv
    .\.venv\Scripts\activate

    # Windows (PowerShell)
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configure Servers:**
    *   Edit the `backend/config.yaml` file.
    *   List each server you want to monitor, providing a unique `name` and its `glances_api_url`.
    *   **Important:** The `glances_api_url` must include the correct protocol (`http` or `https`), IP address or hostname, port (default `61208`), and the **correct API path suffix** (`/api/3/` for Glances v3 or `/api/4/` for Glances v4 - check your Glances logs). Make sure the URL ends with a trailing slash `/`.
    *   Example `config.yaml`:
        ```yaml
        servers:
          - name: kube1
            glances_api_url: http://192.168.50.211:61208/api/3/
          - name: kube2
            glances_api_url: http://192.168.50.212:61208/api/3/
          - name: NAS-1
            glances_api_url: http://192.168.50.213:61208/api/4/
          # Add more servers as needed
        ```

### Running the Application

1.  **Start the Backend Service:**
    *   Navigate to the `backend` directory in your terminal:
        ```bash
        cd backend
        ```
    *   Run Uvicorn (make sure your virtual environment is active):
        ```bash
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ```
        *   `--reload`: Automatically restarts the server when code changes (good for development).
        *   `--host 0.0.0.0`: Makes the backend accessible from other machines on your network (necessary for the frontend in your browser to reach it).
        *   `--port 8000`: Specifies the port the backend listens on.

2.  **Open the Frontend:**
    *   Navigate to the `frontend` directory in your file explorer.
    *   Open the `index.html` file directly in your web browser (e.g., Chrome, Firefox, Edge).

## Usage

*   The dashboard will automatically load and display cards for each server configured in `config.yaml`.
*   Each card shows the server name, current status, and key performance metrics (CPU, Memory, Disk I/O, Network I/O).
*   Data refreshes automatically every 5 seconds.
*   Use the "Toggle Theme" button in the top-right corner to switch between light and dark modes. Your preference is saved locally in your browser.
*   If a server is unreachable or Glances is not running correctly, it will show an "Offline" or "Error" status with details if available.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if you choose to add one).