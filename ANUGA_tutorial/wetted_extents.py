import arcpy
import os
from arcpy import env
from arcpy.sa import *
import shutil
import fileinput
import sys
import csv

#This script runs from python 2.7 IDE

#Set to directory with ANUGA-produced asciis
env.workspace = r"C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\"
outws = r"C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\"

#Need to change these for each set, and verify they are in the correct order
discharges = ["100000","500000"]	
timesteps = ["10","25"]	#In alphabetical order

scenario = "tutorial_run1"	#change this for each scenario

inputDEMs_list = arcpy.ListFiles("tutorial_stage_*.asc")	#change this for each scenario
inputDEMs = sorted(inputDEMs_list)
print(inputDEMs)

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
index = 0
for i in inputDEMs:
	tstep = timesteps[index]
	Q = discharges[index]
	print(tstep)
	DEMname = i.strip("tutorial_stage_clip_*") 	#change this for each scenario
	Input_ascii = env.workspace+"\\"+i
	print(Input_ascii)
	outname_rm = DEMname.strip(tstep+".asc")
	outname = scenario+"_"
	ext=outws+"stage_"+outname+Q+".tif"
	# Process: ASCII to Raster
	arcpy.ASCIIToRaster_conversion(Input_ascii, ext, "INTEGER")
	print(ext)
	# Process: Raster to Polygon
	poly=outws+"stage_outline_"+outname+Q+".shp"
	arcpy.RasterToPolygon_conversion(ext, poly, "NO_SIMPLIFY", "Value")
	# Process: Dissolve
	diss=outws+"outline_"+outname+Q+".shp"
	arcpy.Dissolve_management(poly, diss, "", "", "MULTI_PART", "DISSOLVE_LINES")
	# Process: Define Projection
	arcpy.DefineProjection_management(diss, "PROJCS['NAD_1927_UTM_Zone_11N',GEOGCS['GCS_North_American_1927',DATUM['D_North_American_1927',SPHEROID['Clarke_1866',6378206.4,294.9786982]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]],VERTCS['Unknown VCS',VDATUM['Unknown'],PARAMETER['Vertical_Shift',0.0],PARAMETER['Direction',1.0],UNIT['User_Defined_Unit',0.1]]")	
	# Process: Polygon To Line
	poly_line = outws+"line_"+outname+Q+".shp"
	arcpy.PolygonToLine_management(diss, poly_line, "IDENTIFY_NEIGHBORS")
	# Process: Dissolve
	diss_line=outws+"line_dis_"+outname+Q+".shp"
	arcpy.Dissolve_management(poly_line, diss_line, "", "", "MULTI_PART", "DISSOLVE_LINES")	
	
	index = index + 1