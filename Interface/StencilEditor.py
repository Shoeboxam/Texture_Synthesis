import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, random, json, copy
from Raster.Raster import Raster
from Raster.filters import colorize, composite


class StencilEditor(tk.Frame):
    stencilpaths = []
    stencil_data = None

    layer_quantity = 1

    def __init__(self, master, stencil, stencildir, path):
        tk.Frame.__init__(self, master)
        self.stencilname = stencil
        self.stencildir = stencildir
        self.default_patches = path
        path = path.replace('\\', '//')

        self.grid()
        self.master.title(stencil)

        self.master.rowconfigure(0, weight=1)

        try:
            self.stencil_data = json.load(open(stencildir + "\\" + stencil + ".json"))
            self.imagestencil = ImageTk.PhotoImage(Image.open(self.stencil_data["path"]))
        except FileNotFoundError:
            self.imagestencil = Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil.png")
            self.imagestencilmasked = Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil_masked.png")

        # Frame 1
        self.master.columnconfigure(0, weight=1)
        self.Frame1 = tk.Frame(master)
        self.Frame1.grid(row=0, column=0, sticky="nsew")
        self.Frame1.columnconfigure(0, weight=1)

        self.labelname = tk.Label(self.Frame1, text="Name")
        self.labelname.grid(row=0, column=0, sticky="w")
        self.entryname = tk.Entry(self.Frame1)
        self.entryname.grid(row=0, column=0, sticky="e")
        self.Frame1.rowconfigure(0)

        self.labelquantity = tk.Label(self.Frame1, text="Quantity")
        self.labelquantity.grid(row=1, column=0, sticky="w")
        self.entryquantity = tk.Entry(self.Frame1)
        self.entryquantity.grid(row=1, column=0, sticky="e")
        self.Frame1.rowconfigure(2)

        self.Tree = ttk.Treeview(self.Frame1)
        self.Tree.grid(row=3, column=0, sticky="nsew")
        self.Frame1.rowconfigure(3, weight=1)

        self.Tree.bind("<<TreeviewSelect>>", self.prepare_stencils)

        self.Tree.heading('#0', text="Resources", anchor='w')

        ysb = ttk.Scrollbar(self.Frame1, orient='vertical', command=self.Tree.yview)
        self.Tree.configure(yscroll=ysb.set)

        root_node = self.Tree.insert('', 'end', text=path, open=True)
        self.process_directory(root_node, path, self.Tree)

        ysb.grid(row=3, column=1, sticky='ns')

        # Frame 2
        self.master.columnconfigure(1, weight=1)
        self.Frame2 = tk.Frame(master)
        self.Frame2.grid(row=0, column=1, sticky="nsew")

        self.imagebox = tk.Label(self.Frame2, image=self.imagestencil)
        self.imagebox.grid(row=0, column=0, sticky="nsew")
        self.Frame2.rowconfigure(0, minsize=int(master.winfo_screenheight()/2))

        if self.stencil_data:
            self.imagestencilmasked = self.image_masker()

        self.imagemaskbox = tk.Label(self.Frame2, image=ImageTk.PhotoImage(self.imagestencilmasked))
        self.imagebox.grid(row=1, column=1, sticky="nsew")
        self.Frame2.rowconfigure(0, minsize=int(master.winfo_screenheight()/2))

        # Frame 3
        self.master.columnconfigure(0, weight=1)
        self.Frame3 = tk.Frame(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.Frame1.columnconfigure(0, weight=1)

    def process_directory(self, parent, path, tree):

        for p in os.listdir(path):
            abspath = os.path.join(path + "//", p)
            isdir = os.path.isdir(abspath)
            if not isdir:
                tree.insert(parent, 'end', text=p, tags=abspath, open=False)
            else:
                oid = tree.insert(parent, 'end', text=p, open=False)
                self.process_directory(oid, abspath, tree)

    def image_masker(self):
        raster_layers = []

        for stencilpath in self.stencilpaths:
            layer = Raster.from_path(stencilpath, "RGBA")
            raster_layers.append(colorize(layer, random.uniform(0, 1), 0, .5, .8, 0, .5))

        renderimage = composite(raster_layers).get_image()
        dim = min(renderimage.size)
        renderimage.crop((0, 0, dim, dim))

        return renderimage.resize((400, 400), Image.NEAREST)

    def prepare_stencils(self, event):

        selitem = self.Tree.selection()[0]
        try:
            relative_path = os.path.normpath(self.Tree.item(selitem, "tags")[0])
        except IndexError:
            return

        self.stencilimage = Image.open(self.default_patches + '\\' + relative_path)

        renderimage = copy.deepcopy(self.stencilimage)
        dim = min(renderimage.size)

        renderimage.crop((0, 0, dim, dim))
        renderimage.resize((400, 400), Image.NEAREST)

        self.imagebox.configure(image=ImageTk.PhotoImage(renderimage))
        self.imagebox.image = ImageTk.PhotoImage(renderimage)

        for stencilpath in self.stencilpaths:
            os.remove(stencilpath)
        self.stencilpaths.clear()

        for i in range(self.layer_quantity):
            stencilpath = self.stencildir + '\\' + self.stencilname + '_' + str(i) + '.png'
            self.stencilpaths.append(stencilpath)
            self.stencilimage.save(stencilpath)

        renderimage = ImageTk.PhotoImage(self.image_masker())

        self.imagemaskbox.configure(image=renderimage)
        self.imagemaskbox.image = renderimage
