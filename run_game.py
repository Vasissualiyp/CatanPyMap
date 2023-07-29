import tkinter as tk
from PIL import Image, ImageTk
from screeninfo import get_monitors
from index import main

main()

def get_monitor_with_res(width, height):
    for m in get_monitors():
        if m.width == width and m.height == height:
            return m
    return None

# Open the image file
img = Image.open("game.png")

# Find the 4K monitor
monitor = get_monitor_with_res(4096, 2160)
if monitor is None:
    raise ValueError("No 4K monitor found")

# Create a Tk root widget
root = tk.Tk()

# Create a canvas for drawing
canvas = tk.Canvas(root, width=monitor.width, height=monitor.height, highlightthickness=0)
canvas.pack()

# Convert the image to a format Tkinter can use
tk_img = ImageTk.PhotoImage(img)
canvas.create_image(0, 0, anchor='nw', image=tk_img)

# Put the canvas on the screen and make it fullscreen
root.attributes('-fullscreen', True)
root.geometry(f'+{monitor.x}+{monitor.y}')
root.mainloop()

