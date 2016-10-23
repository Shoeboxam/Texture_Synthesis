import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from Synthesizer.sources import files

from Synthesizer.settings import Settings

class App(tk.Frame):
    textures = {}

    def __init__(self, master, path):
        path = path.replace('\\', '//')
        tk.Frame.__init__(self, master)
        self.grid()
        self.master.title("Synthesizer")

        self.master.rowconfigure(0, weight=1)

        # Frame 1
        self.Frame1 = tk.Frame(master)
        self.Frame1.grid(row=0, column=0, sticky="nsew")
        self.master.columnconfigure(0, weight=1)

        self.Tree = ttk.Treeview(self.Frame1)
        self.Tree.grid(row=0, column=0, sticky="nsew")
        self.Frame1.columnconfigure(0, weight=1)
        self.Frame1.rowconfigure(0, weight=1)

        self.Tree.bind("<ButtonRelease-1>", self.TreeItemClick)

        self.Tree.heading('#0', text="Default Patches", anchor='w')

        ysb = ttk.Scrollbar(self.Frame1, orient='vertical', command=self.Tree.yview)
        self.Tree.configure(yscroll=ysb.set)

        root_node = self.Tree.insert('', 'end', text=path, open=True)
        self.process_directory(root_node, path, self.Tree)

        ysb.grid(row=0, column=1, sticky='ns')

        # Frame 2
        self.Frame2 = tk.Frame(master)
        self.Frame2.grid(row=0, column=1, sticky="nsew")
        self.master.columnconfigure(1, weight=1)

        self.imageselected = ImageTk.PhotoImage(
            Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\lander.png"))

        self.imagebox = tk.Label(self.Frame2, image=self.imageselected)
        self.imagebox.grid(row=0, column=0, sticky="nsew")
        self.Frame2.rowconfigure(0, minsize=int(root.winfo_screenheight()/2))

        self.listbox = tk.Listbox(self.Frame2, selectmode="extended")
        self.listbox.grid(row=1, column=0, sticky="nsew")
        self.Frame2.rowconfigure(1, weight=2)
        self.Frame2.columnconfigure(0, weight=1)

        self.listbox.bind("<ButtonRelease-1>", self.ListboxItemClick)

        ysbFrame2 = ttk.Scrollbar(self.Frame2, orient='vertical', command=self.listbox.yview)
        self.listbox.configure(yscroll=ysbFrame2.set)

        for item in self.textures.values():
            self.listbox.insert(0, item)

        ysbFrame2.grid(row=1, column=1, sticky='ns')

        # Frame 3
        self.Frame3 = tk.Listbox(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.master.columnconfigure(2, weight=1)


        templates = ['Carl', 'Patrick', 'Lindsay', 'Helmut', 'Chris', 'Gwen']
        for item in templates:
            self.Frame3.insert(0, item)

    def TreeItemClick(self, event):
        selitems = self.Tree.selection()
        self.textures.clear()

        def parent_prepend(id, path):
            parent = self.Tree.item(id, "parent")
            if parent:
                path = self.Tree.item(parent, "value") + path
                parent_prepend(parent, path)
            return path

        if selitems:
            self.listbox.delete(0, "end")
            for item in selitems:                             # Each selection
                folder = os.path.normpath(self.Tree.item(item, "tags")[0])
                for path, subdirs, files in os.walk(folder):  # Each folder
                    for name in files:                        # Each file
                        key = (path + '\\' + name).replace(settings.default_patches, "")
                        self.textures[key] = name
                        self.listbox.insert(0,key)

    def ListboxItemClick(self, event):
        firstitem = self.listbox.get(self.listbox.curselection()[0])

        imageselected = Image.open(settings.default_patches + '\\' + firstitem)
        dim = min(imageselected.size)

        imageselected = imageselected.crop((0, 0, dim, dim))
        imageselected = ImageTk.PhotoImage(imageselected.resize((400, 400), Image.NEAREST))

        self.imagebox.configure(image=imageselected)
        self.imagebox.image = imageselected

    def process_directory(self, parent, path, tree):

        for p in os.listdir(path):
            abspath = os.path.join(path + "//", p)
            isdir = os.path.isdir(abspath)
            if not isdir:
                pass
                # tree.insert(parent, 'end', text=p, open=False)
            else:
                oid = tree.insert(parent, 'end', text=p, tags=abspath, open=False)
                self.process_directory(oid, abspath, tree)

root = tk.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

settings = Settings(r"C:/Users/mike_000/Documents/Pycharm/Texture_Synthesis/Synthesizer/config.json")
if not (os.path.exists(settings.default_patches)):
    files.create_default(settings.mods_directory)

app = App(root, path=settings.default_patches)
app.mainloop()