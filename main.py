"""Launch the College Placement System GUI."""

import tkinter as tk

from gui import PlacementApp


if __name__ == "__main__":
    root = tk.Tk()
    PlacementApp(root)
    root.mainloop()
