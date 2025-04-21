# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import socket
import threading
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

# Import Notepad++ Python Script modules
from Npp import notepad, console, MESSAGEBOXFLAGS, STATUSBARSECTION

# --- Configuration ---
DEFAULT_PORT = 8000
MAX_PORT_ATTEMPTS = 50
SERVER_STATUS_SECTION = STATUSBARSECTION.DOCTYPE

# --- Global Server State ---
server_info = {
    "httpd": None,
    "thread": None,
    "port": None,
    "directory": None,
    "is_running": False
}

# --- Server Functions ---

def find_available_port(start_port, max_attempts):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('localhost', port))
            s.close()
            console.write("Found available port: {}\n".format(port))
            return port
        except socket.error as e:
            if e.errno == 98 or e.errno == 10048:
                console.write("Port {} in use, trying next...\n".format(port))
            else:
                console.error("Unexpected error while finding port: {}\n".format(e))
                return None
    return None

def server_thread_target(httpd, directory):
    """Server thread execution target."""
    original_dir = os.getcwd()
    try:
        os.chdir(directory)
        console.write("HTTP server serving from: '{}'\n".format(directory))
        httpd.serve_forever()
    except Exception as e:
        console.error("Server thread error: {}\n".format(e))
    finally:
        os.chdir(original_dir)
        console.write("Server thread terminated.\n")

def start_web_server():
    """Start the web server if not already running."""
    global server_info
    console.show()

    if server_info["is_running"]:
        notepad.messageBox(
            "Server already running at http://localhost:{}\nServing: {}".format(
                server_info["port"], server_info["directory"]
            ),
            "Web Server - Info",
            MESSAGEBOXFLAGS.ICONINFORMATION
        )
        console.write("Attempted to start server when already active.\n")
        return

    current_file = notepad.getCurrentFilename()
    if not current_file:
        console.error("No active file to determine serving directory.\n")
        notepad.messageBox(
            "Please open a file in the directory you want to serve.",
            "Web Server - Error",
            MESSAGEBOXFLAGS.ICONERROR
        )
        return

    current_dir = os.path.dirname(current_file)
    target_file_basename = os.path.basename(current_file)

    port = find_available_port(DEFAULT_PORT, MAX_PORT_ATTEMPTS)
    if port is None:
        error_msg = "Could not find available port between {} and {}.".format(
            DEFAULT_PORT, DEFAULT_PORT + MAX_PORT_ATTEMPTS - 1
        )
        console.error(error_msg + "\n")
        notepad.messageBox(error_msg, "Web Server - Error", MESSAGEBOXFLAGS.ICONERROR)
        return

    try:
        httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)

        server_info["httpd"] = httpd
        server_info["port"] = port
        server_info["directory"] = current_dir
        server_info["is_running"] = True

        thread = threading.Thread(target=server_thread_target, args=(httpd, current_dir))
        thread.daemon = True
        server_info["thread"] = thread
        thread.start()

        url_path = target_file_basename if target_file_basename.lower().endswith(('.html', '.htm')) else ''
        url = "http://localhost:{}/{}".format(port, url_path)

        status_msg = "Server running on port {}".format(port)
        notepad.setStatusBar(SERVER_STATUS_SECTION, status_msg)
        console.write("Server started at: {}\n".format(url))
        console.write("Serving directory: {}\n".format(current_dir))

        webbrowser.open(url)

    except socket.error as e:
        error_msg = "Socket error starting server on port {}: {}".format(port, e)
        console.error(error_msg + "\n")
        notepad.messageBox(error_msg, "Web Server - Error", MESSAGEBOXFLAGS.ICONERROR)
        server_info["is_running"] = False
        server_info["httpd"] = None
    except Exception as e:
        error_msg = "Unexpected error starting server: {}".format(e)
        console.error(error_msg + "\n")
        notepad.messageBox(error_msg, "Web Server - Error", MESSAGEBOXFLAGS.ICONERROR)
        server_info["is_running"] = False
        server_info["httpd"] = None

def stop_web_server():
    """Stop the web server if running."""
    global server_info
    console.show()

    if not server_info["is_running"] or not server_info["httpd"]:
        console.write("Attempted to stop server when not active.\n")
        notepad.messageBox("Web server is not running.", "Web Server - Info", MESSAGEBOXFLAGS.ICONINFORMATION)
        return

    console.write("Stopping web server on port {}...\n".format(server_info["port"]))

    try:
        server_info["httpd"].shutdown()
        server_info["thread"].join(timeout=5.0)
        if server_info["thread"].is_alive():
            console.warn("Server thread didn't terminate cleanly after timeout.\n")
        else:
             console.write("Server thread joined successfully.\n")

        server_info["httpd"].server_close()
        console.write("Server socket closed.\n")

        notepad.setStatusBar(SERVER_STATUS_SECTION, "")
        console.write("Web server stopped successfully.\n")
        notepad.messageBox(
            "Web server stopped.\nPort released: {}".format(server_info["port"]),
            "Web Server Stopped",
            MESSAGEBOXFLAGS.ICONINFORMATION
        )

    except Exception as e:
        error_msg = "Error stopping server: {}".format(e)
        console.error(error_msg + "\n")
        notepad.messageBox(error_msg, "Web Server - Error", MESSAGEBOXFLAGS.ICONERROR)
    finally:
        server_info["httpd"] = None
        server_info["thread"] = None
        server_info["port"] = None
        server_info["directory"] = None
        server_info["is_running"] = False
        notepad.setStatusBar(SERVER_STATUS_SECTION, "")

def show_server_status():
    """Show current server status."""
    console.show()
    if server_info["is_running"]:
        msg = "Server ACTIVE\nPort: {}\nDirectory: {}".format(
            server_info["port"], server_info["directory"]
        )
        console.write("Server status: ACTIVE on port {}\n".format(server_info["port"]))
        notepad.messageBox(msg, "Web Server Status", MESSAGEBOXFLAGS.ICONINFORMATION)
    else:
        msg = "Server INACTIVE."
        console.write("Server status: INACTIVE\n")
        notepad.messageBox(msg, "Web Server Status", MESSAGEBOXFLAGS.ICONINFORMATION)

def refresh_web_server():
    """Restart the web server with current active file's directory."""
    global server_info
    console.show()
    
    if server_info["is_running"]:
        stop_web_server()
    start_web_server()

if __name__ == '__main__':
    console.write("--- Executing script directly ---\n")
    if not server_info["is_running"]:
        start_web_server()
    else:
        show_server_status()