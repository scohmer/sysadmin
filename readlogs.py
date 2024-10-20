import json
import tkinter as tk
from tkinter import scrolledtext

# Path to the JSON file
json_file_path = "maintenance_logs.json"

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
        log_text.insert(tk.END, "-" * 40 + "\n")

# Set up the GUI
app = tk.Tk()
app.title("Maintenance Log Viewer")

log_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=50, height=20)
log_text.pack(pady=10)

load_button = tk.Button(app, text="Load Logs", command=load_logs)
load_button.pack(pady=5)

app.mainloop()
