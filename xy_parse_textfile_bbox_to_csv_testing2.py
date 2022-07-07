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
from collections import defaultdict
# # =============================================================================
# # Read text file for parsing
# # =============================================================================

# path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'
# txt = 'results_70imgs.txt'
# with open(os.path.join(path_txt,txt)) as f:
#     lines = f.readlines()

# '''
# Remove the \n from the string elements of the txt file
# '''
# for idx,line in enumerate(lines):
#     lines[idx] = line.strip()

# '''
# Create dictionary representing key-value pair of FrameID_{Number} and TrackerID
# '''
# frames_all={} # Dictionary with key=Frame,val = ['tracker1,fps,(xmin,ymin,xmax,ymax),...']
# frames = {} 
# frames_track = {} # Dictionary with key=Frame, val = [tracker1,tracker2,...]
# frames_coords={}
# for i in range(70): #number of frames in the video/txt file
#     j=i+1
#     if(j<70):
#         frame_idx_start = lines.index('Frame #:  %s'%(j))
#         frame_idx_end = lines.index('Frame #:  %s'%(j+1))
#         tracker_id_list = lines[frame_idx_start+1:frame_idx_end]
#     else:
#         frame_idx_start = lines.index('Frame #:  %s'%(j))
#         tracker_id_list = lines[frame_idx_start+1:]
#     frames_all['FrameID_%s'%(j)] = tracker_id_list

# for k in range(len(frames_all)): # iterate through each key
#     frame_ = k+1
#     tracker=[] #Create a list of only 'trackers' that exist within a frame
#     coords=[]
#     # Check the size of list values and iteratively tracker_id_list[0].split(',')[0]
#     for values in range(len(frames_all['FrameID_%s'%(frame_)])):
#         print (values)
#         tracker.append(frames_all['FrameID_%s'%(frame_)][values].split(',')[0]) #(frames_all['FrameID_70'])[29].split(',')[0]
#         # coords.append(frames_all['FrameID_%s'%(frame_)][values].split(': ')[-1])
#     frames_track['FrameID_%s'%(frame_)] = tracker
#     # frames_coords['FrameID_%s'%(frame_)] = (tracker,coords)

# df_coords = pd.DataFrame(frames_coords)
# df_coords_T = df_coords.T
# # df_coords_T.to_csv(os.path.join(path_txt,'frames_coords_transpose.csv'))

# df_0 = pd.DataFrame(df_coords_T[0])
# df_1 = pd.DataFrame(df_coords_T[1])
# df_combine = pd.concat(df_0,df_1,on='FrameID')


# result_split = [coord.split(',') for coord in df_coords_T[1].str[0]]
# # Find all the unique values(trackerID's) that exist within frames_track dictionary.
# # This list will be the trackerID's that we are looking for tracking.
# # To do this we will convert the values into a "set".

# # unique_trackerID = [val for frm in frames_track for val in frames_track.values()]
# all_trackerID = [val for frm in frames_track for val in frames_track.values()]

# all_trackerID_redundant = ([track for sublist in all_trackerID for track in sublist if 'Track' in track])
# unique_trackerID = list(set(all_trackerID_redundant))

# # =============================================================================
# # Get the list of keys (Frames) where a given value exists
# # =============================================================================

# # tracker = 'Tracker ID: 153, Class: iceberg,  BBox Coords (xmin, ymin, xmax, ymax): (515, 241, 562, 286)'
# # list_of_keys = [key for key, list_of_values in frames.items() if tracker in list_of_values]

# '''
# List all frames where a specific trackerID is present
# '''


# trackerID_frames = []
# trackerID_frames_coords = []
# for trackerID in unique_trackerID:
# # list_of_keys = [key for key, list_of_values in frames.items() if tracker in list_of_values]
#     # frame_num = [frame_ for frame_,track in frames.items() for trackID in track if trackID == 'Tracker ID: 1' ]
#     trackerID_frames.append((trackerID,[frame_ for frame_,track in frames_track.items() for trackID in track if trackID == trackerID ]))
#     # trackerID_frames_coords.append((trackerID, [val for frame_,values in frames_all.items() for val in values]))
#     # trackerID_frames_coords.append((trackerID,[(frame_,trackID[1]) for frame_,track in frames_coords.items() for trackID in track if trackID[0] == trackerID]))


# # Add the frames as columns


# list_of_frames = ['FrameID_%s'%(k+1) for k in range(len(frames_all))]
# df_final = pd.DataFrame(columns=list_of_frames)#columns=range(len(frames_all))
# # df_final.columns = list_of_frames

# #Set all the trackerID's as index
# df_final['TrackerID']=(unique_trackerID) 
# df_final = df_final.set_index('TrackerID')

# # Saving the dictionary of trackerID and Frames to a dataFrame and to a csv
# # df = pd.DataFrame(trackerID_frames,columns=['Tracker','Frames'])
# # df.to_csv(os.path.join(path_txt,'tracks_and_frames.csv'))

# '''             FrameID_1               FrameID_2               FrameID_3  . . . . .     FrameID_n
# TrackerID:1   (xmin,ymin,xmax,ymax)   (xmin,ymin,xmax,ymax)   (xmin,ymin,xmax,ymax)    (xmin,ymin,xmax,ymax)
# TrackerID:2         .                   .
# TrackerID:3         .                   .    
# .
# .
# .
# .TrackerID:n

# '''
# for count,value in enumerate(trackerID_frames): #Iterate through each trackerID
#     # print(value[0])
#     for ind in (range(len(value[1]))): #Iterate through each list of frameID
#         # print(value[1][ind])
#         df_final.at[value[0],value[1][ind]] = 1
        

# df_final.to_csv(os.path.join(path_txt,'grid_of_locations.csv'))



# '''
# Associate frameID with dates
# '''


# # User inputs
# # path_ = r'/home/s004s394_a/track_bergs/new_data_for_roboflow/test.v10i.darknet/geotiff_for_mp4/pngs'
# # path_ = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs'
# path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# # outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
# outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
# csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
# csv_ = 'grid_of_locations.csv'#'test1_tracker_Icebergs.csv'

# pattern = "*.tif" 

# out_gif = os.path.join(path_,"Sermilik_melange_2020_v3.gif")
# refer = 'S1A_IW_GRDH_1SDH_20200127T091147_20200127T091212_030984_038EE8_2DFB.png'

# print(path_)
# fileNames = []
# for _,dirs,files in os.walk(path_,topdown=True): 
#     dirs.clear() #excludes the files in subdirectories
#     for name in files:   
#         if fnmatch(name,pattern):
#             fileNames.append(name)

# fileNames.sort(key = lambda x: x.split('_')[4]) 
# print(fileNames)

# # Mapping frameID with dates
# frameDate={}
# for count,file_ in enumerate((tqdm(fileNames))):
#     print(count)
#     indx = count+1
#     frameDate['FrameID_%s'%(indx)]=(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
    
    
# # Frame dictionary
# frameDict = {}
# trackDict = {}
# Dict = {}

# df = pd.read_csv(os.path.join(outPath,csv_))
# # df = df.dropna()
# # print(df.head())                  
# df['x'] = 0
# df['y'] = 0
# df['Date'] = 0
# frame = 1
# # Associate fileNames with frames

# for count,file_ in enumerate((tqdm(fileNames))):
#     print(count)
#     indx = count+1
#     # read_sar = gdal.Open(os.path.join(path_,file_),gdal.GA_ReadOnly)
#     # transform_ = read_sar.GetGeoTransform()
#     # proj = read_sar.GetProjection()
#     # xOrigin = transform_[0]
#     # yOrigin = transform_[3]
#     # pixWidth = transform_[1]
#     # pixHeight = transform_[5]
    
#     # Testing rasterio geotransform
#     with ras.open(os.path.join(path_,file_)) as src:
#         binary_img_arr = src.read(1)
#         profile = src.profile
#         profile.update(dtype=ras.float32,count=1)
   
#         transform_ = src.transform
#         # x, y = ras.transform.xy(transform_, df.loc[df['frameID']==frame]['centroid_y'], df.loc[df['frameID']==frame]['centroid_x'])
   

# # df.at[frame,'x'] = df.loc[df['frameID']==frame]['centroid_y']*transform_[1]+transform_[0]
# # df.at[frame,'y'] = df.loc[df['frameID']==frame]['centroid_x']*transform_[5]+transform_[3]
#         df.loc[df['FrameID_%s'%(indx)]==1] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
#         # df.loc[df['frameID']==frame,['x']] = x #df.loc[df['frameID']==frame]['centroid_x']*transform_[1]+transform_[0]
#         # df.loc[df['frameID']==frame,['y']] = y #df.loc[df['frameID']==frame]['centroid_y']*transform_[5]+transform_[3]

#         frame+=1










# df_test = pd.DataFrame(columns=['FrameID','Date','TrackerID'])
# df_test['FrameID'] = frameDate.keys()
# df_test['Date'] = frameDate.values()
# df_test['TrackerID'] = frames_track.values()
# # df_test['Coords'] = df_coords_T[1]
# # df_final.at[value[0],value[1][ind]] = 1



# *******************************************************************************************************
# =============================================================================
# # Following Leigh's csv
# =============================================================================


# =============================================================================
# Read text file for parsing
# =============================================================================

path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'
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

# Find all the unique values(trackerID's) that exist within frames_track dictionary.
# This list will be the trackerID's that we are looking for tracking.
# To do this we will convert the values into a "set".

# unique_trackerID = [val for frm in frames_track for val in frames_track.values()]
all_trackerID = [val for frm in frames_track for val in frames_track.values()]

all_trackerID_redundant = ([track for sublist in all_trackerID for track in sublist if 'Track' in track])
unique_trackerID = list(set(all_trackerID_redundant))


'''
List all frames where a specific trackerID is present
'''

df_all = pd.DataFrame()
df_list = []
trackerID_frames = []
trackerID_frames_coords = []
for trackerID in unique_trackerID:
    df_each = pd.DataFrame()
# list_of_keys = [key for key, list_of_values in frames.items() if tracker in list_of_values]
    # frame_num = [frame_ for frame_,track in frames.items() for trackID in track if trackID == 'Tracker ID: 1' ]
    # trackerID_frames.append((trackerID,[frame_ for frame_,track in frames_track.items() for trackID in track if trackID == trackerID ]))
    df_each['frameID'] = [frame_ for frame_,track in frames_track.items() for trackID in track if trackID == trackerID ]
    df_each['trackerID'] = trackerID.split(': ')[-1]#trackerID
    df_list.append(df_each)

    # df_all['FrameID'] = 
    # trackerID_frames_coords.append((trackerID, [val for frame_,values in frames_all.items() for val in values]))
    # trackerID_frames_coords.append((trackerID,[(frame_,trackID[1]) for frame_,track in frames_coords.items() for trackID in track if trackID[0] == trackerID]))

df_all = pd.concat(df_list)


# =============================================================================
# Associate Date with FrameID as a new column
# =============================================================================

'''
Associate frameID with dates
'''


# User inputs
path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csv_ = 'grid_of_locations.csv'#'test1_tracker_Icebergs.csv'

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

# Mapping frameID with dates
frameDate={}
for count,file_ in enumerate((tqdm(fileNames))):
    print(count)
    indx = count+1
    if(indx<=2):
        continue
        # frameDate['FrameID_%s'%(indx)]=(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_all.loc[df_all.index['FrameID_%s'%(indx)],'Date'] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_all.loc[df_all['FrameID_%s'%(indx)],"Date"] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
    else:
        df_all.loc[df_all['frameID']=='FrameID_%s'%(indx),'Date'] = str(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_all.loc[(df_all['frameID'].eq('FrameID_%s'%(indx))) & (df_all['trackerID'].eq([val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][indx].split(',')[0].split(': ')[-1])),'Coords'] = [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][indx].split(': ')[-1]

        # df_all['Date'] = df_all['frameID'].map({'FrameID_%s'%(indx):(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))}) 


# =============================================================================
# Associate frameID with Dates as key,value in a dictionary
# =============================================================================
frameDate={}
for count,file_ in enumerate((tqdm(fileNames))):
    print(count)
    indx = count+1
    if(indx<=2):
        continue
        # frameDate['FrameID_%s'%(indx)]=(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_all.loc[df_all.index['FrameID_%s'%(indx)],'Date'] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_all.loc[df_all['FrameID_%s'%(indx)],"Date"] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
    else:
        frameDate['FrameID_%s'%(indx)] = str(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))

# =============================================================================
# Add the coordinates xmin,ymin,xmax,ymax to the dataframe
# =============================================================================

df_frameDate = pd.DataFrame([frameDate])


# for trackerID in unique_trackerID:
    
# [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][0].split(',')[0].split(': ')[-1]
# df_all.loc[df_all['trackerID']=='FrameID_%s'%(indx),'Coords'] = [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val]
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
        # df['frameID'] = (key)
        # df['trackerID'] = val_up.split(',')[0].split(': ')[-1]
        # df['coords'] = val_up.split(': ')[-1].split('(')[-1].split(')')[0]
        # df['xmin'] = val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[0]
        # df['ymin'] = val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[1]
        # df['xmax'] = val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[2]
        # df['ymax'] = val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[3]
        keys.append(key)
        track.append(int(val_up.split(',')[0].split(': ')[-1]))
        coords.append(val_up.split(': ')[-1].split('(')[-1].split(')')[0])
        xmin.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[0]))
        ymin.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[1]))
        xmax.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[2]))
        ymax.append(float(val_up.split(': ')[-1].split('(')[-1].split(')')[0].split(',')[3]))
        dates.append(frameDate.get(key))
        # df.loc[df['frameID']==key,'date'] = df_frameDate[key][0] #str(dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
        # df_list.append(df)        
        # print(val)
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


# for count,frame in enumerate(frames_all):
#     index = count+1
#     if(index<=2):
#         continue
#     # conditions = df_all['frameID'].eq(frame) & df_all['trackerID'].eq([val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(',')[0].split(': ')[-1]) 
    
#     # df_all['Coords'] = np.where((df_all['frameID'].eq(frame)) & (df_all['trackerID'].eq([val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(',')[0].split(': ')[-1])), [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(': ')[-1],0)

#     # df_all.loc[(df_all['frameID'].eq(frame)) & (df_all['trackerID'].eq([val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(',')[0].split(': ')[-1])),'Coords'] = [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(': ')[-1]
#     df_all.at[(df_all['frameID'].eq(frame)), (df_all['trackerID'].eq([val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(',')[0].split(': ')[-1])),'Coords'] = [val for frame_,values in frames_all.items() for val in values if "FPS:" not in val][index].split(': ')[-1]















# '''
# List all locations (xmin,ymin,xmax,ymax) where a specific trackerID is present
# '''
# # all_coordsID = [val for frm in frames_coords for val in frames_coords.values()]

# # combined_dictionaries = [frames_track,frames_coords]
# # combined_dict = defaultdict(combined_dictionaries)

# common_keys = [key for key in frames_track.keys()]
# combined_dictionaries = {k: (frames_coords[k]) for k in common_keys}


# # Create a tuple with key=FrameID, and value = (trackerID,coordinates)
# frame_track_coord = {}
# for frame in combined_dictionaries:
#     frame_track_coord[frame] = tuple(zip(combined_dictionaries.get(frame)[0],combined_dictionaries.get('FrameID_70')[1]))
    

# # Saving the dictionary of frame with trackerID and coordinates to a csv
# '''
# INCORRECT FRAMEID AND TRACKERID ASSOCIATION
# '''
# df_frame = (pd.DataFrame(frame_track_coord)).T
# df_frame.to_csv(os.path.join(path_txt,'frames_tracker_coords_transpose.csv'))



 
# for trackerID in unique_trackerID:
#     trackerID_frames_coords.append((trackerID,[frame_ for frame_,track in combined_dictionaries.items() for trackID in track if trackID==trackerID]))
    



# # Create multiple dictionary with key = trackerID, and coordinates as values.
# # Then merge all the dictionaries with key = trackerID and value as a list of coordinates.






# # fig,ax = plt.subplots()
# # for tr in trackerID_frames:
# #     plt.bar(tr[0],tr[1],ax=ax)
# # plt.show()















# for f in range(len(frames)):
#     frame=f+1
#     # frames['FrameID_%s'%(frame)]
    
#     df_txt = pd.DataFrame(columns=['frameID','trackerID','xmin','ymin','xmax','ymax','width','height'])

#     df_txt['frameID'] = frame
#     df_txt['trackerID'] = frames['FrameID_%s'%(frame)]



# images = []

# # User inputs
# # path_ = r'/home/s004s394_a/track_bergs/new_data_for_roboflow/test.v10i.darknet/geotiff_for_mp4/pngs'
# # path_ = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs'
# path_ = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# # outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
# outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
# csvPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
# csv_ = 'test1_tracker_Icebergs.csv'

# pattern = "*.tif" 

# out_gif = os.path.join(path_,"Sermilik_melange_2020_v3.gif")
# refer = 'S1A_IW_GRDH_1SDH_20200127T091147_20200127T091212_030984_038EE8_2DFB.png'

# print(path_)
# fileNames = []
# for _,dirs,files in os.walk(path_,topdown=True): 
#     dirs.clear() #excludes the files in subdirectories
#     for name in files:   
#         if fnmatch(name,pattern):
#             fileNames.append(name)

# fileNames.sort(key = lambda x: x.split('_')[4]) 
# print(fileNames)

# # Frame dictionary
# frameDict = {}
# trackDict = {}
# Dict = {}

# df = pd.read_csv(os.path.join(outPath,csv_))
# # df = df.dropna()
# # print(df.head())                  
# df['x'] = 0
# df['y'] = 0
# df['Date'] = 0
# frame = 1
# # Associate fileNames with frames

# for file_ in tqdm(fileNames):

#     # read_sar = gdal.Open(os.path.join(path_,file_),gdal.GA_ReadOnly)
#     # transform_ = read_sar.GetGeoTransform()
#     # proj = read_sar.GetProjection()
#     # xOrigin = transform_[0]
#     # yOrigin = transform_[3]
#     # pixWidth = transform_[1]
#     # pixHeight = transform_[5]
    
#     # Testing rasterio geotransform
#      with ras.open(os.path.join(path_,file_)) as src:
#         binary_img_arr = src.read(1)
#         profile = src.profile
#         profile.update(dtype=ras.float32,
#                        count=1)
        
#         transform_ = src.transform
#         x, y = ras.transform.xy(transform_, df.loc[df['frameID']==frame]['centroid_y'], df.loc[df['frameID']==frame]['centroid_x'])
    
    
#     # df.at[frame,'x'] = df.loc[df['frameID']==frame]['centroid_y']*transform_[1]+transform_[0]
#     # df.at[frame,'y'] = df.loc[df['frameID']==frame]['centroid_x']*transform_[5]+transform_[3]
#         df.loc[df['frameID']==frame,['Date']] = (dt.strptime((file_.split('_')[4:5])[0].rpartition('T')[0],'%Y%m%d').strftime('%Y-%m-%d'))
#         df.loc[df['frameID']==frame,['x']] = x #df.loc[df['frameID']==frame]['centroid_x']*transform_[1]+transform_[0]
#         df.loc[df['frameID']==frame,['y']] = y #df.loc[df['frameID']==frame]['centroid_y']*transform_[5]+transform_[3]

#         frame+=1
    
# #df.to_csv(os.path.join(outPath,'test1_tracker_Icebergs.csv'))
# df.to_csv(os.path.join(outPath,'Icebergs_tracker_70imgs.csv'))
    
# # # Set frame ID to Sentinel-1 image using dictionary
# # for i in range(4,144,1):
# #     print('Frame = ',i)
    
    
    