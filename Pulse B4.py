# Pulse Beta 4 | Made by Alexander Richard Dennant | NEA Project for Computer Science

# Imports —————————————————————————————————————————————

import time # Time
import asyncio # Asynchronous I/O
import tracemalloc
import requests # HTTP Requests
import threading # Threading
from shazamio import Shazam # Shazam API
from customtkinter import CTk as ctk # Custom Tkinter
from tkinter import filedialog, messagebox # Tkinter File Dialog and Message Box
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTk # Custom Tkinter

# Classes —————————————————————————————————————————————

class MemoryChecker(threading.Thread): # MemoryChecker class checks the memory usage of the program
    def __init__(self): # Constructor initializes the running variable to False
        super().__init__() # Call the constructor of the Thread class
        self.running = False # Set the running variable to False

    def run(self): # run method starts the MemoryChecker thread
        self.running = True # Set the running variable to True
        tracemalloc.start() # Start the tracemalloc profiler
        while self.running: # While the running variable is True, print the current and peak memory usage to the console
            current, peak = tracemalloc.get_traced_memory() # Get the current and peak memory usage
            print(f"Current memory usage is {current / 10**6:.2f}MB; Peak was {peak / 10**6:.2f}MB") # Print the current and peak memory usage to the console
            time.sleep(1) # Sleep for 1 second

    def stop(self): # stop method stops the MemoryChecker thread
        self.running = False # Set the running variable to False
        tracemalloc.stop() # Stop the tracemalloc profiler

# StartupMenu Class —————————————————————————————————————————————

class StartupMenu: # StartupMenu class defines the startup menu of the application
    def __init__(self): # Constructor initializes all the necessary UI components to None
        self.title_label = None # Title label
        self.subtitle_label = None # Subtitle label
        self.button_frame = None # Button frame
        self.internet_connected = True # Internet connection status
        self.mem_checker = MemoryChecker() # MemoryChecker thread
        self.mem_checker.start() # Start the MemoryChecker thread

    def stop_mem_checker(self): 
        self.mem_checker.stop()  # Stop the MemoryChecker thread
        self.ctk_root.quit()  # Stop the Tkinter mainloop
        self.ctk_root.destroy()  # Destroy the window
            
    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = ctk() # Create the Tkinter root window
        self.ctk_root.protocol("WM_DELETE_WINDOW", self.stop_mem_checker) # Call the stop_mem_checker method when the window is closed
        self.ctk_root.after(1500, self.check_internet)  # Check the internet connection after 5 seconds
        self.ctk_root.title("PULSE: Startup Menu") # Set the title of the window
        self.ctk_root.resizable(False, False) # Disable resizing of the window
        self.center_window(500, 240) # Center the window on the screen
        
        self.title_label = CTkLabel(self.ctk_root, text="PULSE", font=("Helvetica", 30, "bold")) # Create the title label
        self.title_label.pack(padx=20, pady=(20, 0)) # Pack the title label with padding
        
        self.subtitle_label = CTkLabel(self.ctk_root, text="Startup menu", font=("Helvetica", 12)) # Create the subtitle label
        self.subtitle_label.pack(padx=20, pady=(0, 20)) # Pack the subtitle label with padding
        
        self.internet_label = CTkLabel(self.ctk_root, text="Internet: Checking...", font=("Helvetica", 10)) # Create the internet status label
        self.internet_label.pack(padx=20, pady=(0, 20)) # Pack the internet status label with padding

        self.button_frame = CTkFrame(self.ctk_root) # Create a frame for the buttons
        self.button_frame.pack(side="bottom", pady=20) # Pack the button frame at the bottom of the window with padding

        CTkButton(self.button_frame, text='Exit', command=self.exit_program).pack(side="left", padx=(0, 5)) # Create and pack the 'Exit' button, which calls the exit_program method when clicked
        CTkButton(self.button_frame, text='Open File', command=self.open_file).pack(side="left", padx=(5, 0)) # Create and pack the 'Open File' button, which calls the open_file method when clicked

        self.ctk_root.mainloop() # Start the Tkinter event loop

    def center_window(self, width=500, height=240): # center_window method centers the window on the screen
        screen_width = self.ctk_root.winfo_screenwidth() # Get the screen width and height
        screen_height = self.ctk_root.winfo_screenheight() # Get the screen width and height
        x = (screen_width / 2) - (width / 2) # Calculate the x coordinate to center the window
        y = (screen_height / 2) - (height / 2) # Calculate the y coordinate to center the window
        self.ctk_root.geometry('%dx%d+%d+%d' % (width, height, x, y)) # Set the geometry of the window to center it on the screen

    def display_song_message(self, state=0): # display_song_message method displays the "Processing song and getting recommendations" message
        states = [".", "..", "..."] # List of states
        state = (state + 1) % len(states) # Increment the state
        self.internet_label.configure(text=f"Processing song and getting recommendations{states[state]}") # Update the internet status label
        state = (state + 1) % len(states) # Increment the state
        self.ctk_root.after(500, self.display_song_message, state) # Call the display_song_message method after 500ms

    def exit_program(self): # exit_program method exits the program
        self.ctk_root.destroy() # Destroy the window
        self.mem_checker.stop() # Stop the MemoryChecker thread

    def check_internet(self): # check_internet method checks the internet connection
        thread = threading.Thread(target=self._check_internet) # Create a new thread to check the internet connection
        thread.daemon = True  # Set the daemon attribute to True
        thread.start()  # Start the thread

    def _check_internet(self): # _check_internet method checks the internet connection
        try: # Try to send a GET request to google.com
            r = requests.get('http://google.com', timeout=5) # Send the GET request
            self.internet_connected = r.status_code == 200 # Set the internet_connected variable to True if the status code of the response is 200
        except requests.exceptions.RequestException: # If the request fails, set the internet_connected variable to False
            self.internet_connected = False # Set the internet_connected variable to False

        if not self.internet_connected: # If the internet is not connected, show an error message and exit the program
            self.ctk_root.after(0, self.show_error_and_exit) # Call the show_error_and_exit method

        self.update_internet_label()  # Call the update_internet_label method

    def show_error_and_exit(self, mem_checker): # show_error_and_exit method shows an error message and exits the program
        messagebox.showerror("Error 01 : No Internet", "Error 01 : No Internet | Please connect to the internet and restart the application.") # Show an error message
        mem_checker.stop()
        self.ctk_root.quit()  # Stop the mainloop
        self.ctk_root.destroy()  # Destroy the window  
            
    def update_internet_label(self): # update_internet_label method updates the internet status label
        if self.internet_connected: # If the internet is connected, set the text of the label to "Internet: Connected"
            text = "Internet: Connected" # Set the text of the label to "Internet: Connected"
            self.ctk_root.after(0, lambda: self.internet_label.configure(text=text)) # Update the internet status label

    def open_file(self): # open_file method opens a file dialog to select an MP3 file
        filepath = filedialog.askopenfilename()  # Open the file dialog and get the selected file path
        if filepath:  # If a file was selected
            print(f"File opened: {filepath}") # Print the filepath to the console
            threading.Thread(target=self.recognize_song, args=(filepath,)).start()  # Start a new thread to process the file
            self.display_song_message()  # Start displaying the "Processing song and getting recommendations" message
            self.ctk_root.update()  # Update the GUI
            if filepath.endswith('.mp3'): # Check if the file is an MP3 file
                print(f"File opened: {filepath}") # Print the filepath to the console
                asyncio.run(self.recognize_song(filepath)) # Call the recognize_song method
            else: # If the file is not an MP3 file, show a warning message
                messagebox.showwarning("Invalid File", "Error 02: Invalid File | Please select an MP3 file.") # If no file is selected, show a warning message
        
    async def recognize_song(self, filepath): # recognize_song method uses the Shazam API to recognize the song
        shazam = Shazam() # Create a new Shazam object

        out = await shazam.recognize_song(filepath) # Call the Shazam API to recognize the song

        track = out['track'] # Get the track data from the response
        print(f"Title: {track['title']}, Artist: {track['subtitle']}") # Print the title and artist of the song to the console

        related = await shazam.related_tracks(track_id=track['key'], limit=5, offset=0) # Get the related tracks from the response
        for related_track in related['tracks']: # Loop through each related track
            title = related_track['title'] # Get the title and artist of each related song
            artist = related_track['subtitle'] # Get the title and artist of each related song
            print(f"\nRelated song: {title} by {artist}") # Print the title and artist of each related song to the console

            results = self.search_youtube(f"{title} {artist}") # Search YouTube for the related song
            if results: # If results are found, print the first result to the console
                print("Youtube Link: " + results[0]) # Print the first result to the console
            else: # If no results are found, print an error message to the console
                print('No YouTube results found.') # Print an error message to the console
        
        self.transition_to_main_window() # Transition to the main window

    def search_youtube(self, query): # search_youtube method searches YouTube for a query and returns the first result
        try: # Try to send a GET request to the YouTube API
            params = { # Set the parameters of the GET request
                'key': 'AIzaSyDQ4pqmgDr0niIQvT0aPPte5Ew7yZg5Q04',
                'part': 'snippet',
                'q': query,
                'maxResults': 1,
                'type': 'video'
            }

            response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params) # Send the GET request
            response.raise_for_status() # Raise an exception if the status code of the response is not 200

            data = response.json() # Get the JSON data from the response

            results = [f'https://www.youtube.com/watch?v={item["id"]["videoId"]}' for item in data['items']] # Get the first result from the JSON data

            return results # Return the first result
        except requests.exceptions.RequestException as e: # If the request fails, print an error message to the console
            print(f'An error occurred: {e}') # Print an error message to the console
            return None # Return None

    def transition_to_main_window(self): # transition_to_main_window method destroys the current window and creates a new MainWindow object
        if self.ctk_root: # If the window exists, destroy it and create a new MainWindow object
            self.ctk_root.destroy() # Destroy the window
            main_window = MainWindow() # Create a new MainWindow object
            main_window.create_window() # Call the create_window method to create and display the window

# StartupMenu Class End —————————————————————————————————————————————

# MainWindow Class —————————————————————————————————————————————

class MainWindow: # MainWindow class defines the main window of the application
    def __init__(self): # Constructor initializes all the necessary UI components to None
        self.width = 0 # Width of the window
        self.height = 0 # Height of the window

    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = CTk() # Create the Tkinter root window
        self.ctk_root.title("PULSE: Main Window") # Set the title of the window
        self.ctk_root.resizable(False, False) # Disable resizing of the window

        self.width = int(self.ctk_root.winfo_screenwidth() * 2 / 3) # Set the window size to 2/3 of the screen size
        self.height = int(self.ctk_root.winfo_screenheight() * 2 / 3) # Set the window size to 2/3 of the screen size
        self.ctk_root.geometry(f"{self.width}x{self.height}") # Set the geometry of the window

        self.center_window() # Center the window on the screen

        self.ctk_root.mainloop() # Start the Tkinter event loop

    def center_window(self): # center_window method centers the window on the screen
        screen_width = int(self.ctk_root.winfo_screenwidth()) # Get the screen width and height
        screen_height = int(self.ctk_root.winfo_screenheight()) # Get the screen width and height
        x = (screen_width - self.width) // 2 # Calculate the x and y coordinates to center the window
        y = (screen_height - self.height) // 2 # Calculate the x and y coordinates to center the window
        self.ctk_root.geometry(f"+{x}+{y}") # Set the geometry of the window to center it on the screen
# MainWindow Class End —————————————————————————————————————————————

# Main —————————————————————————————————————————————

memcheck = True
tracemalloc.start() # Start the tracemalloc profiler
if __name__ == "__main__": # Program Start (Calling Window)
    startup_menu = StartupMenu() # Create a new StartupMenu object
    startup_menu.create_window() # Call the create_window method to create and display the window