import json
import os
import sys
import threading
import time
from datetime import datetime
from tkinter import Frame, Menu, Tk, messagebox

import requests

from gui_elements import SectionLabel, TrackerFrame, ValueLabel

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

        self.settings_file = os.path.join(__location__, "settings.json")
        self.load_settings()

        menu_bar = Menu(self.master)
        menu_bar.add_command(label="Reload", command=self.init_window)
        self.master.config(menu=menu_bar)

        clock_frame = TrackerFrame(self.master)
        clock_frame.pack(fill="x")
        time_label = SectionLabel(clock_frame, "Time:")
        time_label.pack(side="left")
        self.clock = ValueLabel(clock_frame, time.strftime('%I:%M:%S %p'))
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

        # Starts updating data every second
        self.load()
    
    def update_clock(self):
        self.clock.update(time.strftime('%I:%M:%S %p'))
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
        if self.main_frame is not None:
            # Main frame exists so we are reloading. Destroy it and recreate it
            self.main_frame.destroy()
        # Make main window frame
        self.main_frame = TrackerFrame(self.master)
        self.main_frame.pack(fill="both", expand=1)

        # User Info
        user_frame = TrackerFrame(self.main_frame)
        user_frame.pack(fill="x")
        user_info_label = SectionLabel(user_frame, "User Info:")
        user_info_label.pack(side="left")
        self.user_info = ValueLabel(user_frame, f"{self.api_thread.username} (Level {self.api_thread.level}) - {self.api_thread.online_status}")
        self.user_info.pack(side="left")
        
        # Legend
        legend_frame = TrackerFrame(self.main_frame)
        legend_frame.pack(fill="x")
        legend_label = SectionLabel(legend_frame, "Selected Legend:")
        legend_label.pack(side="left")
        self.legend = ValueLabel(legend_frame, f"{self.api_thread.legend}")
        self.legend.pack(side="left")
        
        # Kills
        kills_frame = TrackerFrame(self.main_frame)
        kills_frame.pack(fill="x")
        kill_label = SectionLabel(kills_frame, "Kills:")
        kill_label.pack(side="left")
        self.kills = ValueLabel(kills_frame, f"{self.api_thread.total_kills}")
        self.kills.pack(side="left")
        
        # Damage
        damage_frame = TrackerFrame(self.main_frame)
        damage_frame.pack(fill="x")
        damage_label = SectionLabel(damage_frame, "Damage:")
        damage_label.pack(side="left")
        self.damage = ValueLabel(damage_frame, f"{self.api_thread.total_damage}")
        self.damage.pack(side="left")

        # Map info
        cur_map_frame = TrackerFrame(self.main_frame)
        cur_map_frame.pack(fill="x")
        cur_map_label = SectionLabel(cur_map_frame, "Current Map:")
        cur_map_label.pack(side="left")
        self.cur_map = ValueLabel(cur_map_frame, f"{self.api_thread.cur_map} (until {self.api_thread.cur_map_end})")
        self.cur_map.pack(side="left")

        next_map_frame = TrackerFrame(self.main_frame)
        next_map_frame.pack(fill="x")
        next_map_label = SectionLabel(next_map_frame, "Next Map:")
        next_map_label.pack(side="left")
        self.next_map = ValueLabel(next_map_frame, f"{self.api_thread.next_map} (until {self.api_thread.next_map_end})")
        self.next_map.pack(side="left")

    def load(self):
        # Not polling data, update the UI
        if not self.api_thread.polling:
            # Update username and Level
            self.user_info.update(f"{self.api_thread.username} (Level {self.api_thread.level}) - {self.api_thread.online_status}")

            # Update selected legend
            self.legend.update(f"{self.api_thread.legend}")

            # Update kills and damage tracker
            self.kills.update(f"{self.api_thread.total_kills}")
            self.damage.update(f"{self.api_thread.total_damage}")

            # Update current and next map info
            self.cur_map.update(f"{self.api_thread.cur_map} (until {self.api_thread.cur_map_end})")
            self.next_map.update(f"{self.api_thread.next_map} (until {self.api_thread.next_map_end})")

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
            self.player_data = self.get_data("bridge", params="&merge&removeMerged")
            # Username and Level
            self.username = self.player_data["global"]["name"]
            self.level = self.player_data["global"]["level"]

            # Realtime info
            self.online_status = "Online" if self.player_data["realtime"]["isOnline"] == 1 else "Offline"
            self.legend = self.player_data["realtime"]["selectedLegend"]

            # Totals
            self.total_kills = self.player_data["total"]["kills"]["value"]
            self.total_damage = self.player_data["total"]["damage"]["value"]

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
        return

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
    root = Tk()
    tracker = ApexLegendsTracker(root)
    def on_closing():
        tracker.api_thread.running = False
        tracker.api_thread.join()
        os._exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
