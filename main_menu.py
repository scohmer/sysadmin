import tkinter as tk
import subprocess
import os

# Function to launch the logger application
def open_logger():
    logger_path = os.path.join(os.path.dirname(__file__), 'logger_app.exe')
    subprocess.Popen([logger_path], shell=True)

# Function to launch the viewer application
def open_viewer():
    viewer_path = os.path.join(os.path.dirname(__file__), 'viewer_app.exe')
    subprocess.Popen([viewer_path], shell=True)

# Create the main menu window
def main_menu():
    menu_app = tk.Tk()
    menu_app.title("Maintenance Log Menu")

    # Label for the menu
    tk.Label(menu_app, text="Select an Application", font=('Helvetica', 14)).pack(pady=20)

    # Button to open the logger
    logger_button = tk.Button(menu_app, text="Open Logger", command=open_logger, width=20)
    logger_button.pack(pady=10)

    # Button to open the viewer
    viewer_button = tk.Button(menu_app, text="Open Viewer", command=open_viewer, width=20)
    viewer_button.pack(pady=10)

    menu_app.mainloop()

# Run the main menu
if __name__ == "__main__":
    main_menu()
