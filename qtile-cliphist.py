#!/usr/bin/env python3

import subprocess
import os
import time
import shutil
import json
from datetime import datetime

# --- Configuration ---
CLIPBOARD_SELECTION = "clipboard"  # Use "primary" for primary selection
SHOW_CONTENT_PREVIEW = True        # Set to False to just show "Copied"
PREVIEW_MAX_LEN = 50               # Max length of preview
NOTIFICATION_TIMEOUT = 3000        # Milliseconds (3 seconds)
API_BASE_URL = "http://127.0.0.1:8000"  # Base URL for our FastAPI service
# --- End Configuration ---

def run_command(cmd):
    """Runs a command and returns its stdout, handling potential errors."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=5)
        if result.returncode != 0:
            if not (cmd[0] == 'xclip' and result.returncode == 1 and not result.stderr):
                print(f"Error running {' '.join(cmd)}: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"Error: Command not found: {cmd[0]}. Is it installed and in PATH?")
        return None
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out: {' '.join(cmd)}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred running command: {e}")
        return None

def notify(title, message, timeout):
    """Sends a notification using dunstify or notify-send."""
    notifier_cmd_path = shutil.which("dunstify") or shutil.which("notify-send")

    if not notifier_cmd_path:
        print("Error: No notification command found (dunstify or notify-send).")
        return

    notifier_cmd = [notifier_cmd_path, "-t", str(timeout), title, message]
    run_command(notifier_cmd)

def store_clipboard_entry(content):
    """Stores the clipboard content via our FastAPI service using curl."""
    try:
        # Create a temporary file for the JSON data
        with open("/tmp/clipboard_data.json", "w") as f:
            json.dump({"store": content}, f)

        # Use curl to send the data
        cmd = [
            "curl", "-s",
            "-X", "PUT",
            "-H", "Content-Type: application/json",
            "-d", f"@/tmp/clipboard_data.json",
            f"{API_BASE_URL}/clipboard"
        ]
        
        result = run_command(cmd)
        if result:
            try:
                response = json.loads(result)
                if "message" in response and "Text written to clipboard" in response["message"]:
                    return True
            except json.JSONDecodeError:
                print("Error: Invalid JSON response from server")
        return False
    except Exception as e:
        print(f"Error storing clipboard entry: {e}")
        return False

def get_clipboard_history():
    """Retrieves clipboard history from our FastAPI service using curl."""
    try:
        cmd = [
            "curl", "-s",
            "-X", "GET",
            f"{API_BASE_URL}/clipboard"
        ]
        
        result = run_command(cmd)
        if result:
            try:
                response = json.loads(result)
                return response.get("entries", [])
            except json.JSONDecodeError:
                print("Error: Invalid JSON response from server")
        return []
    except Exception as e:
        print(f"Error retrieving clipboard history: {e}")
        return []

def monitor_clipboard():
    """Monitors the clipboard, sends notifications, and stores history via API."""
    clipnotify_cmd = shutil.which("clipnotify")
    xclip_cmd = shutil.which("xclip")

    if not clipnotify_cmd:
        print("Error: 'clipnotify' command not found. Please install it.")
        return
    if not xclip_cmd:
        print("Error: 'xclip' command not found. Please install it.")
        return

    print("Starting clipboard monitor...")
    last_known_content = run_command([xclip_cmd, "-o", "-selection", CLIPBOARD_SELECTION])

    while True:
        process = subprocess.Popen([clipnotify_cmd, "-s", CLIPBOARD_SELECTION])
        process.wait()

        if process.returncode != 0:
            print(f"clipnotify exited with error code {process.returncode}, retrying in 5 seconds...")
            time.sleep(5)
            continue

        time.sleep(0.1)
        new_content = run_command([xclip_cmd, "-o", "-selection", CLIPBOARD_SELECTION])

        if new_content is None:
            if last_known_content is not None:
                print("Clipboard appears to have been cleared or failed to read.")
                last_known_content = None
            continue

        if new_content != last_known_content:
            current_content = new_content
            last_known_content = current_content

            if store_clipboard_entry(current_content):
                title = "Clipboard Updated"
                message = "New content copied."

                if SHOW_CONTENT_PREVIEW:
                    if len(current_content) > PREVIEW_MAX_LEN:
                        preview = current_content[:PREVIEW_MAX_LEN].strip() + "..."
                    else:
                        preview = current_content.strip()
                    preview = preview.replace('"', '\\"')
                    message = f'"{preview}"'

                notify(title, message, NOTIFICATION_TIMEOUT)

if __name__ == "__main__":
    # Ensure only one instance runs
    lock_file_path = f"/tmp/qtile_clipboard_monitor_{os.geteuid()}.lock"
    fd = None

    try:
        fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())

        import atexit
        def cleanup_lock():
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            try:
                if os.path.exists(lock_file_path):
                    with open(lock_file_path, 'r') as f_check:
                        pid_in_file = f_check.read().strip()
                    if pid_in_file == str(os.getpid()):
                        os.remove(lock_file_path)
            except Exception as e:
                print(f"Error during lock file cleanup: {e}")

        atexit.register(cleanup_lock)
        monitor_clipboard()

    except FileExistsError:
        pid = None
        try:
            with open(lock_file_path, 'r') as f:
                pid_str = f.read().strip()
                if pid_str:
                    pid = int(pid_str)
        except (IOError, ValueError) as e:
            print(f"Could not read PID from existing lock file {lock_file_path}: {e}")

        process_running = False
        if pid:
            try:
                os.kill(pid, 0)
                process_running = True
            except OSError:
                process_running = False

        if process_running:
            print(f"Clipboard monitor instance (PID {pid}) already running. Exiting.")
        else:
            print("Stale lock file found. Removing and attempting to start.")
            try:
                os.remove(lock_file_path)
                print("Please restart the script.")
            except OSError as e:
                print(f"Could not remove stale lock file {lock_file_path}: {e}. Exiting.")

    except Exception as e:
        print(f"An unexpected error occurred during startup: {e}")
        if 'cleanup_lock' in locals():
            cleanup_lock()
