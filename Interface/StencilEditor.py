import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, json
import numpy as np
from Raster.Raster import Raster
from Raster.filters import colorize, composite
from colorsys import hsv_to_rgb
from Synthesizer.metadata import stencils


class StencilEditor(tk.Frame):
    stencilpaths = []
    stencil_data = None

    layer_quantity = 1
    colorize = []

    hues = [0.68, 0.32, 0.97, 0.50, 0.17, 0.86, 0.44, 0.09, 0.78, 0.57]

    def __init__(self, master, stencil, stenciledit, stencildir, default_patches, textures):
        tk.Frame.__init__(self, master)
        self.stencilname = stencil
        self.stenciledit = stenciledit
        self.stencildir = stencildir
        self.default_patches = default_patches.replace('\\', '//')

        self.grid()
        self.master.title(stencil)

        self.master.rowconfigure(0, weight=1)

        try:
            self.load_stencil(None)
        except FileNotFoundError:
            self.imagestencil = Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil.png")
            self.imagestencilmasked = Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil_masked.png")

        # Frame 1
        self.master.columnconfigure(0, weight=1)
        self.Frame1 = tk.Frame(master)
        self.Frame1.grid(row=0, column=0, sticky="nsew")
        self.Frame1.columnconfigure(0, weight=1)

        self.Listbox = tk.Listbox(self.Frame1)
        self.Listbox.grid(row=0, column=0, sticky="nsew")
        self.Frame1.rowconfigure(0, weight=1)

        self.Listbox.bind("<<ListboxSelect>>", self.prepare_stencils)

        for path in textures:
            self.Listbox.insert(0, path)
        self.Listbox.selection_set(0)

        ysb = ttk.Scrollbar(self.Frame1, orient='vertical', command=self.Listbox.yview)
        self.Listbox.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=1, sticky='ns')

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

        self.labelname = tk.Label(self.Frame3, text="Name")
        self.labelname.grid(row=0, column=0, sticky="w")
        self.entryname = tk.Entry(self.Frame3)
        self.entryname.grid(row=0, column=0, sticky="e")
        self.Frame3.rowconfigure(0)

        self.labelquantity = tk.Label(self.Frame3, text="Quantity")
        self.labelquantity.grid(row=1, column=0, sticky="w")
        self.quantityvar = tk.IntVar(self.Frame3)
        self.quantityvar.set(self.layer_quantity)

        self.optionquantity = tk.OptionMenu(self.Frame3, self.quantityvar, 1,2,3,4,5,6,7,8,9,10,
                                            command=self.click_quantity_item)
        self.optionquantity.grid(row=1, column=0, sticky="ne")
        self.Frame3.rowconfigure(1)

        self.LayerFrame = tk.Frame(self.Frame3)
        self.LayerFrame.grid(row=2, column=0, sticky="nsew")
        self.Frame3.rowconfigure(2, weight=1)

        self.LayerLabels = []
        self.LayerButtons = []
        self.LayerRecolor = []

        self.make_layer_gui()
        self.ButtonSave = tk.Button(self.Frame3, text="SAVE", command=self.save_stencil)
        self.ButtonSave.grid(row=3, column=0, sticky="nsew")
        self.Frame3.rowconfigure(3)

        self.prepare_stencils(None)

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

        self.relative_path = self.Listbox.get(self.Listbox.curselection()[0])

        absolutepath = os.path.normpath(self.default_patches + "//" + self.relative_path)

        name = os.path.basename(absolutepath).replace('.png', '')
        self.stencilname = name
        self.entryname.delete(0, "end")
        self.entryname.insert(0, name)
        self.master.title(name)

        renderimage = Image.open(absolutepath)

        dim = min(renderimage.size)

        renderimage = renderimage.crop((0, 0, dim, dim))
        renderimage = renderimage.resize((400, 400), Image.NEAREST)

        renderphoto = ImageTk.PhotoImage(renderimage)

        self.imagebox.configure(image=renderphoto)
        self.imagebox.image = renderphoto

        for stencilpath in self.stencilpaths:
            os.remove(stencilpath)
        self.stencilpaths.clear()

        self.stencilimage = Image.open(absolutepath)

        for i in range(self.layer_quantity):
            stencilpath = self.stenciledit + '\\' + self.stencilname + '_' + str(i+1) + '.png'
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
            label = tk.Label(self.LayerFrame, text="Layer " + str(i+1))
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

        self.layer_quantity = self.quantityvar.get()
        self.make_layer_gui()
        self.prepare_stencils(None)

    def save_stencil(self):
        stencils.make_stencil(stencil_name=self.stencilname,
                              quantity=self.layer_quantity,
                              stencil_staging=self.stenciledit,
                              stencil_configs=self.stencildir,
                              colorize=self.colorize, #TODO
                              relative_path=self.relative_path)

    def load_stencil(self, event):

        stencil_data = json.load(open(os.path.normpath(self.stencildir + "//" + self.stencilname + ".png")))

        masks = stencil_data['mask']
        self.layer_quantity = len(masks)
        self.relative_path = stencil_data['path']
        self.imagestencil = Image.open(self.default_patches + '//' + self.relative_path, "RGBA")

        for index, mask in enumerate(masks):
            layer = Raster.from_image(self.imagestencil)
            layer.mask = np.array(mask)
            layer.save(self.stenciledit + '//' + self.stencilname + '_' + str(index+1) + '.png')

        self.make_layer_gui()