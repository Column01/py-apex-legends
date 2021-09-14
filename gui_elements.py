from tkinter import Label, font, Frame


# GUI Constants
BACKGROUND_COLOR = "#333333"
LABEL_COLOR = "#FFFFFF"
VALUE_COLOR = "#40f200"
PADDING_X = 3
PADDING_Y = 3

# FONT CONSTANTS
FAMILY = "Helvetica Neue"
SIZE = 14


class TrackerFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)


class SectionLabel(Frame):
    def __init__(self, master, text):
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)
        _font = font.Font(family=FAMILY, size=SIZE, weight="bold", underline=True)
        label = Label(master, text=text, font=_font, bg=BACKGROUND_COLOR, fg=LABEL_COLOR)
        label.pack(side="left", padx=PADDING_X, pady=PADDING_Y)


class ValueLabel(Frame):
    def __init__(self, master, text):
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)
        _font = font.Font(family=FAMILY, size=SIZE)
        self.label = Label(master, text=text, font=_font, bg=BACKGROUND_COLOR, fg=VALUE_COLOR)
        self.label.pack(side="left")
    
    def update(self, text):
        self.label.configure(text=text)
