# WebServerNpp - Notepad++ Web Server Integration 🌐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Control a web server directly from Notepad++ using Python scripts. Serve files from your current directory and manage the server via console commands.

## 🚀 Quick Start

Get up and running with WebServerNpp in minutes!

## ✨ Features

*   Start/stop server with a simple command.
*   Automatic detection of available ports (default: 8000).
*   Serves files from the active file's directory.
*   Server status displayed in the status bar.
*   Automatically opens HTML files in the browser.

## ⚙️ Installation

### Prerequisites

*   [Notepad++](https://notepad-plus-plus.org/) installed.
*   [Python Script](https://github.com/bruderstein/PythonScript) plugin installed.

### Python Script Plugin Installation

1.  Download the latest release from: [https://github.com/bruderstein/PythonScript/releases](https://github.com/bruderstein/PythonScript/releases)
2.  **Manual Installation:**
    *   Extract the `.zip` file.
    *   Copy `PythonScript.dll` to: `Notepad++\plugins\PythonScript`
    *   Restart Notepad++

### Configure Scripts

1.  Copy `startup.py` and `WebServerNpp.py` to: `Notepad++\plugins\PythonScript\scripts`
2.  Restart Notepad++

## 💻 Usage

### Basic Usage

1.  Open the Python Console:
    `Plugins -> Python Script -> Show Console`

2.  Available commands:

    *   `startws()` - Starts the server in the current directory
        ```python
        startws()
        ```
    *   `stopws()` - Stops the server
        ```python
        stopws()
        ```
    *   `statusws()` - Displays the server status
        ```python
        statusws()
        ```
    *   `refreshws()` - Restarts the server
        ```python
        refreshws()
        ```

## 🛠️ Configuration

### Default Port

To change the default port:

1.  Edit `WebServerNpp.py`
2.  Modify the `DEFAULT_PORT` variable.
    ```python
    DEFAULT_PORT = 8080  # Example: Change to port 8080
    ```

### Port Attempts

To adjust the number of port attempts:

1.  Modify the `MAX_PORT_ATTEMPTS` variable in `WebServerNpp.py`.
    ```python
    MAX_PORT_ATTEMPTS = 10 # Example: Change to 10 attempts
    ```

## ℹ️ Important Notes

*   Developed and tested on Windows 10.
*   Requires the Notepad++ APIs.

## 🚨 Troubleshooting

*   **Python Script Errors:** Verify the plugin installation.  Ensure `PythonScript.dll` is in the correct directory.
*   **Port Conflicts:** The script automatically searches for available ports.  If you consistently encounter issues, consider changing the `DEFAULT_PORT`.

## 📜 License

Open-source (MIT). Contributions are welcome! See the [LICENSE](LICENSE) file for more information.
