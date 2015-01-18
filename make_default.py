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


def cleanup_folder(path):
    file_list = os.listdir(path)

    # Recurse if child folder
    for file in file_list:
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            cleanup_folder(file_path)

    # Delete if empty folder
    if len(file_list) == 0:
        os.rmdir(path)

cleanup_folder(home + "\\resourcepacks\\default\\")
