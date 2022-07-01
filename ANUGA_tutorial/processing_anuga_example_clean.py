'''
Python script for extracting gridded outputs from ANUGA .sww file and for 
calculating Froude number, shear stress and velocity angle from those outputs.
Paste this file in the same directory as the ANUGA .sww file and execute.
Isaac Larsen 27 March 2015
Modified to include spatial variability in Manning's n and to time-average
outputs on 13 July 2015
Modified to extract output at multiple timestepts when using a hydrograph on August 25 2019
'''

import os
import sys
import math
import anuga
import numpy as np
import shutil
import pdb #pdb.set_trace()
from linecache import getline
from glob import glob

#Edit name, Q, and red fields for each rus
name = "tutorial"  #name of ANUGA .sww output file
Q = "tutorial_run1"     #discharge of simulation (m3s-1)
g = 9.80665     #acceleration due to gravity m s-2
rho_w = 1000    # density of water kg m-3
n = 0.065       #mannings n, uncomment this line and comment line 338 if there is a single Manning's n value
cell = 30       #cell is the resolution of the gridded output data in meters.

#red = 100      #outputs data from final timestep only  
#red (reduction) is the timestep from which to export the results (the ANUGA default is: max). This value depends on the timestep in the main flood_sim_....py code.  For example, if the run is 10,000 seconds and the timestep is 100 s, a value of 100 (10000/100=100) will give you the data for the final timestep 

red = [10,25] #set to be 91 to 101 generally, for last ten values in .sww file
for j in range(0,len(red)):#red:
	var = range (0, 10)
	for i in var:
	    if i == 0: # Stage
		outname = name + '_stage_' + Q +'_' + str(red[j])
		quantityname = 'stage'
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)
	    if i == 1: # Absolute Momentum
		outname = name + '_momentum_' + Q +'_' + str(red[j])
		quantityname = '(xmomentum**2 + ymomentum**2)**0.5' #Absolute momentum
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)        
	    if i == 2: # Depth
		outname = name + '_depth_' + Q +'_' + str(red[j])
		quantityname = 'stage-elevation' #Depth
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)        
	    if i == 3: # Velocity
		outname = name + '_velocity_' + Q +'_' + str(red[j])
		quantityname = '(xmomentum**2 + ymomentum**2)**0.5/(stage-elevation+1.e-30)' #Velocity
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)        
	    if i == 4: # Elevation
		outname = name + '_elevation_' + Q +'_' + str(red[j])
		quantityname = 'elevation' #Elevation
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)        
	    if i == 5: # xmomentum
		outname = name + '_xmomentum_' + Q +'_' + str(red[j])
		quantityname = 'xmomentum' #xmomentum    
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)        
	    if i == 6: # ymomentum
		outname = name + '_ymomentum_' + Q +'_' + str(red[j])
		quantityname = 'ymomentum' #ymomentum
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)                   
	    if i == 7: # xvelocity
		outname = name + '_xvelocity_' + Q +'_' + str(red[j])
		quantityname = '(xmomentum/(stage-elevation+1.e-30))' #xvelocity
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)    
	    if i == 8: # yvelocity
		outname = name + '_yvelocity_' + Q +'_' + str(red[j])
		quantityname = '(ymomentum/(stage-elevation+1.e-30))' #yvelocity
		anuga.sww2dem(name+'.sww', outname+'.asc', quantity=quantityname, cellsize=cell, reduction=red[j], verbose=True)      
	    if i == 9: # Calculations    
		source = name + '_xmomentum_' + Q + '_' + str(red[j]) + '.asc' #source file for header 
		NODATA = -9999 #cell value for no data
	
		# copy header lines from: http://geospatialpython.com/2013/12/python-and-elevation-data-creating.html
		hdr = [getline(source, k) for k in range(1,7)]
		#pdb.set_trace()
		values = [float(h.split(" ")[-1].strip()) \
		 for h in hdr]
		cols,rows,lx,ly,cell,nd = values
		xres = cell
		yres = cell * -1        
		
		# load one grid used to set NO DATA values
		xmomentum = np.loadtxt(name + '_xmomentum_' + Q +'_' + str(red[j]) + '.asc', skiprows=6)        
		                            
		
	   
		#write a new projection file to fix UTM zone change from -1 to 11
		f = open("new.prj","w")
		f.write("Projection\tUTM\n")
		f.write("Zone\t11\n")
		f.write("Datum\tNAD27\n")
		f.write("Spheroid\tCLARKE1866\n")
		f.write("Units\tMETERS\n")
		f.write("Zunits\t10.0\n")
		f.write("Parameters")        
		f.close()
		
		#copy the new projection file with names to match all ascii grid files
		shutil.copy('new.prj', name + '_depth_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_elevation_' + Q +'_' + str(red[j])+ '.prj') 
		shutil.copy('new.prj', name + '_tau_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_froude_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_momentum_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_stage_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_vangle_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_velocity_' + Q +'_' + str(red[j])+ '.prj')  
		shutil.copy('new.prj', name + '_xmomentum_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_xvelocity_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_ymomentum_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_yvelocity_' + Q +'_' + str(red[j])+ '.prj')

                	#copy the new projection file with names to match all clipped/averaged ascii grid files
		shutil.copy('new.prj', name + '_depth_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_elevation_clip_' + Q +'_' + str(red[j])+ '.prj') 
		shutil.copy('new.prj', name + '_tau_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_froude_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_momentum_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_stage_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_vangle_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_velocity_clip_' + Q +'_' + str(red[j])+ '.prj')  
		shutil.copy('new.prj', name + '_xmomentum_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_xvelocity_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_ymomentum_clip_' + Q +'_' + str(red[j])+ '.prj')
		shutil.copy('new.prj', name + '_yvelocity_clip_' + Q +'_' + str(red[j])+ '.prj')

                
		#copy and rename the gauge and .sww files with the discharge appended
		#shutil.copy(name + '_gauge_output.csv', name + '_gauge_output_' + Q + '.csv')
		shutil.copy(name + '.sww', name + Q + '.sww')
		
                #calculate Froude number
                xmomentum = np.loadtxt(name + '_xmomentum_' + Q + '_' + str(red[j]) + '.asc', skiprows=6)        
                ymomentum = np.loadtxt(name + '_ymomentum_' + Q + '_' + str(red[j]) + '.asc', skiprows=6) 
                stage = np.loadtxt(name + '_stage_' + Q + '_' + str(red[j]) + '.asc', skiprows=6) 
                elevation = np.loadtxt(name + '_elevation_' + Q  + '_' + str(red[j]) + '.asc', skiprows=6) 
                velocity = np.loadtxt(name + '_velocity_' + Q + '_' + str(red[j]) + '.asc', skiprows=6)
                depth = np.loadtxt(name + '_depth_' + Q + '_' + str(red[j]) + '.asc', skiprows=6) 
                xvelocity = np.loadtxt(name + '_xvelocity_' + Q + '_' + str(red[j]) + '.asc', skiprows=6)
                yvelocity = np.loadtxt(name + '_yvelocity_' + Q + '_' + str(red[j]) + '.asc', skiprows=6)      
                



                #Average stage
                temp = np.loadtxt(name + '_stage_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp

                # Rebuild the new headers for average stage

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_stage_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e") 	
	
                #Average absolute momentum
                temp = np.loadtxt(name + '_momentum_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_momentum_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e") 	
    	
                #Average depth
                temp = np.loadtxt(name + '_depth_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_depth_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e") 

                #Average velocity
                temp = np.loadtxt(name + '_velocity_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_velocity_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e") 

                #Average elevation
                temp = np.loadtxt(name + '_elevation_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp
                        
                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_elevation_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e") 	

                #Average xmomentum
                temp = np.loadtxt(name + '_xmomentum_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_xmomentum_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e")

                #Average ymomentum
                temp = np.loadtxt(name + '_ymomentum_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp
                
                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                #Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_ymomentum_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e")

                #Average xvelocity
                temp = np.loadtxt(name + '_xvelocity_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_xvelocity_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e")

                #Average yvelocity
                temp = np.loadtxt(name + '_yvelocity_' + Q +'_' + str(red[j]) + '.asc', skiprows=6) #.format(1)	
                mean = temp

                # Rebuild the new headers for average momentum

                header = "ncols        %s\n" % mean.shape[1]
                header += "nrows        %s\n" % mean.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean[xmomentum == nd] = NODATA
                mean[xmomentum == 0.0] = NODATA

                # save grid
                with open(name + '_yvelocity_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean, fmt="%4.3e")


                # Calculate Froude number
                mean_froude =  (velocity/((g*depth)**0.5)) #Froude number

                # Rebuild the new header
                header = "ncols        %s\n" % mean_froude.shape[1]
                header += "nrows        %s\n" % mean_froude.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean_froude.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean_froude.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean_froude[xmomentum == nd] = NODATA
                mean_froude[xmomentum == 0.0] = NODATA

                # save Froude number grid
                with open(name + '_froude_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean_froude, fmt="%4.3e")        
 
                #calculate non-uniform shear stress
                mean_tau = (rho_w*g*(n**2)*((velocity**2))/((depth)**(1.0/3)))      
                # Rebuild the new header
                header = "ncols        %s\n" % mean_tau.shape[1]
                header += "nrows        %s\n" % mean_tau.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - mean_tau.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - mean_tau.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                mean_tau[xmomentum == nd] = NODATA
                mean_tau[xmomentum == 0.0] = NODATA

                # save shear stress grid
                with open(name + '_tau_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, mean_tau, fmt="%4.3e")              

                #Calculate velocity_angle       
                angle = (np.degrees(np.arctan2(yvelocity,xvelocity)))
                angle = (angle +360) % 360 # clever trick uses % as modulo, see below

                # Rebuild the new header
                header = "ncols        %s\n" % angle.shape[1]
                header += "nrows        %s\n" % angle.shape[0]
                header += "xllcorner    %s\n" % \
                          (lx + (cell * (cols - angle.shape[1])))
                header += "yllcorner    %s\n" % \
                          (ly + (cell * (rows - angle.shape[0])))
                header += "cellsize     %s\n" % cell
                header += "NODATA_value      %s\n" % NODATA        

                # Set no-data values
                angle[xmomentum == nd] = NODATA
                angle[xmomentum == 0.0] = NODATA

                # save velocity angle grid
                with open(name + '_vangle_clip_' + Q + '_' + str(red[j]) + '.asc', "wb") as f:
                        f.write(header)
                        np.savetxt(f, angle, fmt="%4.3e")


# Cleanup
os.remove('new.prj') #delete the new.prj file
os.remove(name + Q + '.sww') #delete the copied .sww file

for j in range(0,len(red)):#delete non-clipped ascii files
	os.remove(name + '_stage_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_momentum_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_depth_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_velocity_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_elevation_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_xmomentum_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_ymomentum_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_xvelocity_' + Q +'_' + str(red[j]) + '.asc') 
	os.remove(name + '_yvelocity_' + Q +'_' + str(red[j]) + '.asc') 

print 'ascii grid processing complete'
	
'''
Convert vector angles to 0-359 degree range 
(in mathematical reference frame with 0 degrees being due east in a geographical reference)
Liam George Betsworth        http://stackoverflow.com/questions/1311049/how-to-map-atan2-to-degrees-0-360
Solution using Modulo
A simple solution that catches all cases.
degrees = (degrees + 360) % 360;
Explanation
Positive: 0 to 180
If you add 360 to a positive number between 0 and 180, then mod it by 360, you will get the exact same number you put in. Mod here just ensures these positive numbers are returned as the same value.
Negative: -180 to 0
If you add 360 to a negative number between -180 and 0, you'll get a range of values between 180 and 360 degrees.
Zero: 0
If you add 360 to 0, you get 360. Using mod means that 0 is returned again, making this a safe 0-359 degrees solution.'''

