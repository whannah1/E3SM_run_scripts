# -*- coding: utf-8 -*-
"""
Will generate a mapping file to produce horizontally averaged output
during runtime for DPxx simulations. NOTE that these simple mapping files
will ONLY work for online DPxx remapping and not offline. The eamxx online
horizontal mapping only needs S (sparse matrix for weights), col, row, which is
what the script does. The map file used for offline mapping (.e.g., nco) requires
other "nominal" variables (frac_a/b, area_a/b, yc_a/b, xc_a/b, yv_a/b, xv_a/b,
src_grid_dims, dst_grid_dims). These nominal variables require other procedures
to generate (e.g., by a complex art of ESMF-NCL), but some field values are meaningless
in DPxx cases and are indeed not required by online mapping.

User only needs to supply basic geometry data for their DPxx simulation.  This
needs to be exactly the same as you've specified in your run script for
NX, NY, LX, LY.

Once you have generated your mapping file simply point to it in your YAML file like so:
horiz_remap_file: /path/to/your/file/mapping_dpxx_x200000m_y200000m_nex20_ney20_to_1x1.20241024.nc

Script authors: Peter Bogenschutz (bogenschutz1@llnl.gov)
                Jishi Zhang (zhang73@llnl.gov)
"""
#-------------------------------------------------------------------------------
import os, netCDF4 as nc4, numpy as np
from datetime import datetime
#---------------------------------------------------------------------------------------------------
class tclr: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#-------------------------------------------------------------------------------
opts_list = []
def add_grid( **kwargs ):
   loc_opts = {}
   for k, val in kwargs.items(): loc_opts[k] = val
   opts_list.append(loc_opts)
#-------------------------------------------------------------------------------

output_root = os.getenv('HOME')+"/maps/" # path where mapping file will be placed

# These geometry parameters should match what you plan to use in your simulation

# add_grid(NE=223,LX=int(500e3))
# add_grid(NE=112,LX=int(500e3))
# add_grid(NE= 56,LX=int(500e3))
# add_grid(NE= 28,LX=int(500e3))
# add_grid(NE= 14,LX=int(500e3))
# add_grid(NE=  7,LX=int(500e3))
# add_grid(NE=  4,LX=int(500e3))

# add_grid(NE=200,LX=int(600e3))
# add_grid(NE=1000,LX=int(600e3))

# add_grid(NE=67,LX=int(600e3))
# add_grid(NE=34,LX=int(600e3))
# add_grid(NE=17,LX=int(600e3))
# add_grid(NE= 9,LX=int(600e3))
# add_grid(NE= 5,LX=int(600e3))

add_grid(NE= 22,LX=int(200e3))
add_grid(NE= 66,LX=int(200e3))
add_grid(NE=333,LX=int(200e3))

# formatted_date = '20251217'

#-------------------------------------------------------------------------------
# for NE in NE_list:
# for n in range(len(opt_list)): 
for opts in opts_list:
   NE = opts['NE']
   LX = opts['LX']

   NX,NY=NE,NE
   LY=LX

   # Figure out number of physics columns
   phys_col=NX*NY*4

   # Compute the physics resolution
   dx=float(LX)/(NX*2.0)
   dy=float(LY)/(NY*2.0)

   # Compute the area of each column
   area_col=dx*dy
   area_dom=float(LX)*float(LY)

   S_in=np.float64(area_col/area_dom)
   col_in=np.arange(phys_col)+1
   row_in=np.ones(phys_col)

   ### Now make the output file

   # # what is the current date?
   # current_date = datetime.now()
   # formatted_date = current_date.strftime("%Y%m%d")

   # Make output string
   filename=f'map_dpxx_x{LX}m_y{LY}m_nex{NX}_ney{NY}_to_1x1.nc'
   # filename=f'map_dpxx_x{LX}m_y{LY}m_nex{NX}_ney{NY}_to_1x1.{formatted_date}.nc'

   fullfile=output_root+filename

   # check to see if outputfile already exists, if so overwrite
   ishere=os.path.isfile(fullfile)
   if ishere:
      os.system('rm '+fullfile)

   # f=nc4.Dataset(fullfile,'w',format='NETCDF4')
   f=nc4.Dataset(fullfile,'w',format='NETCDF3_64BIT_DATA')
   f.createDimension('n_s',phys_col)
   f.createDimension('n_a',phys_col)
   f.createDimension('n_b',1)

   S=f.createVariable('S','f8','n_s')
   col=f.createVariable('col','i4','n_s')
   row=f.createVariable('row','i4','n_s')

   S[:]=np.full(phys_col, S_in, dtype='float64')
   col[:]=col_in
   row[:]=row_in

   f.close()

   # fullfile_alt = fullfile.replace('.nc','.cdf5.nc')
   # cmd = f'ncks --cdf5 --overwrite {fullfile} {fullfile_alt}'
   # print(); print(cmd)
   # os.system(cmd)

   print(); print(f"  Generated map file: {tclr.GREEN}{fullfile}{tclr.END}")

print()
#-------------------------------------------------------------------------------
