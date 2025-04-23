# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread

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

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, text):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, text, (self.tag,))
        self.widget.configure(state='disabled')
        self.widget.see(tk.END)

    def flush(self):
        pass

class WebServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Npp Web Server Controller")
        master.geometry("700x500")
        
        self.create_widgets()
        self.update_status_indicator()
        self.setup_style()
        
        # Redirigir salida de consola
        sys.stdout = TextRedirector(self.log_area, "stdout")
        sys.stderr = TextRedirector(self.log_area, "stderr")

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=5, font=('Arial', 9))
        style.configure('Green.TFrame', background='#4CAF50')
        style.configure('Red.TFrame', background='#F44336')
        style.configure('Status.TLabel', font=('Arial', 10, 'bold'))
        style.configure('TLabelFrame', font=('Arial', 10, 'bold'))
        style.configure('TLabelFrame.Label', font=('Arial', 10))

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Panel de control
        control_frame = ttk.LabelFrame(main_frame, text="Server Control")
        control_frame.pack(fill='x', pady=5)

        # Status indicator with label
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=0, column=0, padx=5, sticky='w')
        
        self.status_indicator = ttk.Frame(status_frame, width=20, height=20)
        self.status_indicator.pack(side='left', padx=(0,5))
        
        self.status_label = ttk.Label(status_frame, text="Stopped", font=('Arial', 10))
        self.status_label.pack(side='left')
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=0, column=1, sticky='e')
        
        ttk.Button(btn_frame, text="Start", command=self.start_server).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Stop", command=self.stop_server).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Restart", command=self.refresh_server).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Status", command=self.show_status).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Open Browser", command=self.open_browser).pack(side='left', padx=2)

        # Información del servidor
        info_frame = ttk.LabelFrame(main_frame, text="Server Information")
        info_frame.pack(fill='x', pady=5)

        self.info_text = scrolledtext.ScrolledText(info_frame, height=4, state='disabled', font=('Consolas', 9))
        self.info_text.pack(fill='x', padx=5, pady=5)

        # Registro de actividad
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log")
        log_frame.pack(expand=True, fill='both', pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=('Consolas', 9))
        self.log_area.pack(expand=True, fill='both', padx=5, pady=5)

        # Configure tags for colored output
        self.log_area.tag_config('stdout', foreground='black')
        self.log_area.tag_config('stderr', foreground='red')

    def update_status_indicator(self):
        if server_info["is_running"]:
            self.status_indicator.configure(style='Green.TFrame')
            self.status_label.config(text=f"Running on port {server_info['port']}")
        else:
            self.status_indicator.configure(style='Red.TFrame')
            self.status_label.config(text="Stopped")
        
        self.update_info_panel()
        self.master.after(1000, self.update_status_indicator)

    def update_info_panel(self):
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        if server_info["is_running"]:
            info = f"Port: {server_info['port']}\n"
            info += f"Directory: {server_info['directory']}\n"
            info += f"URL: http://localhost:{server_info['port']}"
            self.info_text.insert(tk.END, info)
        else:
            self.info_text.insert(tk.END, "Server is not running")
        self.info_text.config(state='disabled')

    def start_server(self):
        Thread(target=start_web_server, daemon=True).start()

    def stop_server(self):
        Thread(target=stop_web_server, daemon=True).start()

    def refresh_server(self):
        Thread(target=refresh_web_server, daemon=True).start()

    def show_status(self):
        if server_info["is_running"]:
            status_text = (
                f"Server ACTIVE\n"
                f"Port: {server_info['port']}\n"
                f"Directory: {server_info['directory']}\n"
                f"URL: http://localhost:{server_info['port']}"
            )
        else:
            status_text = "Server INACTIVE"
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, status_text)
        self.info_text.config(state='disabled')
        
        self.log_area.insert(tk.END, "Status checked: " + ("Server is active\n" if server_info["is_running"] else "Server is inactive\n"))
        self.log_area.see(tk.END)

    def open_browser(self):
        if server_info["is_running"]:
            webbrowser.open(f"http://localhost:{server_info['port']}")
        else:
            messagebox.showwarning("Server Not Running", "The web server is not currently running")

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
    else:
        msg = "Server INACTIVE."
        console.write("Server status: INACTIVE\n")

def refresh_web_server():
    """Restart the web server with current active file's directory."""
    global server_info
    console.show()
    
    if server_info["is_running"]:
        stop_web_server()
    start_web_server()

def show_gui():
    """Show the Tkinter GUI interface"""
    root = tk.Tk()
    app = WebServerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    console.write("--- Executing script directly ---\n")
    if not server_info["is_running"]:
        start_web_server()
    else:
        show_server_status()