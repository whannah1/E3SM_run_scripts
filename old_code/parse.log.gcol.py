#!/usr/bin/env python
#=============================================================================================================
#  Nov, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the status of current E3SM cases (i.e. debug mode, compset, misc flags, etc.)
#=============================================================================================================
import sys
import os
# import fileinput
import numpy as np
from glob import glob
import netCDF4 as nc4
from datetime import datetime
import subprocess
home = os.getenv("HOME")
host = os.getenv("HOST")

from optparse import OptionParser
parser = OptionParser()
# parser.add_option("-n",dest="num_file",default=5,help="sets number of files to print")
(opts, args) = parser.parse_args()

#=============================================================================================================
# arguments are used to provide a log file
#=============================================================================================================
# if len(args) < 1 :
#     search_strings = []
#     print
#     print("ERROR: no file provided!")
#     print
#     exit()
# else :
#     log_file = args

log_file = '/ccs/home/hannah6/ACME/scratch/ACME_SP1_CTL_ne30_32x1_1km_s2_68/run/acme.log.180320-163826'

out_file = 'gcol.nc'

print("")
print("input log file : "+log_file)
print("output nc file : "+out_file)
print("")


#=============================================================================================================
# Parse log file
#=============================================================================================================

ncol = 48466
n = 0

gcol  = np.zeros(ncol)
latd  = np.zeros(ncol)
lond  = np.zeros(ncol)
alpha = np.zeros(ncol)

ifile = open(log_file,"r",buffering=-1)
for line in ifile :
    if "whannah ,     0" in line:

        line_split = line.split(",")

        # if len(line_split)<2 :
        #     print(line)

        gcol [n] = float( line_split[2] )
        latd [n] = float( line_split[3] )
        lond [n] = float( line_split[4] )
        alpha[n] = float( line_split[5] )

        # print(line)
        # print(gcol)
        # print(latr)
        # print(lonr)
        # print(alpha)

        # exit()

        latd[n] = latd[n] * 180./3.14159
        lond[n] = lond[n] * 180./3.14159

        # ncol = ncol+1
        n = n+1


#=============================================================================================================
# Write data to NetCDF file
#=============================================================================================================

# Create the ncol coordinate for output variables
ncol_coord = np.arange(1,ncol+1,1)
# ncol_coord = [0 for i in xrange(ncol)]

# Create the file
nc_file = nc4.Dataset(out_file,'w', format='NETCDF4')

# Create a data group
data_grp = nc_file.createGroup('ncol_data')

# Define dimensions
data_grp.createDimension('ncol', ncol)

# Create the variables
ncol_out  = data_grp.createVariable('ncol' , 'i4', 'ncol')
gcol_out  = data_grp.createVariable('gcol' , 'i4', 'ncol')
lat_out   = data_grp.createVariable('lat'  , 'f4', 'ncol')
lon_out   = data_grp.createVariable('lon'  , 'f4', 'ncol')
alpha_out = data_grp.createVariable('alpha', 'f4', 'ncol')

ncol_out[:]  = ncol_coord
gcol_out[:]  = gcol
lat_out[:]   = latd
lon_out[:]   = lond
alpha_out[:] = alpha

# Add variable attributes
ncol_out.units  = ''
gcol_out.units  = ''
lat_out.units   = 'degrees north'
lon_out.units   = 'degrees east'
alpha_out.units = 'radians'


# Add global attributes
today = datetime.today()
nc_file.description = "gcol and initial CRM rotation angle"
nc_file.history = "Created " + today.strftime("%d/%m/%y")

# close the file
nc_file.close()



