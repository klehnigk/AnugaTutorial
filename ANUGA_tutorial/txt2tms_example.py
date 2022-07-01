from numpy import array, float
from anuga.file.netcdf import NetCDFFile
#from Scientific.IO.NetCDF import NetCDFFile
from anuga.config import netcdf_float
from anuga.abstract_2d_finite_volumes.util import file_function


dischargeTmsFile="tutorial.tms"
projectFileName="tutorial"


# fid = open("inputhydrograph.txt")
# lines = fid.readlines()
# fid.close()

time = [0,50000,100000,250000]
q = [1000,10000,50000,50000]


#for line in lines:
#    fields = line.split()
#    time.append( float(fields[0]))
#    q.append( float(fields[1]))



# Convert to NetCDF
N = len(time)
T = array(time, int)  # Time (seconds)
R = array(q, float)  # Values (m3/s)


# Create tms NetCDF file
fid = NetCDFFile(dischargeTmsFile, 'w')
fid.institution = projectFileName + '_simulation'
fid.description = projectFileName + '_simulation'
fid.starttime = 0
fid.createDimension('number_of_timesteps', len(T))
fid.createVariable('time', netcdf_float, ('number_of_timesteps',))
fid.variables['time'][:] = T
fid.createVariable('hydrograph', netcdf_float, ('number_of_timesteps',))
fid.variables['hydrograph'][:] = R
fid.close()

# created dischargeTmsFile
