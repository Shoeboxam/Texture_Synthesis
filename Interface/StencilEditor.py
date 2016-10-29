import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, json
import numpy as np
from Raster.Raster import Raster
from Raster.filters import colorize, composite
from colorsys import hsv_to_rgb
from Synthesizer.metadata import stencils

import webbrowser


class StencilEditor(tk.Frame):
    stencilpaths = []
    stencil_data = None

    layer_quantity = 1
    colorize = [True]

    hues = [0.68, 0.32, 0.97, 0.50, 0.17, 0.86, 0.44, 0.09, 0.78, 0.57]

    def __init__(self, master, stencil, stenciledit, stencildir, default_patches, textures):
        tk.Frame.__init__(self, master)
        if os.name == 'nt':
            self.master.wm_state('zoomed')
        self.master = master
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.LayerLabels = []
        self.LayerButtons = []
        self.LayerRecolor = []

        self.stencilname = stencil
        self.stenciledit = stenciledit
        self.stencildir = stencildir
        self.default_patches = default_patches.replace('\\', '//')

        self.grid()
        self.master.title(stencil)

        self.master.rowconfigure(0, weight=1)

        self.imagestencil = Image.open(r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil.png")
        self.imagestencilmasked = Image.open(
            r"C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\stencil.png")

        try:
            self.load_stencil()
            self.loaded = True
        except FileNotFoundError:
            self.loaded = False

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
        self.entryname.insert(0, self.stencilname)
        self.Frame3.rowconfigure(0)

        self.labelquantity = tk.Label(self.Frame3, text="Quantity")
        self.labelquantity.grid(row=1, column=0, sticky="w")
        self.quantityvar = tk.IntVar(self.Frame3)
        self.quantityvar.set(self.layer_quantity)

        self.optionquantity = tk.OptionMenu(self.Frame3, self.quantityvar, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                            command=self.click_quantity_item)
        self.optionquantity.grid(row=1, column=0, sticky="ne")
        self.Frame3.rowconfigure(1)

        self.LayerFrame = tk.Frame(self.Frame3)
        self.LayerFrame.grid(row=2, column=0, sticky="nsew")
        self.Frame3.rowconfigure(2, weight=1)

        self.make_layer_gui()
        self.ButtonSave = tk.Button(self.Frame3, text="SAVE", command=self.save_stencil)
        self.ButtonSave.grid(row=3, column=0, sticky="nsew")
        self.Frame3.rowconfigure(3)

        if self.loaded:
            self.update_stencils()
        else:
            self.prepare_stencils(None)

    def image_masker(self):
        raster_layers = []

        for i, stencilpath in enumerate(self.stencilpaths):
            image = Image.open(stencilpath)
            dim = min(image.size)
            image = image.crop((0, 0, dim, dim))

            layer = Raster.from_image(image, "RGBA")
            if self.colorize[i]:
                layer = colorize(layer, self.hues[i], 1, .5, 1, .7, .5)

            raster_layers.append(layer)

        return composite(raster_layers).get_image().resize((400, 400), Image.NEAREST)

    def prepare_stencils(self, event):

        self.relative_path = self.Listbox.get(self.Listbox.curselection())

        absolutepath = os.path.normpath(self.default_patches + "//" + self.relative_path)

        name = os.path.basename(absolutepath).replace('.png', '')
        self.stencilname = name
        self.entryname.delete(0, "end")
        self.entryname.insert(0, name)
        self.master.title("Editing stencil: " + name)
        try:
            renderimage = Image.open(absolutepath)
        except OSError:
            self.Listbox.delete(self.Listbox.curselection())
            return

        dim = min(renderimage.size)

        renderimage = renderimage.crop((0, 0, dim, dim))
        renderimage = renderimage.resize((400, 400), Image.NEAREST)

        renderphoto = ImageTk.PhotoImage(renderimage)

        self.imagebox.configure(image=renderphoto)
        self.imagebox.image = renderphoto

        for stencilpath in self.stencilpaths:
            if os.path.exists(stencilpath):
                os.remove(stencilpath)
        self.stencilpaths.clear()

        self.imagestencil = Image.open(absolutepath)

        for i in range(self.layer_quantity):
            stencilpath = self.stenciledit + '\\' + self.stencilname + '_' + str(i+1) + '.png'
            self.stencilpaths.append(stencilpath)
            self.imagestencil.save(stencilpath)

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

        self.enable = []

        for i in range(self.layer_quantity):
            label = tk.Label(self.LayerFrame, text="Layer " + str(i+1))
            label.grid(row=i, column=0, sticky="w")
            self.LayerLabels.append(label)

            self.enable.append(tk.BooleanVar(self.Frame3))
            if (i < len(self.colorize)):
                self.enable[i].set(self.colorize[i])
            else:
                self.enable[i].set(True)

            checkbox = tk.Checkbutton(self.LayerFrame,
                                      var=self.enable[i],
                                      command=lambda i1=i: self.toggle_checkbox(i1))

            checkbox.grid(row=i, column=1)
            self.LayerRecolor.append(checkbox)

            r, g, b = hsv_to_rgb(self.hues[i], 1, .8)
            color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            button = tk.Button(self.LayerFrame, bg=color, text="Edit", command=lambda i1=i: self.open_texture(i1))
            button.grid(row=i, column=3, sticky="e")
            self.LayerButtons.append(button)

    def open_texture(self, index):
        path = os.path.normpath(self.stenciledit + '\\' + self.stencilname + '_' + str(index + 1) + '.png')
        webbrowser.open(path)

    def toggle_checkbox(self, index):
        self.colorize[index] = self.enable[index].get()
        self.update_stencils()

    def click_quantity_item(self, event):

        self.layer_quantity = self.quantityvar.get()
        while self.layer_quantity >= len(self.colorize):
            self.colorize.append(True)
        self.make_layer_gui()
        self.update_stencils()

    def save_stencil(self):
        stencils.make_stencil(stencil_name=self.stencilname,
                              quantity=self.layer_quantity,
                              stencil_staging=self.stenciledit,
                              stencil_configs=self.stencildir,
                              colorize=self.colorize,
                              relative_path=self.relative_path)
        self.on_closing()

    def load_stencil(self):
        stencil_data = json.load(open(os.path.normpath(self.stencildir + "\\" + self.stencilname + ".json")))
        masks = stencil_data['mask']
        self.layer_quantity = len(masks)
        self.relative_path = stencil_data['path']
        self.imagestencil = Image.open(self.default_patches + '\\' + self.relative_path)
        self.stencilname = stencil_data['name']
        self.master.title("Editing stencil: " + self.stencilname)
        self.colorize = stencil_data['colorize']

        self.stencilpaths.clear()
        for index, mask in enumerate(masks):
            layer = Raster.from_image(self.imagestencil)
            layer.mask = np.array(mask)
            stencilpath = self.stenciledit + '\\' + self.stencilname + '_' + str(index+1) + '.png'
            layer.save(stencilpath)
            self.stencilpaths.append(stencilpath)

    def update_stencils(self):

        self.imagestencil = Image.open(os.path.normpath(self.default_patches + '\\' + self.relative_path))
        renderphoto = ImageTk.PhotoImage(self.imagestencil.resize((400, 400), Image.NEAREST))

        self.imagebox.configure(image=renderphoto)
        self.imagebox.image = renderphoto

        self.stencilpaths.clear()
        for i in range(self.layer_quantity):
            stencilpath = self.stenciledit + '\\' + self.stencilname + '_' + str(i+1) + '.png'
            self.stencilpaths.append(stencilpath)
            if not os.path.exists(stencilpath):
                self.imagestencil.save(stencilpath)

        renderimage_masked = ImageTk.PhotoImage(self.image_masker())

        self.imagemaskbox.configure(image=renderimage_masked)
        self.imagemaskbox.image = renderimage_masked

        self.make_layer_gui()

    def on_closing(self):
        for i in range(10):
            stencilpath_temp = os.path.normpath(self.stenciledit + '//' + self.stencilname + '_' + str(i) + '.png')

            if os.path.exists(stencilpath_temp):
                os.remove(stencilpath_temp)

        self.master.destroy()
