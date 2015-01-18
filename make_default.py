import zipfile
import os


home = os.getcwd()

for file in os.listdir(home + "\\mods\\"):
    if file.endswith(".jar"):
        zip_ob = zipfile.ZipFile(home + "\\mods\\" + file)
        zip_ob.extractall(home + "\\resourcepacks\\default\\")

        print(file)

for root, dirs, files in os.walk(home + "\\resourcepacks\\default\\"):
    for currentFile in files:
        if not currentFile.endswith('.png'):
            os.remove(os.path.join(root, currentFile))
