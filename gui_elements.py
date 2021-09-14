from tkinter import Frame, Label, font

""" GUI CONSTANTS """
# Color
BACKGROUND_COLOR = "#333333"
LABEL_COLOR = "#FFFFFF"
VALUE_COLOR = "#40f200"

# Widget Padding
PADDING_X = 3
PADDING_Y = 3

# Font
FAMILY = "Helvetica Neue"
SIZE = 14


class TrackerFrame(Frame):
    def __init__(self, master, fill):
        """Custom Tkinter Frame for custom formatting with automatic UI packing

        Args:
            master (tkinter.Frame): Tkinter frame that is the master
            fill (str): Fill parameter for automatic packing of element
        """
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)
        self.pack(fill=fill)


class SectionLabel(Frame):
    def __init__(self, master, text):
        """Custom Tkinter Label for GUI Sections with automatic UI packing

        Args:
            master (tkinter.Frame): Tkinter frame that is the master
            text (str): The text content of the label
        """
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)
        _font = font.Font(family=FAMILY, size=SIZE, weight="bold", underline=True)
        label = Label(master, text=text, font=_font, bg=BACKGROUND_COLOR, fg=LABEL_COLOR)
        label.pack(side="left", padx=PADDING_X, pady=PADDING_Y)
        self.pack(side="left")


class ValueLabel(Frame):
    def __init__(self, master, text):
        """Custom Tkinter Label for GUI values with automatic UI packing

        Args:
            master (tkinter.Frame): Tkinter frame that is the master
            text (str): The text content of the label
        """
        Frame.__init__(self, master, bg=BACKGROUND_COLOR)
        _font = font.Font(family=FAMILY, size=SIZE)
        self.label = Label(master, text=text, font=_font, bg=BACKGROUND_COLOR, fg=VALUE_COLOR)
        self.label.pack(side="left")
        self.pack(side="left")
    
    def update(self, text):
        self.label.configure(text=text)
