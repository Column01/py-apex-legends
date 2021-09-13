import json
import os
from tkinter import Button, Frame, Label, Tk, font, Menu, messagebox
import sys

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

        self.settings_file = os.path.join(__location__, "settings.json")
        self.load_settings()

        menu_bar = Menu(self.master)
        menu_bar.add_command(label="Reload", command=lambda: print("test"))
        self.master.config(menu=menu_bar)
        self.get_data("bridge")
        self.display_info()
    
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
        
        self.params = "?version=5&platform={platform}&player={username}&auth={token}".format(platform=self.platform, username=self.username, token=self.token)

    def get_data(self, endpoint, params=""):
        """ Gets data from the unofficial apex legends API

        Paramaters:
            endpoint (str) - The API endpoint to get data from
            params (Optional[str]) - An optional URL encoded list of params to add to the query. Example: "&limit=10"

        """
        resp = requests.get(self.api_base + endpoint + self.params + params)
        self.data = resp.json()


if __name__ == "__main__":
    # Starts the UI
    root = Tk()
    tracker = ApexLegendsTracker(root)
    root.mainloop()
