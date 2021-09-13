import json
import os
import sys
import time
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
        self.api_base = "https://api.mozambiquehe.re/"

        Frame.__init__(self, master)
        self.master = master
        self.master.title("Apex Legends Tracker")

        # Some constants for use later
        self.font = font.Font(family="Helvetica Neue", size=14)
        self.background_color = "#333333"
        self.btn_background_color = "#655F5F"
        self.text_color = "#FFFFFF"

        self.settings_file = os.path.join(__location__, "settings.json")
        self.load_settings()

        menu_bar = Menu(self.master)
        menu_bar.add_command(label="Reload", command=self.load)
        self.master.config(menu=menu_bar)
        self.main_frame = None
        self.load()
    
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
        
        self.params = f"?version=5&platform={self.platform}&player={self.username}&auth={self.token}"

        self.made_requests = 0

    def get_data(self, endpoint, params="", sleep=0):
        """ Returns data from the unofficial apex legends API.

        Paramaters:
            endpoint (str) - The API endpoint to get data from
            params (Optional[str]) - An optional URL encoded list of params to add to the query. Example: "&limit=10"
            sleep (Optional[int, float]) - An optional amount of time to sleep if you are doing multiple requests. Useful to prevent rate limiting.
        """
        resp = requests.get(self.api_base + endpoint + self.params + params)
        self.made_requests += 1
        if sleep > 0:
            time.sleep(sleep)
        return resp.json()

    def display_info(self):
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

        _username = self.player_data["global"]["name"]
        _level = self.player_data["global"]["level"]


        user_frame = Frame(self.main_frame)
        user_frame.configure(bg=self.background_color)
        user_frame.pack(fill="x")
        user = Label(user_frame, text=f"{_username} (Level {_level})", font=self.font, bg=self.background_color, fg=self.text_color)
        user.pack(padx=5, pady=5, side="left")

        _cur_map = self.map_data["battle_royale"]["current"]["map"]
        _cur_change = self.map_data["battle_royale"]["current"]["readableDate_end"].split(" ")[1]
        _next_map= self.map_data["battle_royale"]["next"]["map"]
        _next_change = self.map_data["battle_royale"]["next"]["readableDate_end"].split(" ")[1]

        cur_map_frame = Frame(self.main_frame)
        cur_map_frame.configure(bg=self.background_color)
        cur_map_frame.pack(fill="x")
        cur_map = Label(cur_map_frame, text=f"Current BR map: {_cur_map}\nChanges at: {_cur_change}", font=self.font, bg=self.background_color, fg=self.text_color)
        cur_map.pack(padx=5, pady=5, side="left")

        next_map_frame = Frame(self.main_frame)
        next_map_frame.configure(bg=self.background_color)
        next_map_frame.pack(fill="x")
        next_map = Label(next_map_frame, text=f"Next BR map: {_next_map}\nChanges at: {_next_change}", font=self.font, bg=self.background_color, fg=self.text_color)
        next_map.pack(padx=5, pady=5, side="left")

    def load(self):
        self.player_data = self.get_data("bridge")
        self.map_data = self.get_data("maprotation")
        self.display_info()


if __name__ == "__main__":
    # Starts the UI
    root = Tk()
    tracker = ApexLegendsTracker(root)
    root.mainloop()
