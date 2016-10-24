from Synthesizer.sources import files
from Synthesizer.settings import Settings

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from Interface.StencilEditor import StencilEditor

import os, json

import copy


class App(tk.Frame):
    textures = []
    templates = []

    def __init__(self, master):
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

        self.Tree.bind("<<TreeviewSelect>>", self.click_tree_item)

        self.Tree.heading('#0', text="Default Patches", anchor='w')

        ysb = ttk.Scrollbar(self.Frame1, orient='vertical', command=self.Tree.yview)
        self.Tree.configure(yscroll=ysb.set)

        path = settings.default_patches.replace('\\', '//')
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

        self.Search = tk.Entry(self.Frame2)
        self.Search.grid(row=1, column=0, sticky="w")
        self.Frame2.rowconfigure(1)

        self.Search.bind("<KeyRelease>", self.click_search_item)

        self.Listbox = tk.Listbox(self.Frame2, selectmode="extended")
        self.Listbox.grid(row=2, column=0, sticky="nsew")
        self.Frame2.rowconfigure(2, weight=2)
        self.Frame2.columnconfigure(0, weight=1)

        self.Listbox.bind("<<ListboxSelect>>", self.click_listbox_item)

        ysbFrame2 = ttk.Scrollbar(self.Frame2, orient='vertical', command=self.Listbox.yview)
        self.Listbox.configure(yscroll=ysbFrame2.set)

        for item in self.textures:
            self.Listbox.insert(0, item)

        ysbFrame2.grid(row=2, column=1, sticky='ns')

        # Frame 3
        self.Frame3 = tk.Listbox(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.master.columnconfigure(2, weight=1)

        if not os.path.exists(settings.stencil_metadata):
            os.makedirs(settings.stencil_metadata)

        for file in os.listdir(settings.stencil_metadata):
            json.loads(open(file).read())

        self.Frame3.insert(0, "Create New Stencil...")

        templates = os.listdir(settings.stencil_metadata)
        for item in templates:
            self.Frame3.insert(0, item)

        self.Frame3.bind("<Double-Button-1>", self.click_stencil_edit)

    def click_tree_item(self, event):
        selitems = self.Tree.selection()
        self.textures.clear()

        if selitems:
            self.Listbox.delete(0, "end")
            for item in selitems:                             # Each selection
                folder = os.path.normpath(self.Tree.item(item, "tags")[0])
                for path, subdirs, file_list in os.walk(folder):  # Each folder
                    for name in file_list:                        # Each file
                        key = (path + '\\' + name).replace(settings.default_patches, "")
                        self.textures.append(key)
                        self.Listbox.insert(0, key)

    def click_search_item(self, event):
        searchStr = self.Search.get().lower()
        self.Listbox.delete(0, "end")
        for path in self.textures:
            if searchStr in path.lower():
                self.Listbox.insert(0, path)
        # self.listbox.selection_set(0, "end")

    def click_listbox_item(self, event):

        firstitem = self.Listbox.get(self.Listbox.curselection()[0])

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

    def click_stencil_edit(self, event):
        editor = tk.Toplevel()
        w, h = int(editor.winfo_screenwidth()*1.7), int(editor.winfo_screenheight()*1.7)
        editor.geometry("%dx%d+0+0" % (w, h))
        StencilEditor(editor,
                      stencil=self.Frame3.selection_get(),
                      stenciledit=settings.stencil_editing,
                      stencildir=settings.stencil_metadata,
                      path=settings.default_patches)


root = tk.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

settings = Settings(r"C:/Users/mike_000/Documents/Pycharm/Texture_Synthesis/Synthesizer/config.json")
if not (os.path.exists(settings.default_patches)):
    files.create_default(settings.mods_directory)

app = App(root)
app.mainloop()
