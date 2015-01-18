from scipy.stats.stats import pearsonr
import os
from PIL import Image

home = r"C:\Users\mike_000\AppData\Roaming\.ftb\FTBResurrection\minecraft"
threshold = 0.80

template_img = Image.open(r"C:\Users\mike_000\Desktop\planks_oak.png")
template = template_img.convert("L").getdata()

for root, dirs, files in os.walk(home + "\\resourcepacks\\default\\"):
    for current_file in files:
        img = Image.open(root + "\\" + current_file)

        if (img.size == template_img.size):
            candidate = img.convert("L").getdata()

            if(pearsonr(template, candidate)[0] > threshold):
                print(current_file)
