# -*- coding: utf-8 -*-
"""
The code generates a .gif animation from images in .png, .jpg, .tif
and other image file formats.

@author: Siddharth Shankar
"""

import imageio
from fnmatch import fnmatch
import os
from datetime import datetime as dt
from tqdm import tqdm

images = []

# User inputs
# path_ = r'D:\track_bergs\coastal_icebergs_test\iceberg_test1\png'#r'path/to/dir'#dpi-150
# path_ = r'D:\track_bergs\coastal_icebergs_test\iceberg_test2_70imgs\png'
# path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO\png'#r'D:\trackBergs\coastal_icebergs_test\iceberg_test3_90imgs_RINK\png'
# path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png'
# path_ = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip\png'#r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast'

path_ = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiff_clip_2022\png'
pattern = "*.jpg" 
out_gif = "icebergs_143imgs_sermilik_AGU21.mp4"

fileNames = []
for _,dirs,files in os.walk(path_,topdown=True): 
    dirs.clear() #excludes the files in subdirectories
    for name in files:   
        if fnmatch(name,pattern):
            fileNames.append(name)

fileNames.sort(key = lambda x: x.split('_')[4]) 

writer = imageio.get_writer(os.path.join(path_,out_gif),fps=1)
for fileName in tqdm(fileNames):
    writer.append_data(imageio.imread(os.path.join(path_,fileName)))
    # images.append(imageio.imread(os.path.join(path_,fileName)))
# imageio.mimsave(os.path.join(path_,out_gif), images,duration=0.5)
writer.close()

