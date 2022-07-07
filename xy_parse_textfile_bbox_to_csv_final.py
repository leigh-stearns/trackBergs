#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Converting the bounding box centroid (x,y) to georeferenced coordinates

1. Get the transform from the geotiff
2. Get the centroid row, col of the bounding box
3. x = col*transform[1]+ transform[0]
   y = row*transform[5]+ transform[3] 

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

@author: Siddharth Shankar
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
import datetime
from collections import defaultdict
import numpy as np
import skimage
from tqdm import tqdm
import geopandas as gpd
import scipy
from shapely.geometry import Point,MultiPoint,mapping
import fiona
import rasterio as ras

# *******************************************************************************************************
# =============================================================================
# # Following Leigh's csv structure
# =============================================================================

# =============================================================================
# Read text file for parsing
# =============================================================================

# User inputs
path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'

path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csv_ = 'grid_of_locations.csv'#'test1_tracker_Icebergs.csv'

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
frames_all={} # Dictionary with key=Frame,val = ['tracker1,fps,(xmin,ymin,xmax,ymax),...']
frames = {} 
frames_track = {} # Dictionary with key=Frame, val = [tracker1,tracker2,...]
frames_coords={}
for i in range(70): #number of frames in the video/txt file
    j=i+1
    if(j<70):
        frame_idx_start = lines.index('Frame #:  %s'%(j))
        frame_idx_end = lines.index('Frame #:  %s'%(j+1))
        tracker_id_list = lines[frame_idx_start+1:frame_idx_end]
    else:
        frame_idx_start = lines.index('Frame #:  %s'%(j))
        tracker_id_list = lines[frame_idx_start+1:]
    frames_all['FrameID_%s'%(j)] = tracker_id_list

for k in range(len(frames_all)): # iterate through each key
    frame_ = k+1
    tracker=[] #Create a list of only 'trackers' that exist within a frame
    coords=[]
    # Check the size of list values and iteratively tracker_id_list[0].split(',')[0]
    for values in range(len(frames_all['FrameID_%s'%(frame_)])):
        print (values)
        tracker.append(frames_all['FrameID_%s'%(frame_)][values].split(',')[0]) #(frames_all['FrameID_70'])[29].split(',')[0]
        # coords.append(frames_all['FrameID_%s'%(frame_)][values].split(': ')[-1])
    frames_track['FrameID_%s'%(frame_)] = tracker
    # frames_coords['FrameID_%s'%(frame_)] = (tracker,coords)

'''
# Find all the unique values(trackerID's) that exist within frames_track dictionary.
# This list will be the trackerID's that we are looking for tracking.
# To do this we will convert the values into a "set".
'''
# unique_trackerID = [val for frm in frames_track for val in frames_track.values()]
all_trackerID = [val for frm in frames_track for val in frames_track.values()]

all_trackerID_redundant = ([track for sublist in all_trackerID for track in sublist if 'Track' in track])
unique_trackerID = list(set(all_trackerID_redundant))


# =============================================================================
# Associate Date with FrameID as a new column
# =============================================================================


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


# =============================================================================
# Associate frameID with Dates as key,value in a dictionary
# =============================================================================
frameDate={}
for count,file_ in enumerate((tqdm(fileNames))):
    print(count)
    indx = count+1
    if(indx<=2):
        continue
    else:
        frameDate['FrameID_%s'%(indx)] = str(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))

# =============================================================================
# Add the coordinates xmin,ymin,xmax,ymax to the dataframe
# =============================================================================

df_frameDate = pd.DataFrame([frameDate])


df_list = []
for key,values in frames_all.items():
    # Remove FPS and Video text strings from the dictionary
    values_updated = ([val for val in values if "FPS:" not in val if "Video has ended or failed, try a different video format!" not in val])
    df = pd.DataFrame()
    keys=[]
    track=[]
    coords=[]
    xmin=[]
    ymin=[]
    xmax=[]
    ymax=[]
    dates=[]
    for val_up in values_updated:
        keys.append(key)
        track.append(int(val_up.split(',')[0].split(': ')[-1]))
        coords.append(val_up.split(': ')[-1].split('(')[-1].split(')')[0])
        xmin.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[0]))
        ymin.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[1]))
        xmax.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[2]))
        ymax.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[3]))
        dates.append(frameDate.get(key))
    df['frameID'] = keys
    df['date'] = dates
    df['trackerID'] = track
    df['cords'] = coords
    df['xmin'] = xmin
    df['ymin'] = ymin
    df['xmax'] = xmax
    df['ymax'] = ymax
    df_list.append(df)
    
df_all_values = pd.concat(df_list)



# =============================================================================
# Add the coordinates, dimensions, and projected coordinates
# =============================================================================
'''
Bounding Box dimension
----------------------
x = xmin
y = ymin
width =  (xmax-xmin)*10 ---> Width of bounding box in meters
height = (ymax-ymin)*10 ---> Height of bounding box in meters
centroid_bbox = {(xmax+xmin)/2 , (ymax+ymin)/2}
'''

df_all_values['width'] = (df_all_values['xmax']-df_all_values['xmin'])*10
df_all_values['height'] = (df_all_values['ymax']-df_all_values['ymin'])*10
df_all_values['centroid_x'] = (df_all_values['xmax']+df_all_values['xmin'])/2
df_all_values['centroid_y'] = (df_all_values['ymax']+df_all_values['ymin'])/2
df_all_values['Area_BBox'] = df_all_values['width']*df_all_values['height']
df_all_values['date_obj'] = pd.to_datetime(df_all_values['date'])
df_all_values['doy'] = df_all_values['date_obj'].dt.dayofyear

indx=1

for file_ in tqdm(fileNames):
    frame='FrameID_%s'%(indx)
    if indx>=3:
           
        read_sar = gdal.Open(os.path.join(path_,file_),gdal.GA_ReadOnly)
        transform_ = read_sar.GetGeoTransform()
        proj = read_sar.GetProjection()
        xOrigin = transform_[0]
        yOrigin = transform_[3]
        pixWidth = transform_[1]
        pixHeight = transform_[5]
        
        # Testing rasterio geotransform
        with ras.open(os.path.join(path_,file_)) as src:
          binary_img_arr = src.read(1)
          profile = src.profile
          profile.update(dtype=ras.float32,
                          count=1)
          
          transform_ = src.transform
          x, y = ras.transform.xy(transform_, df_all_values.loc[df_all_values['frameID']==frame]['centroid_y'], df_all_values.loc[df_all_values['frameID']==frame]['centroid_x'])
        
        
        df_all_values.loc[df_all_values['frameID']==frame,['x']] = x #df.loc[df['frameID']==frame]['centroid_x']*transform_[1]+transform_[0]
        df_all_values.loc[df_all_values['frameID']==frame,['y']] = y #df.loc[df['frameID']==frame]['centroid_y']*transform_[5]+transform_[3]

    indx+=1

# =============================================================================
# Save the dataframe to a csv
# =============================================================================

# df_all_values.to_csv(os.path.join(path_,'df_all_values.csv'))



# =============================================================================
# Plotting the trackerID/icebergs
# =============================================================================
tracker_id = 8
tracker1 = df_all_values.loc[df_all_values['trackerID']==tracker_id]
ax = tracker1.plot.scatter(x='x',y='y',c='doy',colormap='viridis')
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.grid(linestyle='dotted')
plt.title('TrackerID: %s'%(tracker_id))
plt.tight_layout()
plt.savefig(os.path.join(path_,'trackerid_%s.png'%(tracker_id)),dpi=300)
plt.show()