#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:39:11 2021

@author: s004s394_a
"""

from PIL import Image
import os
from fnmatch import fnmatch
from osgeo import gdal
import numpy as np

# root2 = r'/home/s004s394_a/Downloads/drive-download-20210803T164550Z-001/'#r'/home/s004s394_a/clips/v3/384/test5'#r'/home/s004s394_a/clips/masks/'
# out_path = r'/home/s004s394_a/Downloads/drive-download-20210803T164550Z-001/track' #r'/home/s004s394_a/clips/v3/384/test5' #384_v2/jpeg/
# root2 = r'/home/s004s394_a/track_bergs/drive-download-20210826T142626Z-001'

# root2 = r'/home/s004s394_a/track_bergs/new_data_for_roboflow/test.v10i.darknet/geotiff_for_mp4'
# out_path = r'/home/s004s394_a/track_bergs/new_data_for_roboflow/test.v10i.darknet/geotiff_for_mp4/pngs'
# out_path = r'/home/s004s394_a/track_bergs/drive-download-20210826T142626Z-001'
# root2 = r'/home/s004s394_a/track_bergs/new_imgs'
# out_path = r'/home/s004s394_a/track_bergs/new_imgs'


# root2 = r'/home/s004s394_a/track_bergs/Melange_split/tif_splits_416/'
# out_path = r'/home/s004s394_a/track_bergs/Melange_split/png_splits_416/'

# root2 = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip/'
# root2 = r'D:\track_bergs\coastal_iceberg_track_416x416/'
# root2 = r'D:\track_bergs\coastal_icebergs_test/'
# root2 = r'D:\track_bergs\coastal_icebergs_test\iceberg_test1'

# =============================================================================
# ENABLE AFTER CONVERTING BACKGROUN IMG TO PNG
# =============================================================================
'''
root2 = r'D:\track_bergs\coastal_icebergs_test\iceberg_test2_70imgs'
out_path= r'D:\track_bergs\coastal_icebergs_test\iceberg_test2_70imgs\png'
'''
# *****************************************************************************
# out_path = r'D:\track_bergs\coastal_icebergs_test\iceberg_test1'#r'D:\track_bergs\coastal_icebergs_test/'#r'D:\track_bergs\coastal_iceberg_track_416x416\png'
'''
root2 = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO'#r'D:\trackBergs\coastal_icebergs_test\iceberg_test3_90imgs_RINK'
out_path = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO\png'# r'D:\trackBergs\coastal_icebergs_test\iceberg_test3_90imgs_RINK\png'
'''

'''
root2 = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1'
out_path = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png_test'
'''

root2 = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip'
out_path = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip\png'
pattern = "*.tif" 
outfile = {}

fileName = []


for _,dirs,files in os.walk(root2,topdown=True): 
    dirs.clear() #excludes the files in subdirectories
    for name in files:   
        if fnmatch(name,pattern):
            fileName.append(name)

print (fileName)

for band1 in fileName:
    outfile = band1.split('.')[0]+'.jpg'#'.png'
    out_file_path = os.path.join(out_path,outfile)
    img = gdal.Open(os.path.join(root2,band1))
    gdal.Translate(out_file_path,img,format='JPEG',scaleParams=[[]])





    # print ("file : " + infile)
    # if infile[-3:] == "tif" or infile[-3:] == "bmp" :
    #    # print "is tif or bmp"
    #    outfile = infile[:-3] + "jpeg"
    #    im = Image.open(infile)
    #    print ("new filename : " + outfile)
    #    out = im.convert("RGB")
    #    out.save(outfile, "JPEG", quality=100)





















# from PIL import Image, ImageMath
# import numpy as np

# # im1 = Image.open('/home/s004s394_a/clips/label_single_band/')

# def convert_tif_png(tif_filename: root2, out_folder:root2):
#     # Open mask with PIL 
#     arr_tif = np.array(Image.open(tif_filename))

#     # change values from 255 to 1
#     im = Image.fromarray(np.where(arr_tif==255, 1, 0))

#     im.save(out_folder/tif_filename.with_suffix('.png').name)
    
#     return im


# convert_tif_png(r'/home/s004s394_a/clips/label_single_band/masked4_singleband.tif', out_path)
