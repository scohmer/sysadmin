import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import json
import csv
from datetime import datetime
import wmi
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize WMI client
c = wmi.WMI()

# Fetch Full Name of the logged-in user
def get_user_full_name():
    user_info = c.Win32_ComputerSystem()[0]
    user_name = user_info.UserName  # Returns "DOMAIN\\Username"
    if user_name:
        try:
            domain, username = user_name.split('\\')
        except ValueError:
            # In case the domain is not included
            domain = None
            username = user_name
        users = c.Win32_UserAccount(Name=username)
        for user in users:
            if domain is None or user.Domain == domain:
                full_name = user.FullName
                if full_name:
                    return full_name
                else:
                    return username  # Fallback to username if FullName is empty
    return None

# Get the current month and year
current_month_year = datetime.now().strftime("%b_%Y").upper()

# Get the shared path from the .env file
shared_path = os.getenv("SHARED_PATH", ".")

# Construct the full paths for JSON and CSV files using the shared path
json_file_path = os.path.join(shared_path, f"{current_month_year}_maintenance_log.json")
csv_file_path = os.path.join(shared_path, f"{current_month_year}_maintenance_log.csv")

# Get salt from environment variable or generate one
env_salt = os.getenv("SALT_GEN")
if env_salt:
    salt = env_salt.encode('utf-8')
else:
    salt = os.urandom(16)

# Function to generate a unique ID using SHA-256 with salt (still used internally for integrity checks)
def generate_unique_id(data):
    combined_data = f"{data['hostname']}{data['action_taken']}{data['username']}{data['timestamp']}".encode('utf-8')
    salted_data = salt + combined_data
    return hashlib.sha256(salted_data).hexdigest()

# Function to get the next auto-incrementing entry_id
def get_next_entry_id():
    try:
        with open(json_file_path, 'r') as json_file:
            logs = json.load(json_file)
            if logs:
                # Get the last entry's ID and increment it by 1
                last_entry_id = logs[-1].get("entry_id", 0)
                return last_entry_id + 1
    except (FileNotFoundError, json.JSONDecodeError):
        # If no logs exist, start from 1
        return 1

# Get the image path from the environment variable or use a default value
logo_img_path = os.getenv("LOGO_IMG", "images/generic_logo.png")

# Function to get the path to bundled files in PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # When running in a normal environment (not bundled), use the script's directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize the main menu window
app = tk.Tk()
app.title("Maintenance Log Menu")

# Load the company logo using the correct path
image_path = resource_path(logo_img_path)
image = Image.open(image_path)

# Resize the image to 50% of its original size using LANCZOS filter
width, height = image.size
resized_image = image.resize((width // 2, height // 2), Image.LANCZOS)

# Convert the resized image to a format Tkinter can use
logo = ImageTk.PhotoImage(resized_image)

# Display the company logo at the top of the window
logo_label = tk.Label(app, image=logo)
logo_label.pack(pady=20)

# Function to log actions (Logger)
def log_action():
    hostname = hostname_entry.get()
    action_taken = action_entry.get("1.0", tk.END).strip()

    if not hostname or not action_taken:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    # Get the user's full name
    full_name = get_user_full_name()
    if not full_name:
        messagebox.showerror("Error", "Unable to retrieve user full name.")
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the next entry ID
    entry_id = get_next_entry_id()

    log_entry = {
        "entry_id": entry_id,
        "hostname": hostname,
        "action_taken": action_taken,
        "username": full_name,
        "timestamp": timestamp
    }

    # Generate unique ID for internal use only
    unique_id = generate_unique_id(log_entry)
    log_entry["unique_id"] = unique_id

    try:
        # Append to JSON file (keeping the unique_id here)
        with open(json_file_path, 'r+') as json_file:
            try:
                logs = json.load(json_file)
            except json.JSONDecodeError:
                logs = []
            logs.append(log_entry)
            json_file.seek(0)
            json.dump(logs, json_file, indent=4)
    except FileNotFoundError:
        with open(json_file_path, 'w') as json_file:
            json.dump([log_entry], json_file, indent=4)

    # Prepare log entry for CSV (remove unique_id before writing)
    csv_log_entry = log_entry.copy()  # Create a copy of the log entry
    del csv_log_entry["unique_id"]  # Remove unique_id before writing to CSV

    # Append to CSV file
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        fieldnames = ["entry_id", "hostname", "action_taken", "username", "timestamp"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(csv_log_entry)

    # Success message after log entry is written
    messagebox.showinfo("Success", f"Action logged successfully! Log Entry ID: {entry_id}")
    
    # Clear inputs
    hostname_entry.delete(0, tk.END)
    action_entry.delete(0, tk.END)

# Function to load and display logs (Viewer)
def load_logs():
    try:
        with open(json_file_path, 'r') as json_file:
            logs = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    log_text.delete(1.0, tk.END)

    for log in logs:
        log_text.insert(tk.END, f"Log Entry ID: {log['entry_id']}\n")
        log_text.insert(tk.END, f"Hostname: {log['hostname']}\n")
        log_text.insert(tk.END, f"Action Taken: {log['action_taken']}\n")
        log_text.insert(tk.END, f"Username: {log['username']}\n")
        log_text.insert(tk.END, f"Timestamp: {log['timestamp']}\n")
        log_text.insert(tk.END, "-" * 40 + "\n")

# Function to check log integrity (but hide unique_id in output)
def open_log_integrity():
    try:
        with open(json_file_path, 'r') as json_file:
            logs = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Error", "No logs available for integrity check.")
        return

    integrity_results = []
    for log in logs:
        current_log_data = {
            "hostname": log['hostname'],
            "action_taken": log['action_taken'],
            "username": log['username'],
            "timestamp": log['timestamp']
        }

        current_hash = generate_unique_id(current_log_data)

        if current_hash == log['unique_id']:
            result = f"Log entry with ID '{log['entry_id']}' is intact."
        else:
            result = f"WARNING: Log entry with ID '{log['entry_id']}' has been tampered with!"
        integrity_results.append(result)

    log_text.delete(1.0, tk.END)
    for result in integrity_results:
        log_text.insert(tk.END, result + "\n")
        log_text.insert(tk.END, "-" * 40 + "\n")

    intact_count = sum("is intact" in r for r in integrity_results)
    tampered_count = len(integrity_results) - intact_count
    summary_message = f"Integrity check complete: {intact_count} intact, {tampered_count} tampered."
    messagebox.showinfo("Integrity Check Results", summary_message)

# Function to open Logger window
def open_logger():
    app.withdraw()
    logger_window = tk.Toplevel(app)
    logger_window.title("Logger")

    # Display the company logo at the top of the Logger window
    logo_label = tk.Label(logger_window, image=logo)
    logo_label.pack(pady=20)

    # Hostname label and input
    tk.Label(logger_window, text="Hostname:").pack(pady=5)
    global hostname_entry
    hostname_entry = tk.Entry(logger_window)
    hostname_entry.pack(pady=5)

    # Action Taken label and larger input box (Text widget)
    tk.Label(logger_window, text="Action Taken:").pack(pady=5)
    global action_entry
    action_entry = tk.Text(logger_window, width=40, height=5, wrap=tk.WORD)  # Multi-line input
    action_entry.pack(pady=5)

    # Log Action button
    log_button = tk.Button(logger_window, text="Log Action", command=log_action)
    log_button.pack(pady=10)

    logger_window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(logger_window))

# Function to open Viewer window
def open_viewer():
    app.withdraw()
    viewer_window = tk.Toplevel(app)
    viewer_window.title("Viewer")

    global log_text
    log_text = scrolledtext.ScrolledText(viewer_window, wrap=tk.WORD, width=50, height=20)
    log_text.pack(pady=10)

    load_button = tk.Button(viewer_window, text="Load Logs", command=load_logs)
    load_button.pack(pady=5)

    integrity_button = tk.Button(viewer_window, text="Check Log Integrity", command=open_log_integrity)
    integrity_button.pack(pady=5)

    viewer_window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(viewer_window))

# Function to reopen the main menu when a window is closed
def on_window_close(window):
    window.destroy()
    app.deiconify()

# Add the title and buttons
tk.Label(app, text="Select an Application", font=('Helvetica', 14)).pack(pady=20)

logger_button = tk.Button(app, text="Open Logger", command=open_logger, width=20)
logger_button.pack(pady=10)

viewer_button = tk.Button(app, text="Open Viewer", command=open_viewer, width=20)
viewer_button.pack(pady=10)

app.mainloop()
