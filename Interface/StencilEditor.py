import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, random, json, copy
from Raster.Raster import Raster
from Raster.filters import colorize, composite
from colorsys import hsv_to_rgb


class StencilEditor(tk.Frame):
    stencilpaths = []
    stencil_data = None

    layer_quantity = 1

    hues = [random.uniform(0, 1) for x in range(0, 10)]

    def __init__(self, master, stencil, stenciledit, stencildir, path):
        tk.Frame.__init__(self, master)
        self.stencilname = stencil
        self.stenciledit = stenciledit
        self.stencildir = stencildir
        self.default_patches = path
        path = path.replace('\\', '//')

        self.grid()
        self.master.title(stencil)

        self.master.rowconfigure(0, weight=1)

        try:
            self.stencil_data = json.load(open(stencildir + "\\" + stencil + ".json"))
            self.imagestencil = Image.open(self.stencil_data["path"])
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
        self.Frame2 = tk.Frame(master)
        self.Frame2.grid(row=0, column=1, sticky="nsew")
        self.master.columnconfigure(1, weight=1)

        self.imagebox = tk.Label(self.Frame2, image=ImageTk.PhotoImage(self.imagestencil))
        self.imagebox.grid(row=0, column=0, sticky="ns")
        self.Frame2.rowconfigure(0, weight=1)

        if self.stencil_data:
            self.imagestencilmasked = self.image_masker()

        self.imagemaskbox = tk.Label(self.Frame2, image=ImageTk.PhotoImage(self.imagestencilmasked))
        self.imagemaskbox.grid(row=1, column=0, sticky="ns")
        self.Frame2.rowconfigure(1, weight=1)

        # Frame 3
        self.master.columnconfigure(2, weight=1)
        self.Frame3 = tk.Frame(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.Frame3.columnconfigure(0, weight=1)

        self.labelquantity = tk.Label(self.Frame3, text="Quantity")
        self.labelquantity.grid(row=0, column=0, sticky="w")
        self.entryquantity = tk.Entry(self.Frame3)
        self.entryquantity.grid(row=0, column=0, sticky="ne")
        self.Frame3.rowconfigure(0)

        self.entryquantity.bind("<KeyRelease>", self.click_quantity_item)

        self.LayerFrame = tk.Frame(self.Frame3)
        self.LayerFrame.grid(row=1, column=0, sticky="nsew")
        self.Frame3.rowconfigure(1, weight=1)

        self.LayerLabels = []
        self.LayerButtons = []
        self.LayerRecolor = []

        self.make_layer_gui()

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

        for i, stencilpath in enumerate(self.stencilpaths):
            image = Image.open(stencilpath)
            dim = min(image.size)
            image = image.crop((0, 0, dim, dim))

            layer = Raster.from_image(image, "RGBA")
            raster_layers.append(colorize(layer, self.hues[i], 0, .5, 1, 0, .5))

        return composite(raster_layers).get_image().resize((400, 400), Image.NEAREST)

    def prepare_stencils(self, event):

        if not os.path.exists(self.stenciledit):
            os.makedirs(self.stenciledit)

        selitem = self.Tree.selection()[0]

        try:
            relative_path = os.path.normpath(self.Tree.item(selitem, "tags")[0])
        except IndexError:
            return

        name = self.Tree.item(selitem, "text")
        self.stencilname = name
        self.entryname.delete(0, "end")
        self.entryname.insert(0, name)
        self.master.title(name)

        renderimage = Image.open(relative_path)

        dim = min(renderimage.size)

        renderimage = renderimage.crop((0, 0, dim, dim))
        renderimage = renderimage.resize((400, 400), Image.NEAREST)

        renderphoto = ImageTk.PhotoImage(renderimage)

        self.imagebox.configure(image=renderphoto)
        self.imagebox.image = renderphoto

        for stencilpath in self.stencilpaths:
            os.remove(stencilpath)
        self.stencilpaths.clear()

        self.stencilimage = Image.open(relative_path)

        for i in range(self.layer_quantity):
            stencilpath = self.stenciledit + '\\' + self.stencilname + '_' + str(i) + '.png'
            self.stencilpaths.append(stencilpath)
            self.stencilimage.save(stencilpath)

        renderimage_masked = ImageTk.PhotoImage(self.image_masker())

        self.imagemaskbox.configure(image=renderimage_masked)
        self.imagemaskbox.image = renderimage_masked

    def make_layer_gui(self):
        for i in range(len(self.LayerButtons)):
            self.LayerButtons[i].destroy()
            self.LayerLabels[i].destroy()
            self.LayerRecolor[i].destroy()
        self.LayerButtons.clear()
        self.LayerLabels.clear()
        self.LayerRecolor.clear()

        for i in range(self.layer_quantity):
            label = tk.Label(self.LayerFrame, text="Layer " + str(i))
            label.grid(row=i, column=0, sticky="w")
            self.LayerLabels.append(label)

            checkbox = tk.Checkbutton(self.LayerFrame)
            checkbox.grid(row=i, column=1)
            self.LayerRecolor.append(checkbox)

            r, g, b = hsv_to_rgb(self.hues[i], 1, .8)
            color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            button = tk.Button(self.LayerFrame, bg=color, text="Edit")
            button.grid(row=i, column=3, sticky="e")
            self.LayerButtons.append(button)

    def click_quantity_item(self, event):

        try:
            quantity = int(self.entryquantity.get())
            if quantity <= 10:
                self.layer_quantity = quantity
            self.make_layer_gui()
        except ValueError:
            return