import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import csv
from datetime import datetime
import getpass
import os

# Paths for the files (adjust these as necessary)
json_file_path = "maintenance_logs.json"
csv_file_path = "maintenance_logs.csv"


# Function for the main menu
def main_menu():
    menu_app = tk.Tk()
    menu_app.title("Maintenance Log Menu")

    # Label for the menu
    tk.Label(menu_app, text="Select an Application", font=('Helvetica', 14)).pack(pady=20)

    # Button to open the logger
    logger_button = tk.Button(menu_app, text="Open Logger", command=lambda: open_logger(menu_app), width=20)
    logger_button.pack(pady=10)

    # Button to open the viewer
    viewer_button = tk.Button(menu_app, text="Open Viewer", command=lambda: open_viewer(menu_app), width=20)
    viewer_button.pack(pady=10)

    menu_app.mainloop()


# Logger application
def open_logger(root):
    root.destroy()  # Close the main menu window

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

    # Set up the Logger GUI
    logger_app = tk.Tk()
    logger_app.title("Logger")

    tk.Label(logger_app, text="Hostname:").grid(row=0, column=0, padx=10, pady=5)
    hostname_entry = tk.Entry(logger_app)
    hostname_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(logger_app, text="Action Taken:").grid(row=1, column=0, padx=10, pady=5)
    action_entry = tk.Entry(logger_app)
    action_entry.grid(row=1, column=1, padx=10, pady=5)

    log_button = tk.Button(logger_app, text="Log Action", command=log_action)
    log_button.grid(row=2, column=0, columnspan=2, pady=10)

    logger_app.mainloop()


# Viewer application
def open_viewer(root):
    root.destroy()  # Close the main menu window

    def load_logs():
        if not os.path.exists(json_file_path):
            messagebox.showerror("Error", "No log file found!")
            return

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
            log_text.insert(tk.END, "-" * 40 + "\n")

    # Set up the Viewer GUI
    viewer_app = tk.Tk()
    viewer_app.title("Viewer")

    log_text = scrolledtext.ScrolledText(viewer_app, wrap=tk.WORD, width=50, height=20)
    log_text.pack(pady=10)

    load_button = tk.Button(viewer_app, text="Load Logs", command=load_logs)
    load_button.pack(pady=5)

    viewer_app.mainloop()


# Run the main menu
if __name__ == "__main__":
    main_menu()
