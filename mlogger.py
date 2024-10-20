import tkinter as tk
from tkinter import messagebox
import json
import csv
from datetime import datetime
import getpass
import os

# Paths for the files
json_file_path = "maintenance_logs.json"
csv_file_path = "maintenance_logs.csv"

# Function to log actions
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
        fieldnames = ["hostname", "action_taken", "username", "timestamp"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(log_entry)

    # Success message and clear inputs
    messagebox.showinfo("Success", "Action logged successfully!")
    hostname_entry.delete(0, tk.END)
    action_entry.delete(0, tk.END)

# Set up the GUI
app = tk.Tk()
app.title("Maintenance Logging System")

tk.Label(app, text="Hostname:").grid(row=0, column=0, padx=10, pady=5)
hostname_entry = tk.Entry(app)
hostname_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(app, text="Action Taken:").grid(row=1, column=0, padx=10, pady=5)
action_entry = tk.Entry(app)
action_entry.grid(row=1, column=1, padx=10, pady=5)

log_button = tk.Button(app, text="Log Action", command=log_action)
log_button.grid(row=2, column=0, columnspan=2, pady=10)

app.mainloop()
