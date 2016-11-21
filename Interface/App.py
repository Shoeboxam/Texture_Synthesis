from Synthesizer.sources import files
from Synthesizer.settings import Settings
from Interface.MappingEditor import MappingEditor
from Synthesizer.sources.files import create_default
from Synthesizer.metadata.stencils import apply_stencil
from Raster.Raster import Raster
from Utilities.vectorize import vectorize

import threading
import json
import webbrowser
import os
import tkinter as tk


class App(tk.Frame):

    def __init__(self, master, settings):
        tk.Frame.__init__(self, master)

        self.settings = settings
        if not (os.path.exists(settings.default_patches)):
            print("Creating default texture pack. This may take a few minutes.")
            print(settings.default_patches)
            files.create_default(settings)

        self.grid()
        self.master.title("Synthesizer")
        self.master.iconbitmap(r'C:\Users\mike_000\Documents\Pycharm\Texture_Synthesis\Interface\favicon.ico')

        self.master.bind("<FocusIn>", self.update_resourcepack_listing)
        if os.name == 'nt':
            self.master.wm_state('zoomed')

        self.master.rowconfigure(0, weight=1)

        # Frame 1
        self.Frame1 = tk.Frame(master)
        self.Frame1.grid(row=0, column=0, sticky="nsw")

        labelhome = tk.Label(self.Frame1, text="Home")
        labelhome.grid(row=0, column=0, sticky='w')
        self.homefolderbutton = tk.Button(self.Frame1,
                                          text=self.settings.home,
                                          command=self.open_home)
        self.homefolderbutton.grid(row=0, column=1, sticky='we')

        labelresourcepack = tk.Label(self.Frame1, text="Resourcepacks")
        labelresourcepack.grid(row=1, column=0, sticky='w')
        self.resourcefolderbutton = tk.Button(self.Frame1,
                                              text=self.settings.resource_skeletons.replace(self.settings.home, ''),
                                              command=self.open_resource_skeletons)
        self.resourcefolderbutton.grid(row=1, column=1, sticky='we')

        labelmappings = tk.Label(self.Frame1, text="Mappings")
        labelmappings.grid(row=2, column=0, sticky='w')
        self.mappingsfolderbutton = tk.Button(self.Frame1,
                                              text=self.settings.mappings_metadata_custom.replace(self.settings.home, ''),
                                              command=self.open_mappings)
        self.mappingsfolderbutton.grid(row=2, column=1, sticky='we')

        labelstencils = tk.Label(self.Frame1, text="Stencils")
        labelstencils.grid(row=3, column=0, sticky='w')
        self.stencilsfolderbutton = tk.Button(self.Frame1,
                                              text=self.settings.stencil_metadata.replace(self.settings.home, ''),
                                              command=self.open_stencils)
        self.stencilsfolderbutton.grid(row=3, column=1, sticky='we')

        labelmods = tk.Label(self.Frame1, text="Mods")
        labelmods.grid(row=4, column=0, sticky='w')
        self.modsfolderbutton = tk.Button(self.Frame1,
                                          text=self.settings.mods_directory.replace(self.settings.home, ''),
                                          command=self.open_mods)
        self.modsfolderbutton.grid(row=4, column=1, sticky='wen')

        labeloutput = tk.Label(self.Frame1, text="Output")
        labeloutput.grid(row=5, column=0, sticky='w')
        self.outputfolderbutton = tk.Button(self.Frame1,
                                            text=self.settings.output_path.replace(self.settings.home, ''),
                                            command=self.open_output)
        self.outputfolderbutton.grid(row=5, column=1, sticky='we')

        splitter = tk.Label(self.Frame1, text='')
        splitter.grid(row=15, column=0, sticky='nswe')
        splitter = tk.Label(self.Frame1, text='Operations')
        splitter.grid(row=15, column=0, sticky='nswe')

        self.mappingbutton = tk.Button(self.Frame1, text='Edit Mappings', command=self.edit_mappings)
        self.mappingbutton.grid(row=16, column=0, sticky='nsew')

        self.generate_defaults_button = tk.Button(self.Frame1, text='Generate Defaults', command=self.generate_defaults)
        self.generate_defaults_button.grid(row=17, column=0, sticky='nsew')

        self.synthesizebutton = tk.Button(self.Frame1, text='SYNTHESIZE', command=self.synthesize)
        self.synthesizebutton.grid(row=20, column=0, columnspan=2, sticky='new')

        # Frame 2
        self.Frame2 = tk.Frame(master)
        self.Frame2.grid(row=0, column=1, sticky="nsew")
        self.master.columnconfigure(1, weight=1)
        self.Frame2.rowconfigure(0, weight=1)
        self.Frame2.columnconfigure(0, weight=1)

        self.ResourcepackListing = tk.Listbox(self.Frame2, selectmode="extended")
        self.ResourcepackListing.grid(row=0, column=0, sticky='nsew')
        self.ResourcepackListing.configure(exportselection=False)

        self.ResourcepackListing.bind("<Double-Button-1>", self.click_resourcepack)

        self.ResourcepackListing.focus_set()

    def edit_mappings(self):
        editor = tk.Toplevel()
        w_e, h_e = editor.winfo_screenwidth(), editor.winfo_screenheight()
        editor.geometry("%dx%d+0+0" % (w_e, h_e))

        mapedit = MappingEditor(editor, self.settings)
        mapedit.mainloop()

    def generate_defaults(self):
        create_default(self.settings)

    def open_home(self):
        if not os.path.exists(self.settings.home):
            os.makedirs(self.settings.home)
        webbrowser.open(self.settings.home)

    def open_resource_skeletons(self):
        if not os.path.exists(self.settings.resource_skeletons):
            os.makedirs(self.settings.resource_skeletons)
        webbrowser.open(self.settings.resource_skeletons)

    def open_mappings(self):
        if not os.path.exists(self.settings.mappings_metadata_custom):
            os.makedirs(self.settings.mappings_metadata_custom)
        webbrowser.open(self.settings.mappings_metadata_custom)

    def open_stencils(self):
        if not os.path.exists(self.settings.stencil_metadata):
            os.makedirs(self.settings.stencil_metadata)
        webbrowser.open(self.settings.stencil_metadata)

    def open_mods(self):
        if not os.path.exists(self.settings.mods_directory):
            os.makedirs(self.settings.mods_directory)
        webbrowser.open(self.settings.mods_directory)

    def open_output(self):
        if not os.path.exists(self.settings.output_path):
            os.makedirs(self.settings.output_path)
        webbrowser.open(self.settings.output_path)

    def update_resourcepack_listing(self, event):

        try:
            rp_name = self.ResourcepackListing.get(self.ResourcepackListing.curselection()[0])
        except IndexError:
            rp_name = 'Create New Resourcepack...'

        self.ResourcepackListing.delete(0, 'end')
        self.ResourcepackListing.insert(0, 'Create New Resourcepack...')
        self.ResourcepackListing.selection_set(0)
        for folder in os.listdir(self.settings.resource_skeletons):
            self.ResourcepackListing.insert(1, folder)

        try:
            index = self.ResourcepackListing.get(0, 'end').index(rp_name)
            self.ResourcepackListing.select_set(index)
            self.ResourcepackListing.see(index)
        except ValueError:
            self.ResourcepackListing.selection_set(0)

        self.ResourcepackListing.focus_set()

    def synthesize(self):
        resourcepacks = self.ResourcepackListing.curselection()
        for pack in resourcepacks:
            rp_folder = self.ResourcepackListing.get(pack)
            if rp_folder is "Create New Resourcepack...":
                continue
            stencil_paths = []
            for root, folders, files in os.walk(self.settings.mappings_metadata_custom):
                for image_file in files:
                    full_path = os.path.join(root, image_file)

                    with open(full_path, 'r') as json_file:
                        mapping_data = json.load(json_file)
                        stencil_paths.append((full_path, mapping_data))

            t = threading.Thread(target=vectorize, args=(stencil_paths, apply_stencil, [self.settings, rp_folder]))
            t.start()

    def click_resourcepack(self, event):
        selection = self.ResourcepackListing.curselection()
        if selection[0] == 0:
            if not os.path.exists(self.settings.resource_skeletons + 'New_Resourcepack'):
                os.makedirs(self.settings.resource_skeletons + 'New_Resourcepack')
            resourcepack_folder = 'New_Resourcepack'
        else:
            resourcepack_folder = self.ResourcepackListing.get(selection[0])

        for stencil in os.listdir(self.settings.stencil_metadata):
            stencil_data = json.load(open(self.settings.stencil_metadata + '\\' + stencil))
            masks = stencil_data['mask']

            for ident, mask in enumerate(masks):
                path = self.settings.resource_skeletons + \
                       resourcepack_folder + '\\' + stencil.replace('.json', '') + '_' + str(ident+1) + '.png'
                if os.path.exists(path):
                    continue

                layer = Raster.from_path(self.settings.default_patches + '\\' + stencil_data['path'], "RGBA")
                layer.mask = mask
                layer.save(path)


if __name__ == '__main__':
    settings = Settings(r"C:/Users/mike_000/Documents/Pycharm/Texture_Synthesis/Synthesizer/config.json")

    root = tk.Tk()
    w, h = int(root.winfo_screenwidth()/2), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))

    app = App(root, settings)
    app.mainloop()
