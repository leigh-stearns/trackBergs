#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converting the bounding box centroid (x,y) to georeferenced coordinates

1. Get the transform from the geotiff
2. Get the centroid row, col of the bounding box
3. x = col*transform[1]+ transform[0]
   y = row*transform[5]+ transform[3] 

@author: s004s394_a
"""
import numpy as np
import skimage
from tqdm import tqdm
import geopandas as gpd
import scipy
from shapely.geometry import Point,MultiPoint,mapping
import fiona
import rasterio as ras

'''
1. Combine frame id to raster: Determines the transform to use
2. Combine trackerID to xmin,ymin,xmax,ymax

"frameID": "S1A_IW_GRDH_1SDH_20200103T091148_20200103T091213_030634_0382A1_DB23"

..trackerID 11 : 
    (xmin, ymin, xmax, ymax): (493, 614, 707, 725)
..trackerID 16 : 
    (xmin, ymin, xmax, ymax): (929, 147, 992, 204)
..trackerID 18 :
    (xmin, ymin, xmax, ymax): (809, 317, 917, 428)
    
Bounding Box dimension
----------------------
x = xmin
y = ymin
width =  (xmax-xmin)*10 ---> Width of bounding box in meters
height = (ymax-ymin)*10 ---> Height of bounding box in meters
centroid_bbox = {(xmax+xmin)/2 , (ymax+ymin)/2}

Translate centroid to georeferenced centroid
---------------------------------------------
read_sar = gdal.Open(image_path,GA_ReadOnly)
transform = read_sar.GetGeoTransform()
proj = read_sar.GetProjection()
xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = transform[5]

x_projected = (col*transform_[1])+transform_[0]
y_projected =(row*transform_[5])+transform_[3]

Area = width*height (in sq.meters)
  
'''
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import imageio
from fnmatch import fnmatch
import os
from datetime import datetime as dt
from tqdm import tqdm
from skimage.transform import resize
from skimage.exposure import match_histograms,equalize_adapthist
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal
from datetime import datetime as dt

# =============================================================================
# Read text file for parsing
# =============================================================================

path_txt = r'D:\track_bergs\coastal_icebergs_test\iceberg_test2_70imgs'
txt = 'results_70imgs.txt'
with open(os.path.join(path_txt,txt)) as f:
    lines = f.readlines()

'''
Remove the \n from the string elements of the txt file
'''
for idx,line in enumerate(lines):
    lines[idx] = line.strip()

'''
Create dictionary representing key-value pair of FrameID_{Number} and TrackerID
'''
frames={}
tracker={}
for i in range(70): #number of frames in the video/txt file
    j=i+1
    if(j<70):
        frame_idx_start = lines.index('Frame #:  %s'%(j))
        frame_idx_end = lines.index('Frame #:  %s'%(j+1))
        tracker_id_list = lines[frame_idx_start+1:frame_idx_end]
    else:
        frame_idx_start = lines.index('Frame #:  %s'%(j))
        tracker_id_list = lines[frame_idx_start+1:]
    frames['FrameID_%s'%(j)] = tracker_id_list


for f in range(len(frames)):
    frame=f+1
    

df_txt = pd.DataFrame(columns=['frameID','xmin','ymin','xmax','ymax','width','height'])




images = []

# User inputs
# path_ = r'/home/s004s394_a/track_bergs/new_data_for_roboflow/test.v10i.darknet/geotiff_for_mp4/pngs'
# path_ = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs'
path_ = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csvPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csv_ = 'test1_tracker_Icebergs.csv'

pattern = "*.tif" 

out_gif = os.path.join(path_,"Sermilik_melange_2020_v3.gif")
refer = 'S1A_IW_GRDH_1SDH_20200127T091147_20200127T091212_030984_038EE8_2DFB.png'

print(path_)
fileNames = []
for _,dirs,files in os.walk(path_,topdown=True): 
    dirs.clear() #excludes the files in subdirectories
    for name in files:   
        if fnmatch(name,pattern):
            fileNames.append(name)

fileNames.sort(key = lambda x: x.split('_')[4]) 
print(fileNames)

# Frame dictionary
frameDict = {}
trackDict = {}
Dict = {}

df = pd.read_csv(os.path.join(outPath,csv_))
# df = df.dropna()
# print(df.head())                  
df['x'] = 0
df['y'] = 0
df['Date'] = 0
frame = 1
# Associate fileNames with frames

for file_ in tqdm(fileNames):

    # read_sar = gdal.Open(os.path.join(path_,file_),gdal.GA_ReadOnly)
    # transform_ = read_sar.GetGeoTransform()
    # proj = read_sar.GetProjection()
    # xOrigin = transform_[0]
    # yOrigin = transform_[3]
    # pixWidth = transform_[1]
    # pixHeight = transform_[5]
    
    # Testing rasterio geotransform
     with ras.open(os.path.join(path_,file_)) as src:
        binary_img_arr = src.read(1)
        profile = src.profile
        profile.update(dtype=ras.float32,
                       count=1)
        
        transform_ = src.transform
        x, y = ras.transform.xy(transform_, df.loc[df['frameID']==frame]['centroid_y'], df.loc[df['frameID']==frame]['centroid_x'])
    
    
    # df.at[frame,'x'] = df.loc[df['frameID']==frame]['centroid_y']*transform_[1]+transform_[0]
    # df.at[frame,'y'] = df.loc[df['frameID']==frame]['centroid_x']*transform_[5]+transform_[3]
        df.loc[df['frameID']==frame,['Date']] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        df.loc[df['frameID']==frame,['x']] = x #df.loc[df['frameID']==frame]['centroid_x']*transform_[1]+transform_[0]
        df.loc[df['frameID']==frame,['y']] = y #df.loc[df['frameID']==frame]['centroid_y']*transform_[5]+transform_[3]

        frame+=1
    
#df.to_csv(os.path.join(outPath,'test1_tracker_Icebergs.csv'))
df.to_csv(os.path.join(outPath,'Icebergs_tracker_70imgs.csv'))
    
# # Set frame ID to Sentinel-1 image using dictionary
# for i in range(4,144,1):
#     print('Frame = ',i)
    
    
    