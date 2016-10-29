from Synthesizer.sources import files
from Synthesizer.settings import Settings
from Interface.MappingEditor import MappingEditor

import os

import tkinter as tk


class App(tk.Frame):

    settings = Settings(r"C:/Users/mike_000/Documents/Pycharm/Texture_Synthesis/Synthesizer/config.json")
    if not (os.path.exists(settings.default_patches)):
        files.create_default(settings.mods_directory)

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.grid()
        self.master.title("Synthesizer")
        self.master.iconbitmap(r'C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\favicon.ico')
        # self.master.bind("<FocusIn>", self.update_resourcepack_listing)
        if os.name == 'nt':
            self.master.wm_state('zoomed')

        self.master.rowconfigure(0, weight=1)

        # Frame 1
        self.Frame1 = tk.Frame(master)
        self.Frame1.grid(row=0, column=0, sticky="nsew")
        self.master.columnconfigure(0, weight=1)

        self.mappingbutton = tk.Button(self.Frame1, text='Edit Mappings', command=self.edit_mappings)
        self.mappingbutton.grid(row=0, column=0, sticky='nsew')

        # Frame 2
        self.Frame2 = tk.Frame(master)
        self.Frame2.grid(row=0, column=1, sticky="nsew")
        self.master.columnconfigure(1, weight=1)

        # Frame 3
        self.Frame3 = tk.Frame(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.master.columnconfigure(1, weight=1)

    def edit_mappings(self):
        editor = tk.Toplevel()
        w, h = editor.winfo_screenwidth(), editor.winfo_screenheight()
        editor.geometry("%dx%d+0+0" % (w, h))

        app = MappingEditor(editor, self.settings)
        app.mainloop()

root = tk.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

app = App(root)
app.mainloop()