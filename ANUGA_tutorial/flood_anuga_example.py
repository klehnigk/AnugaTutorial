"""Script for running the moses coulee flood simulation. Takes 5 command line 
arguments corresponding to the volume of water added to the system per second,
the time the simulation will run for, the resolutions of the outside area, the
resolution of the smaller polygon, and the output folder name.
"""

#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
import anuga
import os #does file manipulation
import time
import sys #does command line arguments
import numpy #does math, i don't think it's necessary
import shutil #for copying the file
import glob

from anuga import distribute, myid, numprocs, finalize, barrier, file_function
from anuga import Inlet_operator

#------------------------------------------------------------------------------
# Process command line arguments on processor 0. Arguments are described above.
#------------------------------------------------------------------------------

try:
    #Edit the time, tstep, and both root variables
    time = 250000
    default_res = int(sys.argv[1])  
    small_res = int(sys.argv[2])    
    outfol = sys.argv[3]

except:
    print 'Incorrect command arguments for simluation. Arguments should be:\n\
    <InputVol> <FinalTime> <OutsideResolution> <FineResolution> <OutFolder>'
    sys.exit()
    
try:
    if myid==0: 
	root = 'tutorial' # variable will be name of all input and output variables
    domain = load_checkpoint_file(domain_name = root, checkpoint_dir = 'checkpoints_'+outfol)
    
except:

#------------------------------------------------------------------------------
# File Processing. If necessary, creates the output directory and copies the
# moses_gauges file to the new directory.
#------------------------------------------------------------------------------

    if myid == 0:
    
	print 'Starting run'
    
	root = 'tutorial' # variable will be name of all input and output variables
	sww_file = root + '.sww' # name of the sww output file from previous segment
	gauge_out = root + '_gage_output.csv'   # name of the file to which depths will be written
	gauge_in_file = root + '_gages.csv' # name of the gage file to be read in
	ascii_file = root + '.asc'  # name of the ascii DEM
	dem_file = root	+ '.dem'    # name of the DEM file produced by txt2tms.py
	bnd_file = root +'_bnd.csv' # name of the boundary file
	msh_file = root	+ '.tsh'    # name of the tsh file produced by txt2tms.py
	tms_file = root	+ '.tsh'    # name of the tms file produced by txt2tms.py
	pts_file = root	+ '.pts'    # name of the pts file produced by txt2tms.py
        Qbc_file = root + '_inlet.csv' #csv file of points specifying location of inlet (basically the inflow boundary)

        
	if not os.path.exists(outfol):
	    os.makedirs(outfol)
	    shutil.copyfile(gauge_in_file, '%s/%s' %(outfol, gauge_in_file))
    
	#------------------------------------------------------------------------------
	# Preparation of topographic data
	# Convert ASC 2 DEM 2 PTS using source data and store result in source data
	#------------------------------------------------------------------------------
    
	# Create DEM from asc data
	anuga.asc2dem(ascii_file, use_cache=False, verbose=False) #ascii exported from dem in arcgis
	# Create pts file for onshore DEM
	anuga.dem2pts(dem_file, use_cache=False, verbose=False)
    
	#------------------------------------------------------------------------------
	# Create the triangular mesh and domain based on
	# overall clipping polygon with a tagged
	# boundary and interior regions as defined in project.py
	#------------------------------------------------------------------------------
    
	# bounding polygon for study area
	bounding_polygon = anuga.read_polygon(bnd_file)
	
	# Uncomment if using breakllines
	#breaklinedir='breaklines/*.csv'     #directory where the breakline csv file(s) are stored
        #c=1
        #for fname in glob.glob(breaklinedir):
        #    bki=anuga.read_polygon(fname)
        #    if c==1:
        #        bklines=numpy.array(bki)
        #    else:
        #        bklines=[bklines,numpy.array(bki)]
        #    c=c+1
        #bklines = anuga.read_polygon('breaklines1.csv')
        #print(bklines)
	
	#Set up the interior polygon
	pol_1 = anuga.read_polygon('pol_1.csv')
	
	#Set up the bounding polygon
	#Uncomment this section if using breaklines
	#domain = anuga.create_domain_from_regions(bounding_polygon, boundary_tags={'s0': [0], 's1': [1], 's2': [2], 's3': [3], 's4': [4], 's5': [5], 's6': [6], 's7': [7], 's8': [8], 's9': [9], 's10': [10], 's11': [11], 's12': [12], 's13': [13], 's14': [14], 's15': [15], 's16': [16], 's17': [17], 's18': [18]}, maximum_triangle_area = default_res, mesh_filename = msh_file, interior_regions = [[pol_1, small_res]], interior_holes=None, hole_tags=None, minimum_triangle_angle=28.0, fail_if_polygons_outside=True, breaklines=[bklines], use_cache = False, verbose = True)

	domain = anuga.create_domain_from_regions(bounding_polygon, boundary_tags={'s0': [0], 's1': [1], 's2': [2], 's3': [3], 's4': [4], 's5': [5], 's6': [6], 's7': [7]}, maximum_triangle_area = default_res, mesh_filename = msh_file, interior_regions = [[pol_1, small_res]], use_cache = False, verbose = True)
	
	
    
	# Print some stats about mesh and domain
	print 'Number of triangles = ', len(domain)
	print 'The extent is ', domain.get_extent()
	print domain.statistics()
    
	#------------------------------------------------------------------------------
	# Setup parameters of computational domain
	#------------------------------------------------------------------------------
    
	domain.set_name(sww_file) # Name of sww file
	domain.set_datadir('./%s/' %outfol) # changes directory to output folder
    
	#------------------------------------------------------------------------------
	# Setup initial conditions
	#------------------------------------------------------------------------------
    
	domain.set_quantity('stage', 0.0)
	domain.set_quantity('friction', 0.065)
	domain.set_quantity('elevation', filename=pts_file,
	                use_cache = False,
	                verbose  =False,
	                alpha  =0.1) #topographic smoothing; see user manual
    else:
	domain = None
    
    #------------------------------------------------------------------------------
    # Now produce parallel domain 
    #------------------------------------------------------------------------------
    
    domain = distribute(domain) 
    
    domain.set_store_vertices_uniquely(True) 

    #Set up inlet
    bcline = anuga.read_polygon('tutorial_inlet.csv')
    Q1 = file_function(filename='tutorial.tms', quantities=['hydrograph'])
    anuga.Inlet_operator(domain, bcline, Q = Q1)
    
    
    #------------------------------------------------------------------------------
    # Setup boundary conditions
    #------------------------------------------------------------------------------
    
    Br = anuga.Reflective_boundary(domain)
    Bt = anuga.Transmissive_boundary(domain)
    Bo = anuga.Dirichlet_boundary([-425, 0, 0])
    Boh = anuga.Dirichlet_boundary([620, 0, 0])
    Bol = anuga.Dirichlet_boundary([300, 0, 0]) #outflow.  Values of stage, x and y momentum.  The boundary will input of output water to attempt to get to the specified height. Negative stage is used to remove water and avoid numerical instability associated with transmissive boundary
    domain.set_boundary({'s0': Br, 's1': Br, 's2': Br, 's3': Bo, 's4': Bo, 's5': Bo, 's6': Br, 's7': Br})
    
    #Uncomment if using checkpoints
    #domain.set_checkpointing(checkpoint_time = 150000, checkpoint_dir = 'checkpoints_'+outfol)  #writes checkpoint file every 50 yieldsteps

#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------

# genertes .sww file
prev_dep=domain.get_quantity('stage').get_integral()
for t in domain.evolve(yieldstep=10000, finaltime=time): #yieldstep is where timestep can be specified
    if myid == 0:
        print domain.timestepping_statistics() #prints the timestep, time it took to run previous timestep, among other things
        cur_dep=domain.get_quantity('stage').get_integral()
        change = cur_dep - prev_dep
        prev_dep = cur_dep

domain.sww_merge(delete_old=True)

finalize()

if myid == 0:
    print 'run complete'
