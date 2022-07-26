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

# =============================================================================
# NW Greenland constant icebergs
# =============================================================================
# User inputs

'''
path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'
path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_geotiffs_clip'
# outPath = r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/helheim_pngs_clip_histMatch'
outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test2_70imgs\bbox'#r'/home/s004s394_a/track_bergs/Track_Helheim_Melange_2020/coordinatesBBox'
csv_ = 'grid_of_locations.csv'#'test1_tracker_Icebergs.csv'
txt = 'results_70imgs.txt'
'''


# =============================================================================
# North Greenland test
# =============================================================================
'''
path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO'
path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO' 
outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO\bbox'
csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test4_39imgs_NO\bbox'
csv_ = 'grid_of_locations_NO.csv'
txt = 'results_39imgs.txt'
'''

# =============================================================================
# North East Greenland test
# =============================================================================
'''
path_txt = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast'
path_ = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast' 
outPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast\bbox'
csvPath = r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast\bbox'
csv_ = 'grid_of_locations_NE_1.csv'
txt = 'results_34imgs_highcontrast.txt'
'''

# =============================================================================
# Melange AGU 2021
# =============================================================================

path_txt = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip' #r'D:\trackBergs\coastal_icebergs_test\iceberg_test5_34imgs_NE_1\png\high_contrast'
path_ = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip' 
outPath = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip'
csvPath = r'D:\trackBergs\Track_Helheim_Melange_2020_testing\helheim_geotiffs_clip'
csv_ = 'grid_of_locations_sermilik_AGU21.csv'
txt = 'test1_tracker_Icebergs.txt'



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
for i in range(143): #number of frames in the video/txt file
    j=i+1
    if(j<143):
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
frameFile={}
for count,file_ in enumerate((tqdm(fileNames))):
    print(count)
    indx = count+1
    if(indx<=3 or indx==7):
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
    if (indx>=4 and indx!=7):
           
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
          print('The frame id is FrameID_%s'%(indx))
          x, y = ras.transform.xy(transform_, df_all_values.loc[df_all_values['frameID']==frame]['centroid_x'], df_all_values.loc[df_all_values['frameID']==frame]['centroid_y'])
        
        
        df_all_values.loc[df_all_values['frameID']==frame,['x']] = x #df.loc[df['frameID']==frame]['centroid_x']*transform_[1]+transform_[0]
        df_all_values.loc[df_all_values['frameID']==frame,['y']] = y #df.loc[df['frameID']==frame]['centroid_y']*transform_[5]+transform_[3]
    elif (indx==1 or indx==2 or indx==3 or indx==7):
        print('No data for frameID: %s'%(indx))
    indx+=1

# =============================================================================
# Save the dataframe to a csv
# =============================================================================

df_all_values.to_csv(os.path.join(path_,'Helheim_Melange_df_all_values_proj_sermilik_AGU21.csv'))





# =============================================================================
# PLOTS
# =============================================================================

# =============================================================================
# Plotting the trackerID/icebergs velocity/distance individually
# =============================================================================
from rasterio.plot import show
# bckgrnd_path = path_+'/background_img'
# background_img = ras.open(os.path.join(bckgrnd_path,'S1A_IW_GRDH_1SDH_20190102T113609_20190102T113634_025298_02CC75_9BA1_background_img.tif'))

all_trackers = sorted(list(set(df_all_values['trackerID'])))

vel = [] #List of all iceberg velocity dataframes i.e [tracker1, tracker2,....]
for count,tracker in enumerate(all_trackers):
    tracker_id = tracker
    tracker1 = df_all_values.loc[df_all_values['trackerID']==tracker_id]
    tracker1['diff'] = tracker1.doy.diff() # difference between successive dates for a specific trackerID
    tracker1['distance'] = ((tracker1.x.diff())**2 + (tracker1.y.diff())**2).pow(0.5)
    tracker1['velocity_mpd'] = (tracker1['distance']/tracker1['diff'])
    vel.append(tracker1)
    ax = tracker1.plot.scatter(x='x',y='y',c='velocity_mpd',colormap='viridis',sharex=False) # add figsize=(10,5) if a specific size is needed
    
    # ax.legend(['velocity (m/day)'])
    # ax.set_facecolor('beige')
    # show((background_img),ax=ax,cmap='gray')
    
    plt.grid(linestyle='dotted')
    plt.title('IcebergID: %s'%((int(tracker_id))))
    # ax.set_xticks(tracker1['x'])
    ax.set_xticklabels(df_all_values['x'],rotation=45)
    ax.set_yticklabels(df_all_values['y'])
    # plt.xlim(1,230)
    # plt.ylim(0,100)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.tight_layout()
    plt.savefig(os.path.join(path_,'velocity_trackerid_%s.png'%(tracker_id)),dpi=300)
plt.show()


# =============================================================================
# Plotting the icebergs velocity as a histogram
# =============================================================================
fig,axes = plt.subplots()

# vel_df_100_150 = vel_df.loc[(vel_df['doy']>=100) & (vel_df['doy']<=150)] 
vel_df = pd.concat(vel)
# vel_df.sum(skipna=True)/len(vel_df) #Average velocity of all icebergs in 7 months

# vel_df['velocity_mpd'].plot.hist(bins=100,ax=axes)

# Trying matplotlib histogram plot
bins,values,_ = axes.hist(vel_df['velocity_mpd'],bins=50,edgecolor='black',color='#2452F9')
print('Iceberg velocity most frequent: %s m/day'%(values[np.where(bins==bins.max())][0]))
# axes.axvspan(1,30,color='orange',alpha=0.1)
# plt.grid(linestyle='dotted')
axes.grid(linestyle='dotted')
axes.legend(['Highest frequency of iceberg velocity: %s m/day'%round((values[np.where(bins==bins.max())][0]),2),
             'n=%s'%(len(vel_df))])
# plt.title('IcebergID: %s'%((int(tracker_id))))
plt.title('Frequency distribution of iceberg velocity in melange at Helheim glacier: 2020')
plt.xticks()
# plt.xlim(1,100)
# plt.ylim(0,100)
plt.xlabel('Velocity of icebergs (m/day)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig(os.path.join(path_,'Helheim_Melange_histogram_velocity_icebergs.png'),dpi=300)
plt.show()



# =============================================================================
# Plotting the trackerID/icebergs velocity/distance together
# =============================================================================
from rasterio.plot import show
# bckgrnd_path = path_+'/background_img'
# background_img = ras.open(os.path.join(bckgrnd_path,'S1A_IW_GRDH_1SDH_20190102T113609_20190102T113634_025298_02CC75_9BA1_background_img.tif'))

fig,axes = plt.subplots(figsize=(15,10))
all_trackers = sorted(list(set(df_all_values['trackerID'])))
plt.rcParams.update({'font.size':22})

vel = []
for count,tracker in enumerate(all_trackers):
    tracker_id = tracker
    tracker1 = df_all_values.loc[df_all_values['trackerID']==tracker_id]
    tracker1['diff'] = tracker1.doy.diff() # difference between successive dates for a specific trackerID
    tracker1['distance'] = ((tracker1.x.diff())**2 + (tracker1.y.diff())**2).pow(0.5)
    tracker1['velocity_mpd'] = (tracker1['distance']/tracker1['diff'])
    vel.append(tracker1)
    # ax = tracker1.plot.scatter(x='x',y='y',c='velocity_mpd',colormap='viridis')
    # tracker1.plot.scatter(x='doy',y='velocity_mpd',ax=axes,c='#2452F9')
    # sc = axes.scatter(x=tracker1.doy,y=tracker1.velocity_mpd,c=tracker1.Area_BBox,
    #                   s=tracker1.Area_BBox/800,cmap='Blues',alpha=0.4)
    # tracker1.plot.line(x='doy',y='velocity_mpd',color='maroon',style='.-',ax=axes)
    
    # axes.axvspan(100,150,color='orange',alpha=0.1)
    # axes.legend(['IcebergID: %s'%(int(tracker_id))])
    # axes.legend(['velocity (m/day)','n=%s'])
    # axes.set_facecolor('white')

    # show((background_img,1),ax=ax,cmap='gray')

# Filter velocity between ranges
# Filter velocity between ranges
# vel_df = pd.concat(vel)
# vel_df.sum(skipna=True)/len(vel_df) #Average velocity of all icebergs in 7 months
# vel_df['velocity_mpd'].plot.hist(bins=50,ax=axes)


# vel_df_100_150 = vel_df.loc[(vel_df['doy']>=100) & (vel_df['doy']<=150)] 
vel_df = pd.concat(vel)
# vel_df.sum(skipna=True)/len(vel_df) #Average velocity of all icebergs in 7 months
sc = plt.scatter(x=vel_df.doy,y=vel_df.velocity_mpd,c=vel_df.Area_BBox/1e6,
                  s=vel_df.Area_BBox/(800),cmap='Blues',alpha=0.6)
# vel_df['velocity_mpd'].plot.hist(bins=50,ax=axes)
# axes.legend(['instances of icebergs=%s'%(len(vel_df))])
# plt.legend(*sc.legend_elements('sizes',num=7))
# axes.axvspan(1,50,color='orange',alpha=0.1)
plt.grid(linestyle='dotted')
cbar = plt.colorbar(sc,ax=axes)
cbar.set_label('Area (km$^2$)')
# plt.title('IcebergID: %s'%((int(tracker_id))))
plt.title('Iceberg velocity in melange at Helheim Glacier: 2020')
plt.xticks()
# plt.xlim(1,220)
# plt.ylim(0,100)
plt.ylabel('Velocity of icebergs (m/day)')
plt.xlabel('Day of the year')
plt.tight_layout()
plt.savefig(os.path.join(path_,'Helheim_Melange_velocity_icebergs_scatterplot_all_instances_2020.png'),dpi=300)
plt.show()











# =============================================================================
# OLD VERSION: ENABLE if needed
# =============================================================================
'''
# =============================================================================
# Plotting the trackerID/icebergs velocity/distance together
# =============================================================================
from rasterio.plot import show
# bckgrnd_path = path_+'/background_img'
# background_img = ras.open(os.path.join(bckgrnd_path,'S1A_IW_GRDH_1SDH_20190102T113609_20190102T113634_025298_02CC75_9BA1_background_img.tif'))

fig,axes = plt.subplots()
all_trackers = sorted(list(set(df_all_values['trackerID'])))

vel = []
for count,tracker in enumerate(all_trackers):
    tracker_id = tracker
    tracker1 = df_all_values.loc[df_all_values['trackerID']==tracker_id]
    tracker1['diff'] = tracker1.doy.diff() # difference between successive dates for a specific trackerID
    tracker1['distance'] = ((tracker1.x.diff())**2 + (tracker1.y.diff())**2).pow(0.5)
    tracker1['velocity_mpd'] = (tracker1['distance']/tracker1['diff'])
    vel.append(tracker1)
    # ax = tracker1.plot.scatter(x='x',y='y',c='velocity_mpd',colormap='viridis')
    tracker1.plot.scatter(x='doy',y='velocity_mpd',ax=axes,c='#2452F9')
    # tracker1.plot.line(x='doy',y='velocity_mpd',color='maroon',style='.-',ax=axes)
    
    # axes.axvspan(100,150,color='orange',alpha=0.1)
    # axes.legend(['IcebergID: %s'%(int(tracker_id))])
    # axes.legend(['velocity (m/day)','n=%s'])
    # ax.set_facecolor('beige')
    # show((background_img,1),ax=ax,cmap='gray')

# Filter velocity between ranges
# Filter velocity between ranges
# vel_df = pd.concat(vel)
# vel_df.sum(skipna=True)/len(vel_df) #Average velocity of all icebergs in 7 months
# vel_df['velocity_mpd'].plot.hist(bins=50,ax=axes)


# vel_df_100_150 = vel_df.loc[(vel_df['doy']>=100) & (vel_df['doy']<=150)] 
vel_df = pd.concat(vel)
# vel_df.sum(skipna=True)/len(vel_df) #Average velocity of all icebergs in 7 months

# vel_df['velocity_mpd'].plot.hist(bins=50,ax=axes)
axes.legend(['instances of icebergs=%s'%(len(vel_df))])
# axes.axvspan(1,50,color='orange',alpha=0.1)
plt.grid(linestyle='dotted')
# plt.title('IcebergID: %s'%((int(tracker_id))))
plt.title('Iceberg tracking velocity: Helheim Melange 2020')
plt.xticks()
# plt.xlim(1,220)
# plt.ylim(0,100)
plt.ylabel('Velocity of icebergs (m/day)')
plt.xlabel('Day of the year')
plt.tight_layout()
plt.savefig(os.path.join(path_,'velocity_icebergs_scatterplot_all_instances_HelheimMelange_2020.png'),dpi=300)
plt.show()
'''