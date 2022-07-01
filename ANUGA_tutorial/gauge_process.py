#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
import anuga 
import os #does file manipulation
import time
import sys #does command line arguments
import numpy #does math, i don't think it's necessary
import shutil #for copying the file

from anuga.structures.inlet_operator import Inlet_operator

#*##############################################################################
# Gauge processing
#*##############################################################################


#------------------------------------------------------------------------------
# change working directory and create  and loop variables
#------------------------------------------------------------------------------

#os.chdir('./%s/'%outfol) #changes the directory of the program to the output folder as specified in the command arguments
names=[]  #array used to hold the list of gauge sample names
output=[] #array used to hold all the depths over time
b=True    #boolean variable for loop manipulation

#------------------------------------------------------------------------------
# create the gauge files
#------------------------------------------------------------------------------
sww_file = 'tutorial.sww'
gauge_in_file = 'tutorial_gages.csv'
gauge_out = 'tutorial_gage_stages.csv'

anuga.sww2csv_gauges(sww_file, gauge_in_file, quantities=['depth'], verbose=True)

#------------------------------------------------------------------------------
# combine all the gauge files into one output csv file
#------------------------------------------------------------------------------

with open(gauge_in_file,'r') as f: #opens the file that contains the list of gauge names and locations
    f.readline()
    for line in f: 
        line=line.split(',')
        oname='gage_'+line[2]+'.csv'
        names.append(oname) #adds each gauge name to the array in order

for name in names: # this loop will run once for each name (and thus each gauge)
    if b: #this section will only execute the first run through
        b=False
        with open(name,'r') as cur_file:  #opens the corresponding gauge file
            cur = cur_file
            cur_file.readline()
            for line in cur_file:
                dep = line.split(',')[2].strip()
                output.append([float(dep)]) #processes the string into a useful format (a float in this case) and adds it to the array
    else: #this section will execute every run through except the first.  It functions the same except adding to each element of the array
        n=0
        with open(name,'r') as cur_file:
            cur_file.readline()
            for line in cur_file:
                dep = line.split(',')[2].strip()
                output[n].append(float(dep)) #processes each data point of the gauge file and adds it to the output
                n+=1
    os.remove(name) #this line deletes the gauge filesmade by the anuga method.  It's not necessary for functionality but makes the file directory cleaner
    
with open(gauge_out,'w') as out_file: #opens an output file and writes the output to the file. Note the output file is csv (comma seperated) and is usable in excel.
    for el in output:
        out_file.write(str(el).strip('[]'))
        out_file.write(' \n')        

print 'run complete'
