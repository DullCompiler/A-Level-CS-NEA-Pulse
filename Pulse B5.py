# Pulse Beta 5 | Made by Alexander Richard Dennant | NEA Project for Computer Science

# Imports —————————————————————————————————————————————
import time
import sqlite3
import itertools
import threading
import requests
import asyncio
from shazamio import Shazam, Serialize
from customtkinter import CTk as ctk
from tkinter import messagebox, filedialog, PhotoImage
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkImage
import sqlite3

# Global Variables —————————————————————————————————————————————
verbose = False # Verbose Mode

# Classes —————————————————————————————————————————————

# StartupMenu Class —————————————————————————————————————————————
class StartupMenu: # StartupMenu class defines the startup menu of the application
    def __init__(self): 
        self.title_label = None 
        self.button_frame = None 
        self.related_songs = [] 
        self.processing = False 
        self.subtitle_label = None 
        self.identified_song = "" 
        self.internet_connected = True
        self.song_details_list = []

    # Creates GUI —————————————————————————————————————————————

    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = ctk() # Create the Tkinter root window
        self.ctk_root.after(0, self.check_internet)  # Call the check_internet method
        self.ctk_root.title("PULSE: Startup Menu") # Set the title of the window
        self.ctk_root.resizable(False, False) # Disable resizing of the window
        self.center_window(500, 240) # Center the window on the screen

        self.title_label = CTkLabel(self.ctk_root, text="PULSE", font=("Helvetica", 30, "bold")) # Create the title label
        self.title_label.pack(padx=20, pady=(20, 0)) # Pack the title label with padding

        self.subtitle_label = CTkLabel(self.ctk_root, text="Startup menu", font=("Helvetica", 12)) # Create the subtitle label
        self.subtitle_label.pack(padx=20, pady=(0, 20)) # Pack the subtitle label with padding

        self.internet_label = CTkLabel(self.ctk_root, text="Internet: Validating", font=("Helvetica", 10)) # Create the internet status label
        self.internet_label.pack(padx=20, pady=(0, 20)) # Pack the internet status label with padding

        self.button_frame = CTkFrame(self.ctk_root) # Create a frame for the buttons
        self.button_frame.pack(side="bottom", pady=20) # Pack the button frame at the bottom of the window with padding

        CTkButton(self.button_frame, text='Exit', command=self.exit_program).pack(side="left", padx=(0, 5)) # Create and pack the 'Exit' button, which calls the exit_program method when clicked
        CTkButton(self.button_frame, text='Open File', command=self.open_file).pack(side="left", padx=(5, 5)) # Create and pack the 'Open File' button, which calls the open_file method when clicked
        CTkButton(self.button_frame, text='Verbose Mode', command=self.verbose_mode).pack(side="left", padx=(5, 0)) # Create and pack the 'Open URL' button, which calls the open_url method when clicked

        self.ctk_root.mainloop() # Start the Tkinter event loop

    def verbose_mode(self):  # developer_menu method opens the developer menu
        global verbose  # Global variable
        verbose = not verbose  # Toggle the verbose variable
        if verbose == True: # If verbose mode is enabled, print a message to the console
            print("Startup Menu Debug Mode Enabled")  # Print a message to the console
        else: # If verbose mode is disabled, print a message to the console
            print("Startup Menu Debug Mode Disabled")  # Print a message to the console

    def center_window(self, width=500, height=240): # center_window method centers the window on the screen
        screen_width = self.ctk_root.winfo_screenwidth() # Get the screen width and height
        screen_height = self.ctk_root.winfo_screenheight() # Get the screen width and height
        x = (screen_width / 2) - (width / 2) # Calculate the x coordinate to center the window
        y = (screen_height / 2) - (height / 2) # Calculate the y coordinate to center the window
        self.ctk_root.geometry('%dx%d+%d+%d' % (width, height, x, y)) # Set the geometry of the window to center it on the screen
    
    def animate_processing_label(self):
        dots = itertools.cycle([".", "..", "..."])
        while self.processing:
            text = f"Processing {next(dots)}"
            self.internet_label.configure(text=text)
            self.ctk_root.update()
            time.sleep(0.5)

    # Internet Connection Check —————————————————————————————————————————————

    def update_internet_label(self): # update_internet_label method updates the text of the internet label
        if self.internet_connected and self.internet_label.winfo_exists(): # If the internet is connected and the internet label exists, update the text
            text = "Internet: Connected" # Set the text of the internet label
            self.ctk_root.after(0, lambda: self.internet_label.configure(text=text)) # Update the text of the internet label

    def exit_program(self): # exit_program method exits the program
        self.ctk_root.destroy() # Destroy the window

    def check_internet(self): # check_internet method checks the internet connection
        try: # Try to send a GET request to google.com
            r = requests.get('http://google.com') # Send the GET request
            self.internet_connected = r.status_code == 200 # Set the internet_connected variable to True if the status code of the response is 200
        except requests.exceptions.RequestException: # If the request fails, set the internet_connected variable to False
            self.internet_connected = False # Set the internet_connected variable to False

        if not self.internet_connected: # If the internet is not connected, show an error message and exit the program
            self.show_error_and_exit()  # Call the show_error_and_exit method with an empty tuple as the argument

        self.update_internet_label()  # Call the update_internet_label method

    def show_error_and_exit(self): # show_error_and_exit method shows an error message and exits the program
        messagebox.showerror("Error 01 : No Internet", "Error 01 : No Internet | Please connect to the internet and restart the application.") # Show an error message
        self.ctk_root.quit()  # Stop the mainloop
        self.ctk_root.destroy()  # Destroy the window  

    # File Dialog —————————————————————————————————————————————

    def open_file(self): # open_file method opens a file dialog and calls the recognize_song method
        filepath = filedialog.askopenfilename() # Open a file dialog and get the filepath
        if filepath: # If a file is selected, call the recognize_song method
            if filepath.endswith('.mp3'): # If the file is an MP3 file, call the recognize_song method
                if verbose == True: # If verbose mode is enabled, print the filepath to the console
                    print(f"File opened: {filepath}") # Print the filepath to the console
                self.processing = True # Set the processing variable to True
                self.ctk_root.after(0, self.animate_processing_label) # Call the animate_processing_label method
                threading.Thread(target=self.run_recognize_song_in_thread, args=(filepath, verbose)).start() # Create a new thread to call the recognize_song method
            else: # If the file is not an MP3 file, show an error message
                messagebox.showwarning("Error 02: Invalid File", "Error 02: Invalid File | Please select an MP3 file.") # If no file is selected, show a warning message

    # Runs the Song Recognition and Grab Related Songs —————————————————————————————————————————————

    def run_recognize_song_in_thread(self, filepath, verbose): # run_recognize_song_in_thread method runs the recognize_song method in a new thread
        self.processing = True
        thread = threading.Thread(target=self.thread_target, args=(filepath, verbose)) # Create a new thread to call the thread_target method
        thread.start() # Start the thread

    def thread_target(self, filepath, verbose):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.recognize_song(filepath, verbose))
        finally:
            loop.close()

    async def recognize_song(self, filepath, verbose): # recognize_song method recognizes the song from the given filepath
        shazam = Shazam() # Create a new instance of the Shazam class
        track = await self.fetch_track(shazam, filepath)
        await self.fetch_related_tracks(shazam, track, verbose)

    async def fetch_track(self, shazam, filepath): # fetch_track method recognizes the song from the given filepath
        out = await shazam.recognize_song(filepath) # Call the recognize_song method of the Shazam class
        track = out['track'] # Get the track from the output
        self.identified_song = self.format_song_details(track) # Format the song details and set the identified_song variable
        if verbose: # If verbose mode is enabled, print the identified song to the console
            print(self.identified_song) # Print the identified song to the console
        return track # Return the track

    async def fetch_related_tracks(self, shazam, track, verbose): # fetch_related_tracks method fetches related songs from the Shazam API
        related = await shazam.related_tracks(track_id=track['key'], limit=5, offset=0) # Call the related_tracks method of the Shazam class
        for related_track in related.get('tracks', []): # Iterate through the related tracks
            full_track_info = await shazam.track_about(track_id=related_track['key']) # Call the track_about method of the Shazam class
            song_details = self.format_song_details(full_track_info) # Format the song details
            if verbose == True: # If verbose mode is enabled, print the related song to the console
                print(song_details) # Print the related song to the console
            await self.search_youtube(related_track['title'], related_track['subtitle']) # Call the search_youtube method to search for the song on YouTube
        self.processing = False # Set the processing variable to False
        self.ctk_root.after(0, self.transition_to_main_window) # Call the transition_to_main_window method

    def format_song_details(self, track): # format_song_details method formats the song details into a string
        album_name = 'Unknown Album' # Album name
        primary_genre = 'Unknown Genre' # Primary genre
        album_cover = 'Unknown Cover' # Album cover
        
        for section in track.get('sections', []): # Iterate through the sections of the track
            if 'metadata' in section: # If the section contains metadata, iterate through the metadata
                for metadata_item in section['metadata']: # Iterate through the metadata items
                    if metadata_item.get('title').lower() == 'album': # If the title of the metadata item is 'album', set the album name
                        album_name = metadata_item.get('text', album_name) # Set the album name
        
        primary_genre = track.get('genres', {}).get('primary', primary_genre) # Get the primary genre of the track

        images = track.get('images', {}) # Get the images of the track
        album_cover = images.get('coverarthq', album_cover) # Get the album cover of the track

        song_details = f"{track.get('title', 'Unknown Title')} by {track.get('subtitle', 'Unknown Artist')}" # Format the song details
        if album_name != 'Unknown Album': # If the album name is not 'Unknown Album', add it to the song details
            song_details += f" | Album: {album_name}" # Return the formatted song details
        if primary_genre != 'Unknown Genre': # If the primary genre is not 'Unknown Genre', add it to the song details
            song_details += f" | Genre {primary_genre}" # Return the formatted song details
        if album_cover != 'Unknown Cover': # If the album cover is not 'Unknown Cover', add it to the song details
            song_details += f" | Album Cover {album_cover}" # Return the formatted song details

        #Adding to Database
        connection=sqlite3.connect("PulseDatabase.db")
        cursor=connection.cursor()
        cursor.execute("INSERT INTO Songs (Song_Title, Song_Album, Song_Artist, Song_Genre, Cover_Art_URL) VALUES (?, ?, ?, ?, ?)", (track.get('title', 'Unknown Title'), album_name, track.get('subtitle', 'Unknown Artist'), primary_genre, album_cover))
        connection.commit()
        connection.close()
        
        self.song_details_list.append(song_details) # Append the song data to the song details list
        return song_details # Return the formatted song details

    async def search_youtube(self, title, artist): # search_youtube method searches for the song on YouTube
        query = f"{title} {artist}" # Create a query for the song
        try: # Try to send a GET request to the YouTube API
            params = { # Set the parameters for the YouTube API request
                'part': 'snippet', 
                'q': query, 
                'maxResults': 1,
                'type': 'video',
                'key': 'insert youtube api key'
            }
            response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params) # Send the GET request to the YouTube API
            response.raise_for_status() # Raise an exception if the status code of the response is not 200
            data = response.json() # Get the JSON data from the response
            self.youtube_link = f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}" if data['items'] else 'No YouTube results found.' # Get the YouTube link from the JSON data
            if verbose == True: # If verbose mode is enabled, print the YouTube link to the console
                print("YouTube Link:", self.youtube_link) # Print the YouTube link to the console
            connection=sqlite3.connect("PulseDatabase.db")
            cursor=connection.cursor()
            cursor.execute("UPDATE Songs SET Youtube_URL = ? WHERE Song_Title = ?", (self.youtube_link, title))
            connection.commit()
            connection.close()
        except requests.exceptions.RequestException as e: # If the request fails, show an error message
            messagebox.showwarning("YouTube API Error", "Error: Please try again. (This may be an API limit reached; if so, please wait for servers to reset)") # Show a warning message
            if verbose == True: # If verbose mode is enabled, print the error to the console
                print(f'An error occurred: {e}') # Print the error to the console

    # Transition to Main Window —————————————————————————————————————————————
    
    def transition_to_main_window(self): # transition_to_main_window method transitions to the main window
        if verbose: # If verbose mode is enabled, print two messages to the console
            print("Disabling Startup Menu Verbose Mode") # Print a message to the console
            print("Starting Main Window") # Print a message to the console
        self.ctk_root.destroy()  # Close the startup menu window
        main_window = MainWindow()  # Assuming MainWindow is similar structure to StartupMenu
        main_window.create_window()  # Here you define the GUI setup for Main Window just like in StartupMenu

# StartupMenu Class End —————————————————————————————————————————————

# MainWindow Class —————————————————————————————————————————————
class MainWindow(): # MainWindow class defines the main window of the application
    verbose = False # Verbose Mode
    def __init__(self): # Constructor initializes all the necessary UI components to None
        self.title_label = None # Title label
        self.button_frame = None # Button frame
        self.related_songs = [] # Related songs
        self.subtitle_label = None # Subtitle label
        self.identified_song = "" # Identified song
        self.internet_connected = True # Internet connection status
        
    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = ctk() # Create the Tkinter root window
        self.ctk_root.title("PULSE: Main Window")
        self.ctk_root.resizable(False, False)
        
        screen_width = self.ctk_root.winfo_screenwidth()
        screen_height = self.ctk_root.winfo_screenheight()
        window_width = int(screen_width * 2 / 3)
        window_height = int(screen_height * 2 / 3)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.ctk_root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        #Top Bar --------------------------------------------------------------------------------
        frame = CTkFrame(self.ctk_root) # Create a frame for the title and buttons
        frame.pack(anchor="n", padx=10, pady=5, fill="both", expand=False) # Pack the frame at the top of the window with padding

        self.title_label = CTkLabel(frame, text="PULSE AUDIO | Main Window", font=("Helvetica", 30, "bold")) # Create the title label
        self.title_label.pack(side="left", padx=10, pady=10) # Pack the title label with padding

        self.button = CTkButton(frame, text="Verbose Mode", command=self.verbose_mode) # Create the button
        self.button.pack(side="right", padx=10, pady=10) # Pack the button with padding
        
        #Top Bar End --------------------------------------------------------------------------------
        
        # Main Frame --------------------------------------------------------------------------------
        main_frame = CTkFrame(self.ctk_root) # Create a frame for the main content
        main_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        self.ctk_root.mainloop() # Start the Tkinter event loop

    def verbose_mode(self):  # developer_menu method opens the developer menu
        global verbose  # Global variable
        verbose = not verbose  # Toggle the verbose variable
        if verbose == True: # If verbose mode is enabled, print a message to the console
            print("Main Menu Debug Mode Enabled")  # Print a message to the console
        else: # If verbose mode is disabled, print a message to the console
            print("Main Menu Debug Mode Disabled")  # Print a message to the console

# MainWindow Class End —————————————————————————————————————————————

# Main ————————————————————————————————————————————
if __name__ == "__main__": # Program Start (Calling Window)
    startup_menu = StartupMenu() # Create a new StartupMenu object
    startup_menu.create_window() # Call the create_window method to create and display the windows
