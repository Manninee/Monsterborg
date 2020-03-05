import tkinter as tk
from PIL import ImageTk


class App:
    def __init__(self, title, imageQueue, inputs, saveEvent):
        self.window = tk.Tk()
        self.window.title(title)
        self.imageQueue = imageQueue
        self.inputs = inputs
        self.saveEvent = saveEvent

        self.keys = ["w", "s", "a", "d", "space"]
        self.streamUpdateDelay = 10
        self.photo = None

        self.canvas = tk.Canvas(self.window)
        self.canvas.create_text(200, 10, fill="darkblue", font="Times 20 italic bold", text="Stream")
        self.canvas.config(highlightthickness=0, highlightbackground="red")
        self.canvas.pack()

        self.window.bind("<KeyPress>", self.keydown)
        self.window.bind("<KeyRelease>", self.keyup)

        self.window.after(self.streamUpdateDelay, self.updateStream)

        self.window.focus_set()

    def updateStream(self):
        if not self.imageQueue.empty():
            image = self.imageQueue.get()
            self.photo = ImageTk.PhotoImage(image=image)
            width, height = image.size
            self.canvas.config(width=width, height=height)
            self.canvas.create_image((0, 0), image=self.photo, anchor=tk.NW)
        self.window.after(self.streamUpdateDelay, self.updateStream)

    def run(self):
        self.window.mainloop()

    def keydown(self, e):
        if e.keysym in self.keys:
            self.inputs.addKey(e.keysym)
        if e.keysym == "r":
            self.startStopSave()

    def keyup(self, e):
        if e.keysym in self.keys:
            self.inputs.removeKey(e.keysym)

    def startStopSave(self):
        if not self.saveEvent.is_set():
            self.saveEvent.set()
            self.canvas.config(highlightthickness=1)
        else:
            self.saveEvent.clear()
            self.canvas.config(highlightthickness=0)
