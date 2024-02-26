# Pulse Beta 9 | Made by Alexander Richard Dennant | NEA Project for Computer Science

# Imports —————————————————————————————————————————————
import os
import re
import time
import librosa
import asyncio
import sqlite3
import requests
import itertools
import threading
import numpy as np
import soundfile as sf
from io import BytesIO
from pytube import YouTube
from shazamio import Shazam
from PIL import ImageTk, Image
from pydub import AudioSegment
from customtkinter import CTk as ctk
from tkinter import messagebox, filedialog
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkImage, CTkSlider, CTkCheckBox

# Global Variables —————————————————————————————————————————————
verbose = False # Verbose Mode

# Clear Database —————————————————————————————————————————————
connection=sqlite3.connect("PulseDatabase.db") # Connect to the database
cursor=connection.cursor() # Create a cursor object
cursor.execute("DELETE FROM Songs") # Clear the Songs table
connection.commit() # Commit the changes to the database
connection.close() # Close the connection to the database

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
        self.input_song_path = ""

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
    
    def animate_processing_label(self): # animate_processing_label method animates the processing label
        dots = itertools.cycle([".", "..", "..."]) # Create an iterator for the dots
        while self.processing: # While the processing variable is True, update the text of the internet label
            text = f"Processing {next(dots)}" # Set the text of the internet label
            self.internet_label.configure(text=text) # Update the text of the internet label
            self.ctk_root.update() # Update the window
            time.sleep(0.5) # Wait for 0.5 seconds

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
                self.input_song_path = filepath # Set the input song path
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

    def thread_target(self, filepath, verbose): # thread_target method runs the recognize_song method in a new thread
        loop = asyncio.new_event_loop() # Create a new event loop
        asyncio.set_event_loop(loop) # Set the event loop
        try: # Try to run the recognize_song method
            loop.run_until_complete(self.recognize_song(filepath, verbose)) # Call the recognize_song method
        finally: # Finally, close the event loop
            loop.close() # Close the event loop

    async def recognize_song(self, filepath, verbose): # recognize_song method recognizes the song from the given filepath
        shazam = Shazam() # Create a new instance of the Shazam class
        track = await self.fetch_track(shazam, filepath) # Call the fetch_track method
        await self.fetch_related_tracks(shazam, track, verbose) # Call the fetch_related_tracks method

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
        if verbose: # If verbose mode is enabled, print two messages to the console
            print("Disabling Startup Menu Verbose Mode") # Print a message to the console
            print("Enabling Download Window Verbose Mode") # Print a message to the console
            print("Starting Download Window") # Print a message to the console
        self.ctk_root.after(0, self.transition_to_download_window) # Call the transition_to_main_window method

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

        connection=sqlite3.connect("PulseDatabase.db") # Connect to the database
        cursor=connection.cursor() # Create a cursor object
        cursor.execute("INSERT INTO Songs (Song_Title, Song_Album, Song_Artist, Song_Genre, Cover_Art_URL) VALUES (?, ?, ?, ?, ?)", (track.get('title', 'Unknown Title'), album_name, track.get('subtitle', 'Unknown Artist'), primary_genre, album_cover)) # Insert the song details into the database
        cursor.execute("UPDATE Songs SET Song_File_Location = ? WHERE ID = (SELECT ID FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 5)", (self.input_song_path,)) # Update the YouTube link of the input song in the database
        connection.commit() # Commit the changes to the database
        connection.close()  # Close the connection to the database
        
        self.song_details_list.append(song_details) # Append the song data to the song details list
        return song_details # Return the formatted song details

    async def search_youtube(self, title, artist): # search_youtube method searches for the song on YouTube
        query = f"{title} {artist}" # Create a query for the song
        api_keys = [
            'AIzaSyCAO0MtrRSfn2Lt08jU07oFo6d_CUxzIhU',
            'AIzaSyBf0SA93_uXcsOHQJwcs6I2YAIzFCeVW2A',
            'AIzaSyCzXKaOWuLFERxAhq7yUMe4KktTArlHtyc',
            'AIzaSyC5dgqDjDWUWJbu9jsBWSGFjJqg9tca3Ok',
            'AIzaSyABeEZmMgFqmV2EF8st-hbrccZu0nEKuB8',
            'AIzaSyCq_1-AAdfj2L34nlJ7TEvesSeZ2AT-ZkM',
            'AIzaSyCHcHpDLI3dDbgZEX2rE_aGWUQ-bAXBp50',
            'AIzaSyBlMuxxJOv3baqGOqID_Mg36G4Ij9sbONI',
            'AIzaSyDkzmLTBaqrJ2qbEt9iu6cNQNLUBZNNkPs'
        ]
        for key in api_keys:
            try: # Try to send a GET request to the YouTube API
                params = { # Set the parameters for the YouTube API request
                    'part': 'snippet', 
                    'q': query, 
                    'maxResults': 1,
                    'type': 'video',
                    'key': key
                }
                response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params) # Send the GET request to the YouTube API
                response.raise_for_status() # Raise an exception if the status code of the response is not 200
                data = response.json() # Get the JSON data from the response
                self.youtube_link = f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}" if data['items'] else 'No YouTube results found.' # Get the YouTube link from the JSON data
                if verbose == True: # If verbose mode is enabled, print the YouTube link to the console
                    print("YouTube Link:", self.youtube_link) # Print the YouTube link to the console
                try:
                    connection=sqlite3.connect("PulseDatabase.db") # Connect to the database
                except: # If the connection to the database fails, show an error message
                    if verbose:
                        print("Error: Could not assign youtube URL to database")
                cursor=connection.cursor() # Create a cursor object
                cursor.execute("UPDATE Songs SET Youtube_URL = ? WHERE Song_Title = ?", (self.youtube_link, title)) # Update the YouTube link in the database
                connection.commit() # Commit the changes to the database
                connection.close() # Close the connection to the database
                break # Exit the loop if the API request is successful
            except requests.exceptions.RequestException as e: # If the request fails, show an error message
                if 'quotaExceeded' in str(e): # If the error is due to API limit exceeded
                    print("API limit exceeded. Trying backup key...")
                    continue # Try the next backup key
                else:
                    pass
                if verbose:
                    print(f"Error: {e}")

    # Transition to Download Window —————————————————————————————————————————————
    def transition_to_download_window(self): # transition_to_main_window method transitions to the main window
        self.ctk_root.destroy()  # Close the startup menu window
        download_window = DownloadWindow()  # Assuming MainWindow is similar structure to StartupMenu
        download_window.create_window()  # Here you define the GUI setup for Main Window just like in StartupMenu

# StartupMenu Class End —————————————————————————————————————————————

# DownloadWindow Class —————————————————————————————————————————————
class DownloadWindow(): # MainWindow class defines the main window of the application
    def __init__(self): # Constructor initializes all the necessary UI components to None
        self.title_label = None # Title label
        self.button_frame = None # Button frame
        self.related_songs = [] # Related songs
        self.subtitle_label = None # Subtitle label
        self.identified_song = "" # Identified song
        self.filepath = "" # Filepath
        
    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = ctk() # Create the Tkinter root window
        self.ctk_root.title("PULSE: Download Manager") # Set the title of the window
        self.ctk_root.resizable(True, True) # Disable resizing of the window
        screen_width = self.ctk_root.winfo_screenwidth()
        screen_height = self.ctk_root.winfo_screenheight()
        window_width = int(screen_width * 2 / 3)
        window_height = int(screen_height * 3 / 4)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.ctk_root.geometry(f"{window_width}x{window_height}+{x}+{y})") # Set the geometry of the window to center it on the screen

       # Gathering Song Data from Database —————————————————————————————————————————————
        
        connection=sqlite3.connect("PulseDatabase.db") # Connect to the database
        cursor=connection.cursor() # Create a cursor object

        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 5") # Gather the input song from the database
        input_song=cursor.fetchone()
        cursor.execute("UPDATE Songs SET Downloaded = 1 WHERE ID = ?", (input_song[0],)) # Update the YouTube link in the database

        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 4") # Gather the first related song from the database
        recsong1=cursor.fetchone()

        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 3") # Gather the second related song from the database
        recsong2=cursor.fetchone()

        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 2") # Gather the third related song from the database
        recsong3=cursor.fetchone()
        
        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 1") # Gather the fourth related song from the database
        recsong4=cursor.fetchone()

        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 0") # Gather the fifth related song from the database
        recsong5=cursor.fetchone()

        connection.commit() # Commit the changes to the database
        connection.close() # Close the connection to the database
        
        # Methods —————————————————————————————————————————————
        
        def load_image_from_url(url): # load_image_from_url method loads an image from a URL and returns it in a format that can be displayed
            try: # Try to load the image from the URL
                response = requests.get(url) # Send a GET request to the URL
                image = Image.open(BytesIO(response.content)) # Open the image from the URL
                image = image.resize((90, 90))  # Resize the image as per your requirements
                photo_image = ImageTk.PhotoImage(image) # Convert the image to a format that can be displayed
                return photo_image # Return the image
            except Exception as e: # If the image cannot be loaded, print an error message to the console
                print(f"Error loading image from URL: {e}") # Print the error to the console
                return None # Return None if the image cannot be loaded

        def download_audio(yturl, recsonginfo): # download_audio method downloads the audio of the related song from YouTube
            downloaded_song_name = recsonginfo[1] # Create the initial song name
            downloaded_song_name = (re.sub('[()]', '', recsonginfo[1])) # Create the initial song name
            filepath = filedialog.asksaveasfilename(initialfile=downloaded_song_name, defaultextension=".mp3", filetypes=(("MP3 Files", "*.mp3"),)) # Open a file dialog to select the download location
            if filepath: # If a file is selected, download the audio from YouTube
                output_dir = os.path.dirname(filepath) # Get the directory of the file
                yt = YouTube(yturl) # Create a new instance of the YouTube class
                stream = yt.streams.filter(only_audio=True).first() # Get the first audio stream
                stream.download(output_path=output_dir) # type: ignore # Download the audio stream
                downloaded_file = stream.default_filename # type: ignore # Get the default filename of the downloaded file
                new_file = os.path.join(output_dir, downloaded_song_name + ".mp3") # Create a new file path
                os.rename(os.path.join(output_dir, downloaded_file), new_file) # Rename the downloaded file
                if verbose: # If verbose mode is enabled, print a message to the console
                    print(f"Downloaded audio file: {new_file}")
                update_database(yturl, new_file) # Call the update_database method

        def update_database(yturl, file_location): # update_database method updates the database with the file location of the downloaded audio
            connection = sqlite3.connect("PulseDatabase.db") # Connect to the database
            cursor = connection.cursor() # Create a cursor object
            cursor.execute("UPDATE Songs SET Song_File_Location = ?, Downloaded = 1 WHERE Youtube_URL = ? AND ID IN (SELECT ID FROM Songs ORDER BY ID DESC LIMIT 5)", (file_location, yturl)) # Update the database with the file location of the downloaded audio
            connection.commit() # Commit the changes to the database
            connection.close() # Close the connection to the database
            self.transition_to_mixing_window() # Call the transition_to_mixing_window method

        # GUI Components —————————————————————————————————————————————

        #Top Bar
        frame = CTkFrame(self.ctk_root) # Create a frame for the title and buttons
        frame.pack(anchor="n", padx=10, pady=5, fill="both", expand=False) # Pack the frame at the top of the window with padding

        self.title_label = CTkLabel(frame, text="PULSE AUDIO | Main Window", font=("Helvetica", 30, "bold")) # Create the title label
        self.title_label.pack(side="left", padx=10, pady=10) # Pack the title label with padding

        self.button = CTkButton(frame, text="Verbose Mode", command=self.verbose_mode) # Create the button to enable verbose mode
        self.button.pack(side="right", padx=10, pady=10) # Pack the button with padding
        
        # Main Frame
        main_frame = CTkFrame(self.ctk_root) # Create a frame for the main content
        main_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        # Input Song
        input_song_frame = CTkFrame(main_frame) # Create a frame for the input song
        input_song_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        album_art_image: CTkImage = load_image_from_url(str(input_song[5])) # type: ignore
        if album_art_image: # Load album art for the input song
            album_art_label = CTkLabel(input_song_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left

            text_label = CTkLabel(input_song_frame, text="Input Song | "f"{input_song[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the song label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(input_song_frame, text=f"Album: {input_song[2]}\nArtist: {input_song[3]}\nGenre: {input_song[4]}", font=("Helvetica", 14), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding
        
        # Related Songs —————————————————————————————————————————————
        #1
        related_song1_frame = CTkFrame(main_frame) # Create a frame for the first related song
        related_song1_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True)  # Pack the frame at the top of the window with padding

        album_art_image: CTkImage = load_image_from_url(str(recsong1[5]))  # type: ignore
        if album_art_image: # Load album art for the related song
            album_art_label = CTkLabel(related_song1_frame, image=album_art_image, text="")  # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10))  # Pack the image label to the left

            download_audio_button = CTkButton(related_song1_frame, text="Download Audio", command=lambda: download_audio(recsong1[6], recsong1)) # Create the download audio button
            download_audio_button.pack(side="right", padx=(10, 10), pady=(10, 10)) # Pack the download audio button opposite to the image and text

            text_label = CTkLabel(related_song1_frame, text=f"{recsong1[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the text label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(related_song1_frame, text=f"Album: {recsong1[2]}\nArtist: {recsong1[3]}\nGenre: {recsong1[4]}", font=("Helvetica", 14), justify="left") # Create the text label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding

        #2
        related_song2_frame = CTkFrame(main_frame) # Create a frame for the second related song
        related_song2_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        album_art_image: CTkImage = load_image_from_url(str(recsong2[5])) # type: ignore # Load album art for the related song
        if album_art_image: # Load album art for the related song
            album_art_label = CTkLabel(related_song2_frame, image=album_art_image, text="")  # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10))  # Pack the image label to the left

            download_audio_button = CTkButton(related_song2_frame, text="Download Audio", command=lambda: download_audio(recsong2[6], recsong2)) # Create the download audio button
            download_audio_button.pack(side="right", padx=(10, 10)) # Pack the download audio button opposite to the image and text

            text_label = CTkLabel(related_song2_frame, text=f"{recsong2[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the song label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(related_song2_frame, text=f"Album: {recsong2[2]}\nArtist: {recsong2[3]}\nGenre: {recsong2[4]}", font=("Helvetica", 14), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding

        #3
        related_song3_frame = CTkFrame(main_frame) # Create a frame for the third related song
        related_song3_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        album_art_image: CTkImage = load_image_from_url(str(recsong3[5])) # type: ignore # Load album art for the related song
        if album_art_image: # Load album art for the related song
            album_art_label = CTkLabel(related_song3_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left

            download_audio_button = CTkButton(related_song3_frame, text="Download Audio", command=lambda: download_audio(recsong3[6], recsong3)) # Create the download audio button
            download_audio_button.pack(side="right", padx=(10, 10)) # Pack the download audio button opposite to the image and text

            text_label = CTkLabel(related_song3_frame, text=f"{recsong3[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the song label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(related_song3_frame, text=f"Album: {recsong3[2]}\nArtist: {recsong3[3]}\nGenre: {recsong3[4]}", font=("Helvetica", 14), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding
                
        #4
        related_song4_frame = CTkFrame(main_frame) # Create a frame for the fourth related song
        related_song4_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        album_art_image: CTkImage = load_image_from_url(str(recsong4[5])) # type: ignore # Load album art for the related song
        if album_art_image: # Load album art for the related song
            album_art_label = CTkLabel(related_song4_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left
            
            download_audio_button = CTkButton(related_song4_frame, text="Download Audio", command=lambda: download_audio(recsong4[6], recsong4)) # Create the download audio button
            download_audio_button.pack(side="right", padx=(10, 10)) # Pack the download audio button opposite to the image and text
            
            text_label = CTkLabel(related_song4_frame, text=f"{recsong4[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the song label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(related_song4_frame, text=f"Album: {recsong4[2]}\nArtist: {recsong4[3]}\nGenre: {recsong4[4]}", font=("Helvetica", 14), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding

        #5
        related_song5_frame = CTkFrame(main_frame) # Create a frame for the fifth related song
        related_song5_frame.pack(anchor="center", padx=10, pady=10, fill="both", expand=True) # Pack the frame at the top of the window with padding
        
        album_art_image: CTkImage = load_image_from_url(str(recsong5[5])) # type: ignore # Load album art for the related song
        if album_art_image: # Load album art for the related song
            album_art_label = CTkLabel(related_song5_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left

            download_audio_button = CTkButton(related_song5_frame, text="Download Audio", command=lambda: download_audio(recsong5[6], recsong5)) # Create the download audio button
            download_audio_button.pack(side="right", padx=(10, 10)) # Pack the download audio button opposite to the image and text

            text_label = CTkLabel(related_song5_frame, text=f"{recsong5[1]}", font=("Helvetica", 20, "bold"), justify="left") # Create the song label
            text_label.pack(anchor="nw", padx=(10, 10), pady=(10, 10)) # Pack the song label with padding
            details_label = CTkLabel(related_song5_frame, text=f"Album: {recsong5[2]}\nArtist: {recsong5[3]}\nGenre: {recsong5[4]}", font=("Helvetica", 14), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding

        self.ctk_root.mainloop() # Start the Tkinter event loop

    # Verbose Mode —————————————————————————————————————————————

    def verbose_mode(self):  # developer_menu method opens the developer menu
        global verbose  # Global variable
        verbose = not verbose  # Toggle the verbose variable
        if verbose == True: # If verbose mode is enabled, print a message to the console
            print("Main Menu Debug Mode Enabled")  # Print a message to the console
        else: # If verbose mode is disabled, print a message to the console
            print("Main Menu Debug Mode Disabled")  # Print a message to the console
    
    # Transition to Mixing Window —————————————————————————————————————————————
    
    def transition_to_mixing_window(self): # transition_to_main_window method transitions to the main window
        self.ctk_root.destroy()  # Close the startup menu window
        mixing_window = MixingWindow()  # Assuming MainWindow is similar structure to StartupMenu
        mixing_window.create_window()  # Here you define the GUI setup for Main Window just like in StartupMenu
    
# DownloadWindow Class End —————————————————————————————————————————————

# MixingWindow Class —————————————————————————————————————————————
class MixingWindow(): # MainWindow class defines the main window of the application
    def __init__(self): # Constructor initializes all the necessary UI components to None
        self.title_label = None # Title label
        self.button_frame = None # Button frame
        self.related_songs = [] # Related songs
        self.subtitle_label = None # Subtitle label
        self.identified_song = "" # Identified song
        self.internet_connected = True # Internet connection status
        self.output_song = [] # Output song
        self.key_input = "" # Key of the input song
        self.key_new = "" # Key of the new song
        self.bpm_input = 0 # BPM of the input song
        self.bpm_new = 0 # BPM of the new song
        
    def create_window(self): # create_window method sets up the window and UI components
        self.ctk_root = ctk() # Create the Tkinter root window
        self.ctk_root.title("PULSE: Mixing Window") # Set the title of the window
        self.ctk_root.resizable(True, True) # Disable resizing of the window
        screen_width = self.ctk_root.winfo_screenwidth() # Get the width of the screen
        screen_height = self.ctk_root.winfo_screenheight() # Get the height of the screen
        window_width = int(screen_width * 2 / 3) # Set the width of the window
        window_height = int(screen_height * 3 / 4) # Set the height of the window
        x = (screen_width - window_width) // 2 # Calculate the x-coordinate of the window
        y = (screen_height - window_height) // 2 # Calculate the y-coordinate of the window
        
        self.ctk_root.geometry(f"{window_width}x{window_height}+{x}+{y})") # Set the geometry of the window to center it on the screen
        
        #Connect to Database
        connection=sqlite3.connect("PulseDatabase.db") # Connect to the database
        cursor=connection.cursor() # Create a cursor object
        
        cursor.execute("SELECT * FROM Songs ORDER BY ID DESC LIMIT 1 OFFSET 5") # Gather the input song from the database
        input_song=cursor.fetchone() # Gather the input song from the database
        
        cursor.execute("SELECT * FROM Songs WHERE Downloaded = 1 ORDER BY ID DESC LIMIT 1 OFFSET 0")
        new_song=cursor.fetchone() # Gather the new song from the database
        
        connection.commit() # Commit the changes to the database
        connection.close() # Close the connection to the database
        
        self.ctk_root.geometry(f"{window_width}x{window_height}+{x}+{y})") # Set the geometry of the window to center it on the screen
            
        def load_image_from_url(url): # load_image_from_url method loads an image from a URL and returns it in a format that can be displayed
            try: # Try to load the image from the URL
                response = requests.get(url) # Send a GET request to the URL
                image = Image.open(BytesIO(response.content)) # Open the image from the URL
                image = image.resize((150, 150))  # Resize the image as per your requirements
                photo_image = ImageTk.PhotoImage(image) # Convert the image to a format that can be displayed
                return photo_image # Return the image
            except Exception as e: # If the image cannot be loaded, print an error message to the console
                print(f"Error loading image from URL: {e}") # Print the error to the console
                return None # Return None if the image cannot be loaded   
                        
        # Librosa Key + BPM Collection ————————————————————————————————————————————— 
        chroma_to_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] # Define the mapping of chroma features to keys
        
        def process_song(song):
            audioread = librosa.core.load(song[8]) # Load the song
            y, sr = audioread # Unpack the audioread tuple into y and sr
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr) # Get the tempo and beat frames of the song
            bpm = format(int(round(tempo))) # Set the song BPM to the tempo
            if verbose: # If verbose mode is enabled, print the song BPM to the console
                print(f"{song[1]} BPM:", bpm) # Print the song BPM to the console

            chromagram = librosa.feature.chroma_stft(y=y, sr=sr) # Get the chroma features of the song
            mean_chroma = np.mean(chromagram, axis=1) # Get the mean chroma of the song
            estimated_key_index = np.argmax(mean_chroma) # Get the index of the estimated key
            estimated_key = chroma_to_key[estimated_key_index] # Get the estimated key
            if verbose: # If verbose mode is enabled, print the estimated key to the console
                print(f"Detected Key ({song[1]}):", estimated_key) # Print the estimated key to the console
            return bpm, estimated_key

        # Input Song
        self.bpm_input, self.key_input = process_song(input_song)

        # New Song
        self.bpm_new, self.key_new = process_song(new_song)
                        
        # Top Bar —————————————————————————————————————————————
        frame = CTkFrame(self.ctk_root) # Create a frame for the title and buttons
        frame.pack(anchor="n", padx=10, pady=5, fill="both", expand=False) # Pack the frame at the top of the window with padding

        self.title_label = CTkLabel(frame, text="PULSE AUDIO | Mixing Window", font=("Helvetica", 30, "bold")) # Create the title label
        self.title_label.pack(side="left", padx=10, pady=10) # Pack the title label with padding

        self.button = CTkButton(frame, text="Verbose Mode", command=self.verbose_mode) # Create the button
        self.button.pack(side="right", padx=10, pady=10) # Pack the button with padding
            
        #Main Frame
        main_frame = CTkFrame(self.ctk_root) # Create a frame for the main content
        main_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding

        # Frame for Input Song (left half)
        input_frame = CTkFrame(main_frame) # Create a frame for the first song
        input_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame on the left side with padding
        
        #get album cover
        album_art_image: CTkImage = load_image_from_url(str(input_song[5])) # type: ignore
        if album_art_image: # Load album art for the input song
            album_art_label = CTkLabel(input_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left

            title_label2 = CTkLabel(input_frame, text=(new_song[1]), font=("Helvetica", 22, "bold")) # Create the song label
            title_label2.pack(anchor="nw", padx=10, pady=10) # Pack the song label with padding
            details_label = CTkLabel(input_frame, text=f"Album | {input_song[2]}\nArtist | {input_song[3]}\nGenre | {input_song[4]}\nKey | {self.key_input}\nBPM | {self.bpm_input}", font=("Helvetica", 20), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding
        
        # Frame for Downloaded Song (right half)
        new_song_frame = CTkFrame(main_frame) # Create a frame for the second song
        new_song_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame on the right side with padding
    
        #get album cover
        album_art_image: CTkImage = load_image_from_url(str(new_song[5])) # type: ignore
        if album_art_image: # Load album art for the new song
            album_art_label = CTkLabel(new_song_frame, image=album_art_image, text="") # Create the album art label
            album_art_label.pack(side="left", padx=(10, 10), pady=(10, 10)) # Pack the image label to the left            

            title_label2 = CTkLabel(new_song_frame, text=(new_song[1]), font=("Helvetica", 22, "bold")) # Create the song label
            title_label2.pack(anchor="nw", padx=10, pady=10) # Pack the song label with padding
            details_label = CTkLabel(new_song_frame, text=f"Album | {new_song[2]}\nArtist | {new_song[3]}\nGenre | {new_song[4]}\nKey | {self.key_new}\nBPM | {self.bpm_new}", font=("Helvetica", 20), justify="left") # Create the details label
            details_label.pack(anchor="nw", padx=(10, 10)) # Pack the details label with padding

        # Frame for Mixing Music
        mixing_frame = CTkFrame(main_frame) # Create a frame for the mixing music
        mixing_frame.pack(anchor="center", padx=10, pady=5, fill="both", expand=True) # Pack the frame at the top of the window with padding
        
        title_label3 = CTkLabel(mixing_frame, text="Mixing Music", font=("Helvetica", 22, "bold")) # Create the title label
        title_label3.pack(anchor="nw", padx=10, pady=10) # Pack the title label with padding

        # Key Match and BPM Match Checklist
        key_match = CTkCheckBox(mixing_frame, text="Key Match", font=("Helvetica", 20)) # Create the key match checkbox
        key_match.pack(anchor="nw", padx=10, pady=10) # Pack the key match checkbox with padding
        bpm_match = CTkCheckBox(mixing_frame, text="BPM Match", font=("Helvetica", 20)) # Create the BPM match checkbox
        bpm_match.pack(anchor="nw", padx=10, pady=10) # Pack the BPM match checkbox with padding
        
        # Update Label Method
        def update_label(slider, label):
            value = slider.get()
            label.configure(text=f"{label.cget('text').split(':')[0]}: {int(value)}")

        # Crossfade Slider
        crossfade_label = CTkLabel(mixing_frame, text="Cross Fade (Seconds): 0", font=("Helvetica", 20, "bold"))  # Set initial value to 0
        crossfade_slider = CTkSlider(mixing_frame, from_=0, to=10, number_of_steps=10, command=lambda value: update_label(crossfade_slider, crossfade_label))
        crossfade_label.pack(anchor="nw", padx=10, pady=10)
        crossfade_slider.pack(anchor="nw", padx=10, pady=10)
        crossfade_slider.set(0)

        # Reverb Slider
        reverb_label = CTkLabel(mixing_frame, text="Reverb (Seconds): 0", font=("Helvetica", 20, "bold"))  # Set initial value to 0
        reverb_slider = CTkSlider(mixing_frame, from_=0, to=10, number_of_steps=10, command=lambda value: update_label(reverb_slider, reverb_label))
        reverb_label.pack(anchor="nw", padx=10, pady=10)
        reverb_slider.pack(anchor="nw", padx=10, pady=10)
        reverb_slider.set(0)

        # Mixing Backend —————————————————————————————————————————————
        def mix_audio(): 
            if verbose: 
                print("Mixing audio") 

            # Create a temporary directory to store the audio files
            directory_temp = os.path.join(os.getcwd(), "temp")
            if not os.path.exists(directory_temp):
                os.makedirs(directory_temp)

            # Load the input song and the new song
            input_song_temp, sr_input = librosa.load(input_song[8])
            new_song_temp, sr_new = librosa.load(new_song[8])

            # If Key Match is enabled, transpose the new song to match the key of the input song
            if key_match.get():
                if verbose:
                    print("Transposing new song to match the key of the input song")
                semitone_difference = ((chroma_to_key.index(self.key_input) - chroma_to_key.index(self.key_new)) / chroma_to_key.index(self.key_new)) % 12
                new_song_temp = librosa.effects.pitch_shift(new_song_temp, sr=sr_new, n_steps=semitone_difference)
                sf.write(os.path.join(directory_temp, "temp.wav"), new_song_temp, sr_new)
                

            # If BPM Match is enabled, time-stretch the new song to match the BPM of the input song
            if bpm_match.get():
                if verbose:
                    print("Time-stretching new song to match the BPM of the input song")
                bpm_difference = int(self.bpm_new) - int(self.bpm_input)
                sf.write(os.path.join(directory_temp, "temp.wav"), new_song_temp, sr_new)

            # If Crossfade is enabled, apply crossfade to the mix
            crossfade_duration = crossfade_slider.get()
            if crossfade_duration > 0:
                if verbose:
                    print("Applying crossfade to the mix")
                fade_duration = int(crossfade_duration * 1000)
                input_song_temp = AudioSegment.from_file(input_song[8])
                new_song_temp = AudioSegment.from_file(new_song[8])
                mix = input_song_temp.append(new_song_temp, crossfade=fade_duration)

            # If Reverb is enabled, apply reverb to the mix
            reverb = reverb_slider.get()
            if reverb > 0:
                if verbose:
                    print("Applying reverb to the mix")
                mix_temp = AudioSegment.from_file(mix.export(format="wav"))
                mix = mix_temp.overlay(mix_temp, position=0, gain_during_overlay=-6)

                # Export the mix with reverb as a temp file
                mix.export(os.path.join(directory_temp, "temp.wav"), format="wav")

            # Ask user where to save the mix and delete the temp file
            if verbose:
                print("Mixing complete")
            mix.export(filedialog.asksaveasfilename(initialfile=("Mix of " + (input_song[1]) + " + " + (new_song[1]) + ".mp3"), defaultextension=".mp3", filetypes=(("MP3 Files", "*.mp3"),))) # Open a file dialog to select the download location
            # Close the window
            if verbose: # If verbose mode is enabled, print a message to the console
                print("Mixing Finished: Window Closing") # Print a message to the console
            self.ctk_root.destroy() 

        # Mixing Backend End —————————————————————————————————————————————

        # Export Mix Button
        export_mix_button = CTkButton(mixing_frame, text="Export Mix", font=("Helvetica", 16), command=mix_audio) # Create the export mix button
        export_mix_button.pack(anchor="nw", padx=10, pady=10) # Pack the export mix button with padding

        self.ctk_root.mainloop() # Start the Tkinter event loop

    def verbose_mode(self):  # developer_menu method opens the developer menu
        global verbose  # Global variable
        verbose = not verbose  # Toggle the verbose variable
        if verbose == True: # If verbose mode is enabled, print a message to the console
            print("Mixing Menu Debug Mode Enabled")  # Print a message to the console
        else: # If verbose mode is disabled, print a message to the console
            print("Mixing Menu Debug Mode Disabled")  # Print a message to the console

# MixingWindow Class End —————————————————————————————————————————————

# Main ————————————————————————————————————————————
if __name__ == "__main__": # Program Start (Calling Window)
    startup_menu = StartupMenu() # Create a new StartupMenu object
    startup_menu.create_window() # Call the create_window method to create and display the windows