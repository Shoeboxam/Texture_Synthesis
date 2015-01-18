import numpy as np
from scipy.stats.stats import pearsonr
import os
from PIL import ImageEnhance
from PIL import Image

home = r"C:\Users\mike_000\AppData\Roaming\.ftb\FTBResurrection\minecraft"
threshold = 0.90

template_img = ImageEnhance.Color(Image.open(r"C:\Users\mike_000\Desktop\planks_oak.png")).enhance(0)
template = template_img.convert("L").getdata()


def correlate(list_one, list_two, threshold):
    try:
        correlation = pearsonr(list_one, list_two)[0]
        # print(correlation)
        return correlation > threshold
    except:
        return False

for root, dirs, files in os.walk(home + "\\resourcepacks\\default\\"):
    for current_file in files:
        img = Image.open(root + "\\" + current_file)

        if (img.size == template_img.size):
            candidate = img.convert("L").getdata()

            if(correlate(template, candidate, threshold)):
                print(current_file)

            # np.asarray()
