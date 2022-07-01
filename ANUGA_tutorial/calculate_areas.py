import arcpy
import os
from arcpy import env
from arcpy.sa import *
import shutil
import fileinput
import sys
import csv

#this script runs from python 2.7 IDE

#Set to directory with ANUGA-produced asciis
env.workspace = r"C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\"
outws = r"C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\"

#Need to change these for each set, and verify they are in the correct order
discharges = ["100000","500000"]	#In alphabetical order
timesteps = ["10","25"]

scenario = "tutorial_run1"	#change for each run

#Need to change these to the correct zone for the scenario in questio
hw_inner = "C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\area_shapefiles\\zone_simple_north_small_inner.shp"
hw_outer = "C:\\Users\\klehnigk2\\Documents\\GitHub\\AnugaTutorial\\ANUGA_tutorial\\area_shapefiles\\zone_simple_north_small_outer.shp"

file1=open(outws+scenario+".txt","w")
writer = csv.writer(file1, dialect='excel')

total_areas_inner = []
total_areas_outer = []
all_areas = []
all_areas_title = ["timestep (s)","discharge (cms)","total outer area (m2)","total inner area(m2)"]
writer.writerow(['timestep (s)','discharge (cms)','total outer area (m2)','total inner area(m2)']) 

inputshps_list = arcpy.ListFiles("outline_*.shp")
inputshps=sorted(inputshps_list)
print(inputshps)

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
index = 0
for i in inputshps:
	tstep = timesteps[index]
	all_areas.append(int(tstep))
	Q = discharges[index]
	all_areas.append(int(Q))
	print(tstep)
	print(Q)
	shpname = i.strip("outline_")
	Input_shp = env.workspace+"\\"+i
	print(Input_shp)
	outname = shpname.strip(Q+".shp")
	ext_inner=outws+outname+Q+"_inner_negative.shp"
	ext_outer=outws+outname+Q+"_outer.shp"
	print("clipping")
	print(ext_inner)
	print(ext_outer)
	# Process: Clip (inner)
	arcpy.Clip_analysis(Input_shp, hw_inner, ext_inner, "")
	# Process: Clip (outer)
	arcpy.Clip_analysis(Input_shp, hw_outer, ext_outer, "")
	print("erasing")
	# Process: Erase (inner)
	erase_inner=outws+outname+Q+"_inner.shp"
	arcpy.Erase_analysis(hw_inner, ext_inner, erase_inner, "")
	print(erase_inner)

	# Process: Dissolve (inner)
	print("dissolving inner")
	diss_inner=outws+outname+Q+"_inner_diss.shp"
	arcpy.Dissolve_management(erase_inner, diss_inner, "Id", "", "MULTI_PART", "DISSOLVE_LINES")
	print(diss_inner)
	
	# Process: get areas (inner)
	arcpy.AddField_management(diss_inner, "Shape_area", "DOUBLE")
	exp1 = "!SHAPE.AREA@SQUAREKILOMETERS!"
	arcpy.CalculateField_management(diss_inner, "Shape_area", exp1, "PYTHON_9.3")
	geometryField = arcpy.Describe(diss_inner).shapeFieldName #Get name of geometry field
	cursor = arcpy.UpdateCursor(diss_inner)
	shape_areas=[]
	try:
		for row in cursor:
			AreaValue = row.getValue(geometryField).area #Read area value as double
			shape_areas.append(AreaValue)
			row.setValue("Shape_area",AreaValue) #Write area value to field
			cursor.updateRow(row)
		del row, cursor #Clean up cursor objects
		inner_total_area=sum(shape_areas)
	except NameError:
		inner_total_area=0
	all_areas.append(inner_total_area)
	total_areas_inner.append(inner_total_area)
	print(inner_total_area)
	
	# Process: Dissolve (outer)
	print("dissolving outer")
	diss_outer=outws+outname+Q+"_outer_diss.shp"
	arcpy.Dissolve_management(ext_outer, diss_outer, "Id", "", "MULTI_PART", "DISSOLVE_LINES")
	print(diss_outer)
	
	# Process: get areas (outer)
	print("making tables")
	arcpy.AddField_management(diss_outer, "Shape_area", "DOUBLE")
	exp = "!SHAPE.AREA@SQUAREKILOMETERS!"
	arcpy.CalculateField_management(diss_outer, "Shape_area", exp, "PYTHON_9.3")
	geometryField = arcpy.Describe(diss_outer).shapeFieldName #Get name of geometry field
	cursor = arcpy.UpdateCursor(diss_outer)
	shape_areas=[]
	try:
		for row in cursor:
			AreaValue = row.getValue(geometryField).area #Read area value as double
			shape_areas.append(AreaValue)
			row.setValue("Shape_area",AreaValue) #Write area value to field
			cursor.updateRow(row)
		del row, cursor #Clean up cursor objects
		outer_total_area=sum(shape_areas)
	except NameError:
		outer_total_area=0
	total_areas_outer.append(outer_total_area)
	all_areas.append(outer_total_area)
	print(outer_total_area)
	
	writer.writerow([int(tstep), int(Q), outer_total_area, inner_total_area])
	all_areas=[]
	index = index + 1
	
file1.close()
print("complete")

