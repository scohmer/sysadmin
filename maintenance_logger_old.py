import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import csv
from datetime import datetime
import getpass
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Paths for the log files
json_file_path = "maintenance_logs.json"
csv_file_path = "maintenance_logs.csv"

# Get salt from environment variable or generate one
salt = os.getenv("SALT_GEN", os.urandom(16)).encode('utf-8')

# Function to generate a unique ID using SHA-256 with salt
def generate_unique_id(data):
    # Combine data fields into a single string
    combined_data = f"{data['hostname']}{data['action_taken']}{data['username']}{data['timestamp']}".encode('utf-8')

    # Combine the salt and the data
    salted_data = salt + combined_data

    # Generate a SHA-256 hash
    return hashlib.sha256(salted_data).hexdigest()

# Function to log actions (Logger)
def log_action():
    hostname = hostname_entry.get()
    action_taken = action_entry.get()

    if not hostname or not action_taken:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    # Get the system username and current timestamp
    username = getpass.getuser()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Data to be logged
    log_entry = {
        "hostname": hostname,
        "action_taken": action_taken,
        "username": username,
        "timestamp": timestamp
    }

    # Generate unique ID for the log entry
    unique_id = generate_unique_id(log_entry)
    log_entry["unique_id"] = unique_id

    # Append to JSON file
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w') as json_file:
            json.dump([], json_file)  # Create empty list

    with open(json_file_path, 'r+') as json_file:
        logs = json.load(json_file)
        logs.append(log_entry)
        json_file.seek(0)
        json.dump(logs, json_file, indent=4)

    # Append to CSV file
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        fieldnames = ["hostname", "action_taken", "username", "timestamp", "unique_id"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(log_entry)

    # Success message and clear inputs
    messagebox.showinfo("Success", "Action logged successfully!")
    hostname_entry.delete(0, tk.END)
    action_entry.delete(0, tk.END)

# Function to load and display logs (Viewer)
def load_logs():
    with open(json_file_path, 'r') as json_file:
        logs = json.load(json_file)
    
    # Clear the text area
    log_text.delete(1.0, tk.END)

    # Display logs in the text area
    for log in logs:
        log_text.insert(tk.END, f"Hostname: {log['hostname']}\n")
        log_text.insert(tk.END, f"Action Taken: {log['action_taken']}\n")
        log_text.insert(tk.END, f"Username: {log['username']}\n")
        log_text.insert(tk.END, f"Timestamp: {log['timestamp']}\n")
        log_text.insert(tk.END, f"Unique ID: {log['unique_id']}\n")
        log_text.insert(tk.END, "-" * 40 + "\n")

# Function to check log integrity
def open_log_integrity():
    # Load logs from the JSON file
    with open(json_file_path, 'r') as json_file:
        logs = json.load(json_file)

    # Initialize the result
    integrity_results = []

    # Iterate through the logs to check the integrity
    for log in logs:
        # Generate a new hash based on the current log data
        current_log_data = {
            "hostname": log['hostname'],
            "action_taken": log['action_taken'],
            "username": log['username'],
            "timestamp": log['timestamp']
        }

        # Generate a bcrypt hash using the current log data
        current_hash = generate_unique_id(current_log_data)

        # Compare the new hash with the stored unique_id
        if current_hash == log['unique_id']:
            result = f"Log entry with unique_id '{log['unique_id']}' is intact."
        else:
            result = f"WARNING: Log entry with unique_id '{log['unique_id']}' has been tampered with!"

        # Append the result to the integrity results
        integrity_results.append(result)

    # Display integrity results
    log_text.delete(1.0, tk.END)
    for result in integrity_results:
        log_text.insert(tk.END, result + "\n")
        log_text.insert(tk.END, "-" * 40 + "\n")

    # Messagebox summary
    intact_count = sum("is intact" in r for r in integrity_results)
    tampered_count = len(integrity_results) - intact_count

    summary_message = f"Integrity check complete: {intact_count} intact, {tampered_count} tampered."
    messagebox.showinfo("Integrity Check Results", summary_message)

# Function to open Logger window
def open_logger():
    app.withdraw()  # Hide the main menu window
    logger_window = tk.Toplevel(app)
    logger_window.title("Logger")

    tk.Label(logger_window, text="Hostname:").grid(row=0, column=0, padx=10, pady=5)
    global hostname_entry
    hostname_entry = tk.Entry(logger_window)
    hostname_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(logger_window, text="Action Taken:").grid(row=1, column=0, padx=10, pady=5)
    global action_entry
    action_entry = tk.Entry(logger_window)
    action_entry.grid(row=1, column=1, padx=10, pady=5)

    log_button = tk.Button(logger_window, text="Log Action", command=log_action)
    log_button.grid(row=2, column=0, columnspan=2, pady=10)

    # When the logger window is closed, reopen the menu
    logger_window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(logger_window))

# Function to open Viewer window
def open_viewer():
    app.withdraw()  # Hide the main menu window
    viewer_window = tk.Toplevel(app)
    viewer_window.title("Viewer")

    global log_text
    log_text = scrolledtext.ScrolledText(viewer_window, wrap=tk.WORD, width=50, height=20)
    log_text.pack(pady=10)

    load_button = tk.Button(viewer_window, text="Load Logs", command=load_logs)
    load_button.pack(pady=5)

    integrity_button = tk.Button(viewer_window, text="Check Log Integrity", command=open_log_integrity)
    integrity_button.pack(pady=5)

    # When the viewer window is closed, reopen the menu
    viewer_window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(viewer_window))

# Function to reopen the main menu when a window is closed
def on_window_close(window):
    window.destroy()  # Close the current window
    app.deiconify()   # Show the main menu again

# Create the main menu window
app = tk.Tk()
app.title("Maintenance Log Menu")

tk.Label(app, text="Select an Application", font=('Helvetica', 14)).pack(pady=20)

# Button to open the Logger
logger_button = tk.Button(app, text="Open Logger", command=open_logger, width=20)
logger_button.pack(pady=10)

# Button to open the Viewer
viewer_button = tk.Button(app, text="Open Viewer", command=open_viewer, width=20)
viewer_button.pack(pady=10)

app.mainloop()
