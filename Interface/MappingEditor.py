import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from Synthesizer.images import analyze_image
from Raster.Raster import Raster
from Interface.StencilEditor import StencilEditor

import os, json


class MappingEditor(tk.Frame):
    textures = []
    templates = []

    def __init__(self, master, settings):
        tk.Frame.__init__(self, master)
        self.settings = settings
        self.grid()
        self.master.title("Mapping Editor")
        self.master.iconbitmap(r'C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\favicon.ico')
        self.master.bind("<FocusIn>", self.update_stencil_listing)
        if os.name == 'nt':
            self.master.wm_state('zoomed')

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

        path = self.settings.default_patches.replace('\\', '//')
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
        self.Frame2.rowconfigure(0, minsize=int(master.winfo_screenheight()/2))

        self.Search = tk.Entry(self.Frame2)
        self.Search.grid(row=1, column=0, sticky="w")
        self.Search.bind("<KeyRelease>", self.click_search_item)

        self.filterCategorized = tk.BooleanVar(self.Frame2, value=True)
        checkbox = tk.Checkbutton(self.Frame2,
                                  var=self.filterCategorized,
                                  command=self.toggle_filter)
        checkbox.grid(row=1, column=1, sticky='e')
        label = tk.Label(self.Frame2, text='Hide mapped files')
        label.grid(row=1, column=0, sticky='e')

        self.Frame2.rowconfigure(1)

        self.Listbox = tk.Listbox(self.Frame2, selectmode="extended")
        self.Listbox.grid(row=2, column=0, sticky="nsew")
        self.Listbox.configure(exportselection=False)
        self.Frame2.rowconfigure(2, weight=2)
        self.Frame2.columnconfigure(0, weight=1)

        self.Listbox.bind("<<ListboxSelect>>", self.click_listbox_item)

        ysb_frame2 = ttk.Scrollbar(self.Frame2, orient='vertical', command=self.Listbox.yview)
        self.Listbox.configure(yscroll=ysb_frame2.set)

        for item in self.textures:
            self.Listbox.insert(0, item)

        ysb_frame2.grid(row=2, column=1, sticky='ns')

        # Frame 3
        self.Frame3 = tk.Listbox(master)
        self.Frame3.grid(row=0, column=2, sticky="nsew")
        self.master.columnconfigure(2, weight=1)

        if not os.path.exists(self.settings.stencil_metadata):
            os.makedirs(self.settings.stencil_metadata)

        if not os.path.exists(self.settings.mappings_metadata):
            os.makedirs(self.settings.mappings_metadata)

        self.update_stencil_listing(None)

        self.Frame3.bind("<Button-3>", self.click_stencil_edit)
        self.Frame3.bind("<Double-Button-1>", self.click_stencil_select)

    def click_tree_item(self, event):
        selitems = self.Tree.selection()
        self.textures.clear()
        if selitems:
            self.Listbox.delete(0, "end")
            for item in selitems:                             # Each selection
                folder = os.path.normpath(self.Tree.item(item, "tags")[0])
                for path, subdirs, file_list in os.walk(folder):  # Each folder
                    for name in file_list:                        # Each file
                        key = (path + '\\' + name).replace(self.settings.default_patches, "")
                        if not key in self.textures:
                            self.textures.append(key)
        self.click_search_item(None)

    def click_search_item(self, event):
        search_str = self.Search.get().lower()
        self.Listbox.delete(0, "end")
        for path in self.textures:
            if search_str in path.lower():
                mappingloc = os.path.normpath(self.settings.mappings_metadata_custom + '//' + path + '.json')
                if not (self.filterCategorized.get() and os.path.exists(mappingloc)):
                    self.Listbox.insert(0, path)
        # self.listbox.selection_set(0, "end")

    def click_listbox_item(self, event):
        try:
            firstitem = self.Listbox.get(self.Listbox.curselection()[0])
        except IndexError:
            return

        imageselected = Image.open(self.settings.default_patches + '\\' + firstitem)
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
        selection = self.Listbox.curselection()
        if self.Frame3.curselection()[0] > 0:
            editor = tk.Toplevel()
            w_t, h_t = int(editor.winfo_screenwidth()*1.7), int(editor.winfo_screenheight()*1.7)
            editor.geometry("%dx%d+0+0" % (w_t, h_t))

            selection_stencil = self.Frame3.get(self.Frame3.curselection())
            StencilEditor(editor,
                          stencil=selection_stencil,
                          stenciledit=self.settings.stencil_editing,
                          stencildir=self.settings.stencil_metadata,
                          default_patches=self.settings.default_patches,
                          textures=[json.load(open(
                              self.settings.stencil_metadata + '//' + selection_stencil + '.json'))['path']])

        elif selection:
            editor = tk.Toplevel()
            w_t, h_t = int(editor.winfo_screenwidth()*1.7), int(editor.winfo_screenheight()*1.7)
            editor.geometry("%dx%d+0+0" % (w_t, h_t))

            items = [self.Listbox.get(selection) for selection in selection]
            StencilEditor(editor,
                          stencil=self.Frame3.selection_get(),
                          stenciledit=self.settings.stencil_editing,
                          stencildir=self.settings.stencil_metadata,
                          default_patches=self.settings.default_patches,
                          textures=items)

        elif self.textures:
            editor = tk.Toplevel()
            w_t, h_t = int(editor.winfo_screenwidth()*1.7), int(editor.winfo_screenheight()*1.7)
            editor.geometry("%dx%d+0+0" % (w_t, h_t))

            StencilEditor(editor,
                          stencil=self.Frame3.selection_get(),
                          stenciledit=self.settings.stencil_editing,
                          stencildir=self.settings.stencil_metadata,
                          default_patches=self.settings.default_patches,
                          textures=self.textures)

    def click_stencil_select(self, event):
        if self.Frame3.curselection()[0] == 0:
            return

        stencil_name = self.Frame3.get(self.Frame3.curselection()[0])
        stencil_data = json.load(open(os.path.normpath(self.settings.stencil_metadata + "\\" + stencil_name + ".json")))
        masks = stencil_data['mask']

        for selection in self.Listbox.curselection():
            relative_path = self.Listbox.get(selection)
            image = Raster.from_image(Image.open(
                self.settings.default_patches + '//' + relative_path).resize(stencil_data['shape'], Image.NEAREST), "RGBA")


            segment_metalist = []
            for ident, mask in enumerate(masks):
                if stencil_data['colorize'][ident]:
                    image.mask = mask
                    segment_data = analyze_image(image)
                    segment_data['id'] = ident
                    segment_data['colorize'] = True
                    segment_metalist.append(segment_data)
                else:
                    segment_data = {}
                    segment_data['id'] = ident
                    segment_data['colorize'] = False
                    segment_metalist.append(segment_data)

            meta_dict = {
                'group_name': stencil_name,
                'segment_dicts': segment_metalist
            }

            output_path = os.path.split(self.settings.mappings_metadata_custom + relative_path)[0]

            # Create folder structure
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # Save json file
            with open(output_path + "\\" + os.path.basename(relative_path) + ".json", 'w') as output_file:
                json.dump(meta_dict, output_file, sort_keys=True, indent=2)
        self.click_search_item(None)

    def update_stencil_listing(self, event):
        try:
            stencil_name = self.Frame3.get(self.Frame3.curselection()[0])
        except IndexError:
            stencil_name = ''

        self.Frame3.delete(0, 'end')
        self.Frame3.insert(0, "Create New Stencil...")

        for file in os.listdir(self.settings.stencil_metadata):
            self.Frame3.insert(1, json.loads(
                open(self.settings.stencil_metadata + '\\' + file).read())['name'].replace('.json', ''))

        try:
            index = self.Frame3.get(0, 'end').index(stencil_name)
            self.Frame3.select_set(index)
            self.Frame3.see(index)
        except ValueError:
            self.Frame3.selection_set(0)

    def toggle_filter(self):
        self.click_search_item(None)
