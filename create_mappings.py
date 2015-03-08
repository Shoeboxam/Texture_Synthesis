from PIL import Image
from zipfile import ZipFile
from scipy.stats.stats import pearsonr

from create_default import *


def extract_defaults(home, jar_path):
    vanilla_dir = home + "\\resourcepacks\\default_vanilla\\"
    zip_ob = ZipFile(jar_path)

    zip_ob.extractall(vanilla_dir)

    # Remove lock
    zip_ob.close()
    remove_cruft(vanilla_dir)


def create_template_index(template_path):
    matches = []
    keys = os.listdir(template_path + '\\keys\\')
    values = os.listdir(template_path + '\\values\\')

    for filename_default, filename_replacer in zip(keys, values):
        if (filename_default == filename_replacer):
            matches.append(filename_default)
        else:
            print("Incomplete template pairing: " + filename_default)

    return matches


# Convert from path to brightness list
def pixelate(path):
    image_input = Image.open(path)
    return image_input.convert("L").getdata()


# Template must already be in list format- performance optimization
def correlate(template, candidate):

    if (template.size != candidate.size):
        return 0

    # This number is... magic!
    threshold = .7
    return threshold < abs(pearsonr(template, candidate)[0])


def create_identification_dictionary(target, template_path):
    # Load template images into variables
    image_keys = {}

    template_filenames = os.listdir(template_path + "\\keys\\")

    template_images = []
    for filename in template_filenames:
        template_images.append(pixelate(template_path + "\\keys\\" + filename))

    for root, folders, files in os.walk(target):
        for current_file in files:
            full_path = root + "\\" + current_file

            for temp_pixels, temp_filename in zip(template_images, template_filenames):
                if correlate(temp_pixels, pixelate(full_path)):
                    image_keys[full_path.replace(target, "")] = temp_filename

    return image_keys
