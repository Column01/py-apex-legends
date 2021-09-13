import json
import os
import sys
import time
import threading
from datetime import datetime
from tkinter import Frame, Label, Menu, Tk, font, messagebox

import requests

# Changes an internal path variable based on whether the application was built into an EXE or not.
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    __location__ = os.path.dirname(sys.executable)
else:
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
                                    os.path.dirname(__file__)))


class ApexLegendsTracker(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Apex Legends Tracker")

        # Some constants for use later
        self.font = font.Font(family="Helvetica Neue", size=14)
        self.label_font = font.Font(family="Helvetica Neue", size=14, weight="bold", underline=True)
        self.background_color = "#333333"
        self.btn_background_color = "#655F5F"
        self.label_color = "#FFFFFF"
        self.value_color = "#40f200"

        self.settings_file = os.path.join(__location__, "settings.json")
        self.load_settings()

        menu_bar = Menu(self.master)
        menu_bar.add_command(label="Reload", command=self.load)
        self.master.config(menu=menu_bar)

        self.clock_frame = Frame(self.master)
        self.clock_frame.configure(bg=self.background_color)
        self.clock_frame.pack(fill="x")
        self.time_label = Label(self.clock_frame, text="Time:", font=self.label_font, bg=self.background_color, fg=self.label_color)
        self.time_label.pack(padx=5, pady=5, side="left")
        self.clock = Label(self.clock_frame, text=time.strftime('%I:%M:%S %p'), font=self.font, bg=self.background_color, fg=self.value_color)
        self.clock.pack(side="left")

        # Start clock display
        self.update_clock()
        self.main_frame = None

        # Starts a thread to gather API data every 30 seconds with a 0.25 second delay between requests
        self.api_thread = APIDataFetcher(self.username, self.platform, self.token, 0.1, 10.0)
        self.api_thread.start()
        
        # Wait until the API thread polls once
        while self.api_thread.polling:
            continue
        # Loads the data into the UI
        self.init_window()

        # Starts a task to reload the data every second
        self.master.after(1000, self.load)

        self.api_thread.username = "TESTING 123"
    
    def update_clock(self):
        self.clock.configure(text=time.strftime('%I:%M:%S %p'))
        self.master.after(200, self.update_clock)
    
    def load_settings(self):
        try:
            with open(self.settings_file, "r") as fp:
                self.settings = json.load(fp)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error loading the settings file as JSON, is it valid?")
        except FileNotFoundError:
            messagebox.showerror("Error", "Unable to find the settings.json file!")

        self.token = self.settings.get("token")
        self.username = self.settings.get("username")
        self.platform = self.settings.get("platform")

        if self.token is None:
            messagebox.showerror("Error", "No token was found in the settings file!")
        if self.username is None:
            messagebox.showerror("Error", "No username was found in the settings file!")
        if self.platform is None:
            messagebox.showerror("Error", "No platform was found in the settings file!")

    def init_window(self):
        if self.main_frame is None:
            # Make main window frame
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)
        else:
            # Main frame exists so we are reloading. Destroy it and recreate it
            self.main_frame.destroy()
            self.main_frame = Frame(self.master)
            self.main_frame.configure(bg=self.background_color)
            self.main_frame.pack(fill="both", expand=1)

        user_frame = Frame(self.main_frame)
        user_frame.configure(bg=self.background_color)
        user_frame.pack(fill="x")
        user_info_label = Label(user_frame, text=f"User Info:", font=self.label_font, bg=self.background_color, fg=self.label_color)
        user_info_label .pack(padx=5, pady=5, side="left")
        self.user_label = Label(user_frame, text=f"{self.api_thread.username} (Level {self.api_thread.level})", font=self.font, bg=self.background_color, fg=self.value_color)
        self.user_label.pack(side="left")

        cur_map_frame = Frame(self.main_frame)
        cur_map_frame.configure(bg=self.background_color)
        cur_map_frame.pack(fill="x")
        cur_map_label = Label(cur_map_frame, text="Current Map:", font=self.label_font, bg=self.background_color, fg=self.label_color)
        cur_map_label.pack(padx=5, pady=5, side="left")
        self.cur_map_name_label = Label(cur_map_frame, text=f"{self.api_thread.cur_map} (until {self.api_thread.cur_map_end})", font=self.font, bg=self.background_color, fg=self.value_color)
        self.cur_map_name_label.pack(side="left")

        next_map_frame = Frame(self.main_frame)
        next_map_frame.configure(bg=self.background_color)
        next_map_frame.pack(fill="x")
        next_map_label = Label(next_map_frame, text=f"Next Map:", font=self.label_font, bg=self.background_color, fg=self.label_color)
        next_map_label.pack(padx=5, pady=5, side="left")
        self.next_map_name_label = Label(next_map_frame, text=f"{self.api_thread.next_map} (until {self.api_thread.next_map_end})", font=self.font, bg=self.background_color, fg=self.value_color)
        self.next_map_name_label.pack(side="left")

    def load(self):
        # Not polling data, update the UI
        if not self.api_thread.polling:
            # Update username and Level
            self.user_label.configure(text=f"{self.api_thread.username} (Level {self.api_thread.level})")

            # Update current and next map info
            self.cur_map_name_label.configure(text=f"{self.api_thread.cur_map} (until {self.api_thread.cur_map_end})")
            self.next_map_name_label.configure(text=f"{self.api_thread.next_map} (until {self.api_thread.next_map_end})")

        self.master.after(1000, self.load)


class APIDataFetcher(threading.Thread):
    def __init__(self, username, platform, token, request_delay, poll_interval):
        threading.Thread.__init__(self)
        self.api_base = "https://api.mozambiquehe.re/"
        self.delay = request_delay
        self.poll_interval = poll_interval
        self.username = username
        self.platform = platform
        self.token = token

        self.params = f"?version=5&platform={self.platform}&player={self.username}&auth={self.token}"

        self.running = False
        self.polling = False

    def run(self):
        self.running = True
        while self.running:
            self.polling = True

            """ Player data """
            self.player_data = self.get_data("bridge")
            # Username and Level
            self.username = self.player_data["global"]["name"]
            self.level = self.player_data["global"]["level"]

            """ Map data """
            self.map_data = self.get_data("maprotation")
            # Current Map
            self.cur_map = self.map_data["battle_royale"]["current"]["map"]
            self.cur_map_end = datetime.fromtimestamp(self.map_data["battle_royale"]["current"]["end"]).strftime("%I:%M %p")
            # Next Map
            self.next_map = self.map_data["battle_royale"]["next"]["map"]
            self.next_map_end = datetime.fromtimestamp(self.map_data["battle_royale"]["next"]["end"]).strftime("%I:%M %p")

            """ Finish poll"""
            self.polling = False
            time.sleep(self.poll_interval)

    def get_data(self, endpoint, params=""):
        """ Returns data from the unofficial apex legends API.

        Paramaters:
            endpoint (str) - The API endpoint to get data from
            params (Optional[str]) - An optional URL encoded list of params to add to the query. Example: "&limit=10"
        """
        resp = requests.get(self.api_base + endpoint + self.params + params)
        time.sleep(self.delay)
        return resp.json()


if __name__ == "__main__":
    # Starts the UI
    root = Tk()
    tracker = ApexLegendsTracker(root)
    root.mainloop()
