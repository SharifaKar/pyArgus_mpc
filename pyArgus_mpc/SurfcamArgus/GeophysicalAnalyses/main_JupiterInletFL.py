#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 16:22:02 2020

@author: matthewconlin

Top level script file for examing intertidal bathymetry from a surfcam at Jupiter Inlet, FL.

Code: Matthew Conlin, University of Florida
10/2020
"""

# Standard library imports #
import datetime
from IPython import get_ipython
import math
import os

# Third-party imports #
import cv2
from matplotlib import colorbar, colors, image as mpimg, dates as mdates, patches, pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import pandas as pd
import pickle
from scipy.interpolate import interp1d,griddata
from scipy.io import loadmat
from sklearn.linear_model import LinearRegression

# Project imports #
from pyArgus_mpc import computation as comp, shorelineMapping as sl, utils
from pyArgus_mpc.SurfcamArgus import analysisTools as sca
from pyArgus_mpc.SurfcamArgus.GeophysicalAnalyses import vidPrep




#=============================================================================#
# Establish things we need later #
#=============================================================================#
direc = '/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/RawVideo/' # Directory to save things to #

rectif_xmin = -200
rectif_xmax = 200
rectif_dx = .2
rectif_ymin = 250
rectif_ymax = 900
rectif_dy = .2

wlobj = utils.NOAAWaterLevelRecord(8722670,'20200301','20200401') # Water level observations from closest station #
wl = wlobj.get()

waveobj = utils.NDBCWaveRecord(41113,2020) # Wave observstions from losest buoy #
waves = waveobj.download()

# Interp through NaNs #
for i in waves.columns[5:8]:
    A = waves[i]
    
    ok = -np.isnan(A)
    xp = ok.ravel().nonzero()[0]
    fp = A[-np.isnan(A)]
    x  = np.isnan(A).ravel().nonzero()[0]
    A[np.isnan(A)] = np.interp(x, xp, fp)
    
    waves[i] = A



#=============================================================================#
# 1. Calibrate the camera using SurfRCaT
    
#=============================================================================#
# Refer to the SurfRCaT github repo and SoftwareX publication for details. This will
# result in a calibVals file which contains the solved-for calibration parameters.
# I will load this in below #
calibVals = np.loadtxt('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Results_SurfRCaT/Test3_Jup_calibVals2.txt') # Get these by using SurfRCaT #

# Make a figure of the remote-GCPs used to complete the SurfRCaT calibration #
im = mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Extrinsic/GCP_01.png')
f = open('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Results_SurfRCaT/gcps_im.pkl','rb'); gcps_im = pickle.load(f)

fig = plt.figure(figsize=(4,3))
ax1 = plt.axes([.05,.58,.9,.37])
ax2 = plt.axes([.02,.26,.3,.25])
ax3 = plt.axes([.34,.26,.3,.25])
ax4 = plt.axes([.66,.26,.3,.25])
ax5 = plt.axes([.02,.05,.3,.3])
ax6 = plt.axes([.34,.05,.3,.3])
ax7 = plt.axes([.66,.05,.3,.3])

ax1.text(0.02, 0.97, 'a', transform=ax1.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax2.text(0.02, 0.97, 'b1', transform=ax2.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax3.text(0.02, 0.97, 'c1', transform=ax3.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax4.text(0.02, 0.97, 'd1', transform=ax4.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax5.text(0.02, 0.94, 'b2', transform=ax5.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax6.text(0.02, 0.97, 'c2', transform=ax6.transAxes,fontsize=8, fontweight='bold', va='top',color='w')
ax7.text(0.02, 0.97, 'd2', transform=ax7.transAxes,fontsize=8, fontweight='bold', va='top',color='w')

ax1.imshow(im)
ax1.set_xticks([])
ax1.set_yticks([])
for p in gcps_im:
    ax1.plot(p[0][0],p[0][1],'r+',markersize=6)
rect1 = patches.Rectangle((230,500),340,-200,edgecolor='k',facecolor='none',linewidth=1,linestyle='--')
rect2 = patches.Rectangle((1350,550),200,-100,edgecolor='k',facecolor='none',linewidth=1,linestyle='--')
rect3 = patches.Rectangle((1450,650),200,-100,edgecolor='k',facecolor='none',linewidth=1,linestyle='--')
con1 = patches.ConnectionPatch(xyA=(230,500),xyB=(400,350),coordsA="data",coordsB="data",axesA=ax1,axesB=ax2,color='k')
con2 = patches.ConnectionPatch(xyA=(1350,550),xyB=(1450,450),coordsA="data",coordsB="data",axesA=ax1,axesB=ax3,color='k')
con3 = patches.ConnectionPatch(xyA=(1650,650),xyB=(1550,550),coordsA="data",coordsB="data",axesA=ax1,axesB=ax4,color='k')
con1_1 = patches.ConnectionPatch(xyA=(400,480),xyB=(609,400),coordsA="data",coordsB="data",axesA=ax2,axesB=ax5,color='k')
con2_1 = patches.ConnectionPatch(xyA=(1450,550),xyB=(609,400),coordsA="data",coordsB="data",axesA=ax3,axesB=ax6,color='k')
con3_1 = patches.ConnectionPatch(xyA=(1550,650),xyB=(609,400),coordsA="data",coordsB="data",axesA=ax4,axesB=ax7,color='k')

ax1.add_patch(rect1)
ax1.add_patch(rect2)
ax1.add_patch(rect3)
ax1.add_artist(con1)
ax1.add_artist(con2)
ax1.add_artist(con3)

ax2.imshow(im)
ax2.set_xticks([])
ax2.set_yticks([])
for p in gcps_im:
    ax2.plot(p[0][0],p[0][1],'r+',markersize=10)
ax2.set_xlim(280,520)
ax2.set_ylim(480,350)
ax2.add_artist(con1_1)

ax3.imshow(im)
ax3.set_xticks([])
ax3.set_yticks([])
for p in gcps_im:
    ax3.plot(p[0][0],p[0][1],'r+',markersize=10)
ax3.set_xlim(1350,1550)
ax3.set_ylim(550,450)
ax3.add_artist(con2_1)

ax4.imshow(im)
ax4.set_xticks([])
ax4.set_yticks([])
for p in gcps_im:
    ax4.plot(p[0][0],p[0][1],'r+',markersize=10)
ax4.set_xlim(1450,1650)
ax4.set_ylim(650,550)
ax4.add_artist(con3_1)

ax5.imshow(mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Results_SurfRCaT/GCPs_lidar_ex_1.png'))
ax5.set_xticks([])
ax5.set_yticks([])
ax5.set_ylim(500,0)
ax5.plot(614.59,171.591249,'k+')
ax5.plot(408.0375,344.648749,'k+')
ax5.plot(876.9675,394.891249,'k+')

ax6.imshow(mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Results_SurfRCaT/GCPs_lidar_ex_2.png'))
ax6.set_xticks([])
ax6.set_yticks([])
ax6.set_ylim(700,0)
ax6.plot(732.736,414.351,'k+')

ax7.imshow(mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Results_SurfRCaT/GCPs_lidar_ex_3.png'))
ax7.set_xticks([])
ax7.set_yticks([])
ax7.set_ylim(700,0)
ax7.plot(517.149,466.725,'k+')




#=============================================================================#
# 2. Calculate and visualize the accuracy of the calibration by calculating checkpoint reprojection residuals

#=============================================================================#
# Calculate the residuals #
gcpFile = '/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Extrinsic/gcpLocs.txt'
gcpxy = loadmat('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Extrinsic/allUV.mat')['UV']
checks = np.arange(1,39)
camLoc = (592268.60,2979958.33)
resids,rmsResid,gcpXYreproj = comp.calcCheckPointResid(calibVals,gcpxy,gcpFile,checks,camLoc)

# Make a figure showing the residuals on a rectified image #
im = mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/Extrinsic/GCP_01.png')
im_rectif,extents = comp.RectifyImage(calibVals,im,[rectif_xmin,rectif_xmax,rectif_dx,rectif_ymin,rectif_ymax,rectif_dy,0])

scale_r = np.linspace(1,.5,11)
scale_g = np.linspace(1,0,11)
scale_b = np.linspace(1,0,11)
carr = np.transpose(np.vstack([scale_r,scale_g,scale_b]))
clist = [tuple(i) for i in carr]
cm = colors.ListedColormap(clist)
plt.rcParams.update({'font.size': 8})
fig = plt.figure(figsize=(2.74,3.5))
ax1 = plt.axes([.2,.1,.6,.85])
cbax = plt.axes([.78,.1,.04,.85]) 
ax2 = plt.axes([.41,.64,.34,.31])
ax2.set_xticks([])
ax2.set_yticks([])
ax3 = plt.axes([.5,.68,.24,.25])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.set_xticks([])
ax1.imshow(im_rectif,extent=extents)
for i in range(0,len(gcpXYreproj)):
    r = np.floor(resids[i])
    if r>10:
        ci=10
    else:
        ci=int(r)
    ax1.plot(gcpXYreproj[i][1]-592268.6,gcpXYreproj[i][2]-2979958.33,'o',markeredgecolor='k',markerfacecolor=clist[ci])
cb1=colorbar.ColorbarBase(cbax,cmap=cm,boundaries=[0,1,2,3,4,5,6,7,8,9,10,11],ticks=[0,1,2,3,4,5,6,7,8,9,10],spacing='proportional',orientation='vertical',label='Reprojection residual (m)')
ax1.set_xlabel('Relative Easting (m)',fontsize=8)
ax1.set_ylabel('Relative Northing (m)',fontsize=8)
ax1.set_xticks([-200,-100,0,100])
ax3.boxplot(resids,sym='kx')
ax3.set_xticks([])
ax3.set_ylim(0,20)
ax3.set_yticks([0,5,10,15,20])
ax3.set_xlim(0.85,1.15)



#=============================================================================#
# 3. Perform the intertidal bathymetry mapping analysis

#=============================================================================#

#======================================================#
# 3.1. Get the Jupiter video path list and the dictionary of video dates/times
#======================================================#
links,pthList = vidPrep.prep_JupiterInletFL()
            

#======================================================#
# 3.2. Train the machine learning view-separation
#======================================================#
# Once you run the below two lines, you can save dataAr_filled and relod it on future runs #
f = open('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/RawVideo/dataAr.pkl','rb')
dataAr = pickle.load(f)
######

ml = sca.PTZViewSepML(vidList=pthList,percentTraining=60,viewWant=1,existingDataAr=dataAr) # Create the machine learning object #
clf,dataAr_filled,accuracy,numObs,numMissed,numFalse = ml.train() # Train the classifier #


#=====================================================#
# 3.3. For each video: apply the ml to separate frames and create a timex of the desired view. 
# This part takes a few minutes for every video. Can skip this step if you already have timexs made. #
#=====================================================#
for key in links:
    ar = links[key]
    for i in range(8,len(ar)):
        try: # If the video exists this try statement will throw an exception #
            np.isnan(ar[i])
        except:
            ID = ar[i].split('/')[5]
            
            # Make the correct filename by getting the date and time of this video #

            if i<10:
                dumhr = '0'
            else:
                dumhr =''
                
            fname = 'JupiterCam_'+key.replace('-','')+dumhr+str(i)+'00'
            vid = direc+fname+'_reduced.avi'
            
            
            if not os.path.exists(direc+'timexs/Jupiter_timex_'+fname.split('_')[1]+'.png'):
                if len(links[key][i]) > 3:
                
                    # Extract the proper frames by applying the ml #
                    get_ipython().run_line_magic('matplotlib','inline')
                    framesUse = ml.apply(vid)
                    
                    # Make the timex using the proper frames #
                    timex = sca.CreatePTZImageProduct(vid,framesUse,1)
        
                    timex_towrite = np.stack([timex[:,:,2]*255,timex[:,:,1]*255,timex[:,:,0]*255],axis=2)
                    cv2.imwrite(direc+'timexs/Jupiter_timex_'+fname.split('_')[1]+'.png',timex_towrite) 
        else:
            pass
                


#=============================================================#
# 3.4. ID each shoreline with SLIM and assign elevations
#=============================================================#                
slims = {}
timexs = [i for i in os.listdir(direc+'timexs') if 'timex' in i]   
transects = None
for im in timexs:
    
    im = direc+'timexs/'+im
    timex = mpimg.imread(im)
                         
    # Rectify the timex #
    z_rectif = wlobj.atTime(wl,im.split('_')[2].split('.')[0]) # Get the observed water level fromt the closest station at the top of the hour #
    im_rectif,extents = comp.RectifyImage(calibVals,timex,[rectif_xmin,rectif_xmax,rectif_dx,rectif_ymin,rectif_ymax,rectif_dy,z_rectif])

    # Identify the shoreline on the timex with the SLIM technique #
    get_ipython().run_line_magic('matplotlib','qt5')
    try:
        if not transects:
            slim,transects = sl.mapShorelineSLIM(im_rectif,[rectif_xmin,rectif_xmax,rectif_dx,rectif_ymin,rectif_ymax,rectif_dy,z_rectif])
        else:
            slim,tt = sl.mapShorelineSLIM(im_rectif,[rectif_xmin,rectif_xmax,rectif_dx,rectif_ymin,rectif_ymax,rectif_dy,z_rectif],transects)
    except: 
        pass
    else:
        get_ipython().run_line_magic('matplotlib','qt')

         # Optional figure creation to view the shoreline #     
#        fig = plt.figure()
#        ax = fig.add_subplot(111)
#        plt.imshow(im_rectif,extent=extents,interpolation='bilinear')
#        plt.axis('equal')
#        plt.ylim(250,600)
#        for ii in slim:
#            plt.plot(ii[0],ii[1],'r.')
#        plt.show()
#        plt.draw()
#        plt.pause(.01)
#        plt.savefig('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/RawVideo/timexs/Jupiter_shoreline_'+im.split('_')[2].split('.')[0]+'.png')
 
        # Get the elevation of the SLIM shoreline #
        Hs = waveobj.atTime(waves,im.split('_')[2].split('.')[0],1)
        Td = waveobj.atTime(waves,im.split('_')[2].split('.')[0],2)
        Hrms = .7*Hs # Use this based on old studies presented on pg. 144 of Komar textbook. 
        d = 9.8 # Depth of wave buoy #
        A = 0.15 # controls curvature of beach profile. Asusming this based on assumed grain size.
        beta = 0.14 # measured this but also verified that it conforms with my assumed grain size.
        k = -0.48 # constant for the swash component of the Zsl calculation. See Plant et al. (2007, JCR) #
        gamma = 0.8 # depth-limited breaking criterion. This is the value used in the original Bettjes paper #
        
        Z_sl_comps = utils.ShorelineElevation(z_rectif,Hs,Hrms,d,Td,A,beta,k,gamma)
        Z_sl = Z_sl_comps[2]
        
        # Save everything #
        slim_a = np.empty([0,2])
        for i in slim:
            slim_a = np.vstack([slim_a,i])
        slims[im.split('_')[2].split('.')[0]] = [slim_a,Z_sl]
 

#=====================================================#
# 3.5. Manually check and remove bad SLIM estimates with interactive point clicking. #
#=====================================================#
for im in timexs:
    
    im = direc+'timexs/'+im
    timex = mpimg.imread(im)
    z_rectif = wlobj.atTime(wl,im.split('_')[2].split('.')[0])
    im_rectif,extents = comp.RectifyImage(calibVals,timex,[rectif_xmin,rectif_xmax,rectif_dx,rectif_ymin,rectif_ymax,rectif_dy,z_rectif])
    
    try:      
        slim = slims[im.split('_')[2].split('.')[0]][0]
    except:
        pass
    else: # Interactive clicking to remove points #
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(im_rectif,extent=extents,interpolation='bilinear')
        plt.axis('equal')
        plt.ylim(250,600)
        for ii in slim:
            plt.plot(ii[0],ii[1],'r.')
        plt.show()
        plt.draw()
        plt.pause(.02)
        ui = input('Want to select points to remove (y or n)?')
        while ui=='y':
            point = plt.ginput(1)
            d = np.sqrt((slim[:,0]-point[0][0])**2 + (slim[:,1]-point[0][1])**2)
            iRemove = np.where(d==np.nanmin(d))
            slim[int(iRemove[0])][0] = np.nan
            slim[int(iRemove[0])][1] = np.nan
            ui = input('Want to select points to remove (y or n)?')
        plt.close()
            
            
     
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(im_rectif,extent=extents,interpolation='bilinear')
        plt.axis('equal')
        plt.ylim(250,600)
        for ii in slim:
            plt.plot(ii[0],ii[1],'r.')
        plt.show()
        plt.draw()
        plt.pause(.01)
#        plt.savefig('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/RawVideo/timexs/Jupiter_shoreline_'+im.split('_')[2].split('.')[0]+'_cleaned.png')
        plt.close()
       
        slims[im.split('_')[2].split('.')[0]][0] = slim
        
        
        
#=========================================#
# 3.6. Make maps and do analyses #
#=========================================#

## Load in the slims variable ##        
cmat07x = np.empty([250,0]); cmat14x = np.empty([250,0]);
cmat07y = np.empty([250,0]); cmat14y = np.empty([250,0]);
cmat07z = np.empty([250,0]); cmat14z = np.empty([250,0]);
for key in slims.keys():
    if '07' in key:
        cmatUse_x = eval('cmat07x')
        cmatUse_y = eval('cmat07y')
        cmatUse_z = eval('cmat07z')       
    else:
        cmatUse_x = eval('cmat14x')
        cmatUse_y = eval('cmat14y')
        cmatUse_z = eval('cmat14z')
        
    z = slims[key][1]
    
    # Limit to 300-450 m y #        
    c = slims[key][0]
    c = c[c[:,1]>=300,:];c = c[c[:,1]<=550,:]
    
    # Interp to 1 m longshore spacing #
    yi = np.arange(300,550,1)
    f = interp1d(c[:,1],c[:,0],bounds_error=False)
    xi = f(yi)
    
    cmatUse_x = np.hstack([cmatUse_x,np.reshape(xi,[len(xi),1])])
    cmatUse_y = np.hstack([cmatUse_y,np.reshape(yi,[len(yi),1])])
    cmatUse_z = np.hstack([cmatUse_z,np.zeros([len(xi),1])+z])
    
    if '07' in key:
        cmat07x = cmatUse_x
        cmat07y = cmatUse_y
        cmat07z = cmatUse_z
    else:
        cmat14x = cmatUse_x
        cmat14y = cmatUse_y
        cmat14z = cmatUse_z  



s07 = np.argsort(cmat07z[0,:])  
s14 = np.argsort(cmat14z[0,:])    

x07,y07 = comp.calcxy(calibVals,cmat07x[:,s07],cmat07y[:,s07],cmat07z[:,s07])
x14,y14 = comp.calcxy(calibVals,cmat14x[:,s14],cmat14y[:,s14],cmat14z[:,s14])


# Calculate slope and contour change along transects #
yt = []
for T in transects:
    yt.append(np.mean([T[0][1],T[1][1]]))

beta07 = []; beta14 = []
c07 = np.empty([0,3]); c14 = np.empty([0,3])
for T in transects:
    xx = np.linspace(T[0][0],T[1][0],500)
    yy = np.linspace(T[0][1],T[1][1],500)
    adist = np.hstack([0,np.cumsum(np.sqrt(np.diff(xx)**2+np.diff(yy)**2))])
    
    zt07 = griddata((cmat07x[:,s07].flatten()[np.isnan(cmat07x[:,s07].flatten())==0],cmat07y[:,s07].flatten()[np.isnan(cmat07x[:,s07].flatten())==0]),cmat07z[:,s07].flatten()[np.isnan(cmat07x[:,s07].flatten())==0],(xx,yy))
    zt14 = griddata((cmat14x[:,s14].flatten()[np.isnan(cmat14x[:,s14].flatten())==0],cmat14y[:,s14].flatten()[np.isnan(cmat14x[:,s14].flatten())==0]),cmat14z[:,s14].flatten()[np.isnan(cmat14x[:,s14].flatten())==0],(xx,yy))

    # Slope change #
    for i in ['zt07','zt14']:
        zz = eval(i)
        reg = LinearRegression()
        try:
            reg.fit(adist[np.isnan(zz)==0].reshape(-1,1),zz[np.isnan(zz)==0].reshape(-1,1))
        except ValueError:
            slope = np.nan
        else:
            slope = abs(float(reg.coef_))
        
        if i=='zt07':
            beta07.append(slope)
        else:
            beta14.append(slope)

    # Contour change #
    c07_1 = np.empty([0,0]); c14_1 = np.empty([0,0])
    for c in [-.75,-.5,0]:
        for i in ['zt07','zt14']:
            zz = eval(i)
            iU = np.where(abs(zz-c)<=0.25)[0]
            if len(iU)>0:
                xti = np.linspace(min(adist[iU]),max(adist[iU]),1000)
                zzi = np.linspace(min(zz[iU]),max(zz[iU]),1000)
                loc = float(xti[np.where(abs(zzi-c) == min(abs(zzi-c)))[0]])
                
                if min(abs(zzi--0.5))>1:
                    loc = np.nan
            else:
                loc = np.nan
                

                
            if i=='zt07':
                c07_1 = np.append(c07_1,loc)
            else:
                c14_1 = np.append(c14_1,loc)
        
    c07 = np.vstack([c07,np.reshape(c07_1,[1,3])])
    c14 = np.vstack([c14,np.reshape(c14_1,[1,3])])


     
# Make a big summary plot #
im07 = mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/IBM_1_20200814/frame_20200307.png')
im14 = mpimg.imread('/Users/matthewconlin/Documents/Research/WebCAT/Applications/Jupiter/IBM_1_20200814/frame_20200314.png')

plt.rcParams.update({'font.size': 8})
fig = plt.figure(figsize=(6.5,3.5))
ax1 = plt.axes([.05,.55,.45,.4])
ax2 = plt.axes([.05,.05,.45,.4])
ax3 = plt.axes([.55,.15,.16,.8])
ax4 = plt.axes([.8,.15,.16,.8],sharey=ax3)
cbax = plt.axes([.40,.1,.02,.10])
ax1.text(0.02, 0.97, 'a', transform=ax1.transAxes,fontsize=8, fontweight='bold', va='top')
ax2.text(0.02, 0.97, 'b', transform=ax2.transAxes,fontsize=8, fontweight='bold', va='top')
ax3.text(0.02, 0.98, 'c', transform=ax3.transAxes,fontsize=8, fontweight='bold', va='top')
ax4.text(0.02, 0.98, 'd', transform=ax4.transAxes,fontsize=8, fontweight='bold', va='top')
ax1.set_xticks([]);ax1.set_yticks([])
ax2.set_xticks([]);ax2.set_yticks([])

ax1.imshow(im07)
c = ax1.scatter(x07,y07,3,cmat07z[:,s07],marker='x',vmin=-1,vmax=0,cmap='summer')
ax1.set_xlim(200,1500)
ax1.set_ylim(450,1080);ax1.invert_yaxis()
ax2.imshow(im14)
ax2.scatter(x14,y14,3,cmat14z[:,s14],vmin=-1,vmax=0,cmap='summer')
ax2.set_xlim(200,1500)
ax2.set_ylim(450,1080);ax2.invert_yaxis()
ax1.text(250,1025,'2020-03-07',backgroundcolor='k',c='w',fontweight='bold')
ax2.text(250,1025,'2020-03-14',backgroundcolor='k',c='w',fontweight='bold')
cb = plt.colorbar(c,ticks=[-1,0],orientation='vertical',cax=cbax)
cb.ax.tick_params(labelsize=7)
cb.ax.set_title('Elev (m)',fontsize=7)

ax3.plot(np.zeros([100,1]),np.linspace(200,600,100),'k--')
ax3.plot(np.subtract(beta14,beta07),yt,'b',linewidth=2)
ax3.set_xlim(-.04,.04)
ax3.set_xticks([-.03,0,.03])
ax3.set_ylim(300,555)
ax3.set_xlabel('Slope change',fontsize=8)

H = []
for i in range(0,3):
    H.append(ax4.plot(c14[:,i]-c07[:,i],yt))
ax4.set_xlabel('Contour change (m)',fontsize=8)
ax4.set_ylabel('Relative northing (m)',fontsize=8)
ax4.set_xticks([0,5,10,15])
ax3.set_ylim(300,555)
fig.legend((H[2][0],H[1][0],H[0][0]),('0.00 m','-0.50 m','-0.75 m'),loc='lower left',bbox_to_anchor=(.76,.15,.07,.5),labelspacing=.2,borderpad=0.2)



# Waves plot #
waveobj = utils.NDBCWaveRecord(41114,[2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020])
waves14_full = waveobj.download()
h = waves14_full['wvht (m)']
exc = np.percentile(h,95)
del waves14_full

waveobj = utils.NDBCWaveRecord(41114,2020)
waves14 = waveobj.download()

waves14 = waves14.iloc[list(np.where(waves14['mo']==3)[0])]
waves14 = waves14.iloc[list(np.where(waves14['day']>=7)[0])]
waves14 = waves14.iloc[list(np.where(waves14['day']<=14)[0])]
waves14 = waves14.reset_index()

k = []
for i in np.array(waves14['DPD (sec)']):
    k.append(utils.newtRaph(i,16.2))

dtimes = []
for i in range(0,len(waves14)):
    if waves14['mo'][i]<10:
        dummo = '0'
    else:
        dummo = ''
    if waves14['day'][i]<10:
        dumday = '0'
    else:
        dumday = ''
    if waves14['hr'][i]<10:
        dumhr = '0'
    else:
        dumhr = ''
    if waves14['mm'][i]<10:
        dummm = '0'
    else:dummm = ''
    
    dtimes.append(str(waves14['yr'][i])+dummo+str(waves14['mo'][i])+dumday+str(waves14['day'][i])+dumhr+str(waves14['hr'][i])+dummm+str(waves14['mm'][i]))
d = pd.to_datetime(dtimes)

plt.rcParams.update({'font.size': 8})
fig,ax = plt.subplots(2,1,figsize=(4,3),sharex=True)
ax[0].plot(d,waves14['wvht (m)'])
ax[0].set_ylim(1,3)
ax[0].set_yticks(np.arange(1,4,1))
ax[0].set_ylabel('$H_s$ (m)',fontsize=8)
ax[0].plot((datetime.datetime(2020,3,7),datetime.datetime(2020,3,15)),(exc,exc),'k--')
rv1 = Rectangle((datetime.datetime(2020,3,7,9),min(ax[0].get_ylim())),datetime.datetime(2020,3,7,18)-datetime.datetime(2020,3,7,9),np.diff(ax[0].get_ylim())[0],
                edgecolor=(1,1,.5),facecolor=(1,1,.5),linestyle='-')
rv2 = Rectangle((datetime.datetime(2020,3,14,8),min(ax[0].get_ylim())),datetime.datetime(2020,3,14,18)-datetime.datetime(2020,3,14,8),np.diff(ax[0].get_ylim())[0],
                edgecolor=(1,1,.5),facecolor=(1,1,.5),linestyle='-')
ax[0].add_artist(rv1)
ax[0].add_artist(rv2)
ax[0].text(datetime.datetime(2020,3,13),exc+.06,'Storm threshold',fontsize=8,horizontalalignment='center')
ax[0].text(datetime.datetime(2020,3,14,11),1.27,'Video collected',fontsize=8,rotation=90)
ax[0].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

ax[1].set_xlim(datetime.datetime(2020,3,7),datetime.datetime(2020,3,15))
r = Rectangle((min(ax[1].get_xlim()),.01),np.diff(ax[1].get_xlim())[0],.02,edgecolor=(.3,.3,.3),facecolor=(.7,.7,.7),linestyle='--')
ax[1].add_artist(r)
ax[1].plot(d,waves14['wvht (m)']/np.divide(math.pi*2,k),'-')
dfmt = mdates.DateFormatter('%m/%d')
ax[1].xaxis.set_major_formatter(dfmt)
ax[1].set_ylabel('Steepness',fontsize=8)
rv1 = Rectangle((datetime.datetime(2020,3,7,9),min(ax[1].get_ylim())),datetime.datetime(2020,3,7,18)-datetime.datetime(2020,3,7,9),np.diff(ax[1].get_ylim())[0],
                edgecolor=(1,1,.5),facecolor=(1,1,.5),linestyle='-')
rv2 = Rectangle((datetime.datetime(2020,3,14,8),min(ax[1].get_ylim())),datetime.datetime(2020,3,14,18)-datetime.datetime(2020,3,14,8),np.diff(ax[1].get_ylim())[0],
                edgecolor=(1,1,.5),facecolor=(1,1,.5),linestyle='-')
ax[1].add_artist(rv1)
ax[1].add_artist(rv2)
ax[1].text(datetime.datetime(2020,3,13,1),.021,'Erosion/accretion',fontsize=8,horizontalalignment='center')
ax[1].text(datetime.datetime(2020,3,13,1),.014,'threshold range',fontsize=8,horizontalalignment='center')

ax[0].text(0.01, 0.97, 'a', transform=ax[0].transAxes,fontsize=8, fontweight='bold', va='top')
ax[1].text(0.01, 0.97, 'b', transform=ax[1].transAxes,fontsize=8, fontweight='bold', va='top')





