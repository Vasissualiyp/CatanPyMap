import tkinter as tk
from time import sleep
from PIL import Image, ImageTk
from screeninfo import get_monitors
from index import main_mapgenerator
from main import Parameters
import threading
import queue
import sys

def get_monitor_with_res(width, height):
    for m in get_monitors():
        if m.width == width and m.height == height:
            return m
    return None

def listen_for_input(q):
    while True:
        command = input()
        q.put(command)

def main_tk():
    # Get the list of monitors
    monitors = get_monitors()

    # Display the monitors
    for i, m in enumerate(monitors):
        print(f"{i+1}: {m.width}x{m.height}")

    # Ask the user for the monitor they want to use
    monitor_number = int(input("Enter the number of the monitor you want to use: "))
    monitor = monitors[monitor_number-1]

    # Generate the map
    monitor_info = (4096, 2160, 1210, 680)
    parameters = Parameters(monitor_info)
    main_mapgenerator(monitor_info, parameters)
    sleep(0.5)

    # Open the image file
    img = Image.open("game.png")

    # Find the 4K monitor
    #monitor = get_monitor_with_res(4096, 2160)
    #if monitor is None:
    #    raise ValueError("No 4K monitor found")

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

    # Create a queue to communicate between threads
    q = queue.Queue()

    # Start the console listener thread
    listener_thread = threading.Thread(target=listen_for_input, args=(q,))
    listener_thread.start()

    # Check the queue periodically
    def check_queue():
        try:
            command = q.get_nowait()
            if command.lower() in ['quit', 'exit']:
                root.quit()
            elif command.lower() == 'reload':
                root.quit()
                sys.exit(main_tk())
        except queue.Empty:
            pass

        root.after(100, check_queue)

    root.after(100, check_queue)
    root.mainloop()

# Start the program
main_tk()

