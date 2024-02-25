# Pulse Beta 1 | Made by Alexander Richard Dennant | NEA Project for Computer Science

# Imports ------------------------------------------------------------------------------------------------------
import requests                                            # For the check internet function
from tkinter import filedialog                             # For the open file function
from tkinter import messagebox                             # For the warning message about Internet Connectivity
from customtkinter import CTk as ctk                       # Main class for CustomTkinter (ctk), seems to be used for creating the UI (ctk_root)
from customtkinter import CTkLabel, CTkButton, CTkFrame    # Components from CustomTkinter (ctk)

# Start Up Menu ------------------------------------------------------------------------------------------------

# Check internet connectivity 
def check_internet():
    try:
        r = requests.get('http://google.com')
        return r.status_code == 200
    except:
        return False

# Define functions for each button
def open_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        print(f"File opened: {filepath}")

def save_file():
    filepath = filedialog.asksaveasfilename(defaultextension=".txt")
    if filepath:
        print(f"File saved: {filepath}")

def exit_program():
    ctk_root.destroy()

def center_window(width=500, height=240):
    # get screen width and height
    screen_width = ctk_root.winfo_screenwidth()
    screen_height = ctk_root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    ctk_root.geometry('%dx%d+%d+%d' % (width, height, x, y))


ctk_root = ctk()
ctk_root.title("PULSE: Startup Menu")
#ctk_root.geometry("500x240") - this line is no needed as center_window function will take care of geometry
ctk_root.resizable(False,False)

# Use the center_window function instead of the previous line
center_window(500, 240)

# Title and subtitle
title_label = CTkLabel(ctk_root, text="PULSE", font=("Helvetica", 30, "bold"))
title_label.pack(padx=20, pady=(20, 0))

subtitle_label = CTkLabel(ctk_root, text="Startup menu", font=("Helvetica", 12))
subtitle_label.pack(padx=20, pady=(0, 20))

# Internet connection status
internet_label = CTkLabel(ctk_root, text="", font=("Helvetica", 10, "bold"))

if check_internet():
    internet_label.configure(text="Internet: Connected")
else:
    messagebox.showwarning("No Internet", "Error 01 : No Internet | Pulse requires an active internet connection in order to enable necessary functionalty")
    exit_program()

internet_label.pack(padx=20, pady=20)

# Buttons
button_frame = CTkFrame(ctk_root)
button_frame.pack(side="bottom", pady=20)

CTkButton(button_frame, text='Exit', command=exit_program).pack(side="left", padx=(0, 10))
CTkButton(button_frame, text='Open File', command=open_file).pack(side="left", padx=10)
CTkButton(button_frame, text='New File', command=save_file).pack(side="left", padx=(10, 0))

ctk_root.mainloop()

#End of Start Up Menu ------------------------------------------------------------------------------------------
