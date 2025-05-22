import http.server
import socketserver
import threading
import os
import socket
from typing import Optional
from crewai.tools import tool
import functools # NEUER IMPORT
import time # NEUER IMPORT

_http_server_thread: Optional[threading.Thread] = None
_http_server_instance: Optional[socketserver.TCPServer] = None
_current_hosting_port: Optional[int] = None
_current_hosting_directory: Optional[str] = None

def is_port_available(port: int) -> bool:
    """Checks if a port is available (not in use)."""
    # Temporär Port 0 verwenden, um einen zufälligen freien Port zu bekommen,
    # um die Logik zu testen, ohne den Zielport tatsächlich zu binden.
    # Für die echte Prüfung muss der Zielport verwendet werden.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port)) # Prüfe den spezifischen Port
            return True
        except socket.error:
            return False

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with logging suppressed."""
    def log_message(self, format, *args):
        pass

@tool("Start Local HTTP Server Tool")
def start_local_http_server_tool(directory: str, port: int = 8088) -> str:
    """
    Starts a simple local HTTP server in a separate thread to serve files from the specified directory.
    Checks if the port is available before starting.
    Args:
        directory (str): The local directory from which to serve files (e.g., './application_code').
        port (int): The port number on which to start the server. Defaults to 8088.
    """
    global _http_server_thread, _http_server_instance, _current_hosting_port, _current_hosting_directory

    if _http_server_thread and _http_server_thread.is_alive():
        if _current_hosting_port == port and _current_hosting_directory == directory:
            return f"TOOL_INFO: HTTP server is already running on http://localhost:{port} serving '{directory}'."
        else:
            return f"TOOL_ERROR: Another HTTP server is already running (port: {_current_hosting_port}, dir: '{_current_hosting_directory}'). Stop it first using 'Stop Local HTTP Server Tool'."

    abs_directory = os.path.abspath(directory) # Arbeite mit absoluten Pfaden
    if not os.path.isdir(abs_directory):
        return f"TOOL_ERROR: Directory '{abs_directory}' not found or is not a directory."

    if not is_port_available(port):
        return f"TOOL_ERROR: Port {port} is already in use. Please choose a different port or stop the existing service."

    try:
        # Verwende functools.partial, um das 'directory'-Argument an den Handler zu binden
        # Dies erfordert Python 3.7+ für das directory-Argument im Handler
        handler_class = functools.partial(QuietHTTPRequestHandler, directory=abs_directory)
        
        # TCPServer wird im Kontext des Hauptthreads erstellt, aber serve_forever läuft im neuen Thread
        _http_server_instance = socketserver.TCPServer(("", port), handler_class) 
        
        _http_server_thread = threading.Thread(target=_http_server_instance.serve_forever, daemon=True)
        _http_server_thread.start()
        
        time.sleep(0.5) # Kurze Pause, damit der Server-Thread starten kann

        _current_hosting_port = port
        _current_hosting_directory = abs_directory # Speichere den absoluten Pfad
        print(f"--- Debug (HTTP Server): Server started on http://localhost:{port} serving '{abs_directory}' ---")
        return f"Local HTTP server started successfully on http://localhost:{port} serving files from '{abs_directory}'."
    except Exception as e:
        print(f"--- Debug (HTTP Server): Error starting server: {e} ---")
        return f"TOOL_ERROR: Could not start local HTTP server on port {port} for directory '{abs_directory}': {e}"

@tool("Stop Local HTTP Server Tool")
def stop_local_http_server_tool() -> str:
    """
    Stops the currently running simple local HTTP server if one was started by this tool.
    """
    global _http_server_thread, _http_server_instance, _current_hosting_port, _current_hosting_directory
    
    if _http_server_instance and _http_server_thread and _http_server_thread.is_alive():
        print(f"--- Debug (HTTP Server): Attempting to stop HTTP server on port {_current_hosting_port}... ---")
        try:
            _http_server_instance.shutdown() 
            _http_server_instance.server_close() 
            _http_server_thread.join(timeout=5) 
            
            if _http_server_thread.is_alive():
                print("--- Debug (HTTP Server): Server thread did not stop in time. ---")
            
            message = f"Local HTTP server on port {_current_hosting_port} serving '{_current_hosting_directory}' stopped successfully."
            _http_server_thread = None
            _http_server_instance = None
            _current_hosting_port = None
            _current_hosting_directory = None
            print(f"--- Debug (HTTP Server): {message} ---")
            return message
        except Exception as e:
            print(f"--- Debug (HTTP Server): Error stopping server: {e} ---")
            return f"TOOL_ERROR: Error stopping local HTTP server: {e}"
    else:
        return "TOOL_INFO: No local HTTP server (started by this tool) is currently running."

