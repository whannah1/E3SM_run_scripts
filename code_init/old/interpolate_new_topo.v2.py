#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Create new topo file for E3SM
# v1 - downscale topo, skip smoothing and skip to step #3
# v2 - downscale to topo and then us TR to interpolate np4 topo to pg2 get 'smoothed' topo
#---------------------------------------------------------------------------------------------------
# If you see a message about "sum of weights is negative - negative area?" 
# then you need to edit this file:
# components/cam/tools/topo_tool/cube_to_target/remap.F90
# and change the threshold on line 148 to be a more negative number
# changing -1e-9 to 1-e-8 has worked before
#---------------------------------------------------------------------------------------------------
import os
from datetime import datetime
home = os.getenv('HOME')
build,execute,do_step_1,do_step_2,do_step_3 = False,False,False,False,False

# build     = True
execute   = True
# do_step_1 = True   # use cube_to_target to downscale the hi-res topography
# do_step_2 = True   # interpolate from preexisting np4 topo to get 'smoothed' topo
do_step_3 = True   # use cube_to_target to get SGH that are consistent with 'smoothed' topo


grid_name = 'ne120pg2'       # target grid

atm_scrip_file      = home+'/E3SM/data_grid/'+grid_name+'_scrip.nc'
e3sm_root           = home+'/E3SM/E3SM_SRC1'
cube_to_target_root = e3sm_root+'/components/cam/tools/topo_tool/cube_to_target'

# date_stamp = datetime.now().strftime('%Y%m%d')
date_stamp = '20190618'

output_root         = '/global/cscratch1/sd/whannah/acme_scratch/init_files'
input_topo_file     = '/project/projectdirs/acme/inputdata/atm/cam/hrtopo/USGS-topo-cube3000.nc'
output_topo_file1   = output_root+'/USGS_'+grid_name+'_unsmoothed_'+date_stamp+'.nc'
smoothed_topo_file  = output_root+'/USGS_'+grid_name+'_smoothed_'  +date_stamp+'.nc'
output_topo_file2   = output_root+'/USGS_'+grid_name+'_'           +date_stamp+'.nc'

#---------------------------------------------------------------------------------------------------
# Get machine-specific modules
os.system(e3sm_root+'/cime/tools/configure && source $(pwd)/.env_mach_specific.sh')

# Print informative stuff
info_str = '\n'
info_str = info_str+'\n date_stamp          : '+date_stamp
info_str = info_str+'\n e3sm_root           : '+e3sm_root
info_str = info_str+'\n cube_to_target_root : '+cube_to_target_root
info_str = info_str+'\n'
info_str = info_str+'\n atm_scrip_file      : '+atm_scrip_file
info_str = info_str+'\n input_topo_file     : '+input_topo_file
info_str = info_str+'\n smoothed_topo_file  : '+smoothed_topo_file
info_str = info_str+'\n output_topo_file1   : '+output_topo_file1
info_str = info_str+'\n output_topo_file2   : '+output_topo_file2
info_str = info_str+'\n'

print(info_str)

#---------------------------------------------------------------------------------------------------
# build the code for the topography tool
if build:
   os.chdir(cube_to_target_root)
   bld_vars = 'FC=ifort  INC_NETCDF=${NETCDF_DIR}/include  LIB_NETCDF=${NETCDF_DIR}/lib  '
   # bld_vars = 'FC=gfortran  INC_NETCDF=${NETCDF_DIR}/include  LIB_NETCDF=${NETCDF_DIR}/lib  '

   cmd = bld_vars+' make clean '
   print('\n'+cmd+'\n')
   os.system(cmd)

   cmd = bld_vars+' make'
   print('\n'+cmd+'\n')
   os.system(cmd)
   print('Done building cube_to_target.')

#---------------------------------------------------------------------------------------------------
# step #1 - use cube_to_target to downscale the hi-res topography
if do_step_1:
   print('Run cube_to_target to downscale topography...')

   # Create the output directory if it doesn't exist
   cmd = 'mkdir -p `dirname '+output_topo_file1+'`'
   print('\n'+cmd+'\n')
   if execute: os.system(cmd)

   cmd = cube_to_target_root+'/cube_to_target'     \
         +' --target-grid '      +atm_scrip_file   \
         +' --input-topography ' +input_topo_file  \
         +' --output-topography '+output_topo_file1
   print('\n'+cmd+'\n')
   if execute: 
      os.system(cmd)
      print('Done running cube_to_target.')


#---------------------------------------------------------------------------------------------------
# step #2 - interpolate from preexisting np4 topo to get 'smoothed' topo
if do_step_2 :

   src_mesh_file = '~/Tempest/files_exodus/'+grid_name.replace('pg2','')+'.g'
   dst_mesh_file = '~/Tempest/files_exodus/'+grid_name+'.g'

   # input_root  = '/project/projectdirs/acme/inputdata/atm/cam/inic/homme/'
   input_root  = '/global/cscratch1/sd/whannah/acme_scratch/init_files/'
   output_root = '/global/cscratch1/sd/whannah/acme_scratch/init_files/'

   overlap_file = '~/Tempest/files_map/tmp_overlap_mesh.nc'
   mapping_file = '~/Tempest/files_map/tmp_mapping_weights.nc'

   tempest_path = '~/Tempest/tempestgecore/bin/'

   # Generate overlap mesh
   cmd = tempest_path+'GenerateOverlapMesh --a '+src_mesh_file+' --b '+dst_mesh_file+' --out '+overlap_file
   print('\n'+cmd+'\n')
   if execute: os.system(cmd)
     
   # Generate mapping weights
   cmd = tempest_path+'GenerateOfflineMap '
   cmd = cmd+' --in_mesh  '+src_mesh_file
   cmd = cmd+' --out_mesh '+dst_mesh_file
   cmd = cmd+' --ov_mesh '+overlap_file
   # cmd = cmd+' --in_np 4 --out_np 4 --in_type cgll --out_type cgll '
   # cmd = cmd + ' --in_type fv  --in_np 1 '
   cmd = cmd + ' --in_type cgll  --in_np 4 '
   cmd = cmd + ' --out_type fv --out_np 1 '
   cmd = cmd + ' --out_double --mono  '
   # cmd = cmd + ' --volumetric '
   cmd = cmd+'--out_map '+mapping_file
   print('\n'+cmd+'\n')
   if execute: os.system(cmd)
     
   # Apply mapping weights
   if grid_name=='ne30pg2' : src_file = '/project/projectdirs/acme/inputdata/atm/cam/topo/USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc'
   if grid_name=='ne120pg2': src_file = '/project/projectdirs/acme/inputdata/atm/cam/topo/USGS-gtopo30_ne120np4_16xdel2-PFC-consistentSGH.nc'
   dst_file = smoothed_topo_file
   cmd = 'ncremap -4 -m '+mapping_file+' '+src_file+' '+dst_file
   print('\n'+cmd+'\n')
   if execute: os.system(cmd)


#---------------------------------------------------------------------------------------------------
# step #3 - use cube_to_target to get SGH that are consistent with 'smoothed' topo
if do_step_3:
   cmd = cube_to_target_root+'/cube_to_target'        \
         +' --target-grid '        +atm_scrip_file    \
         +' --input-topography '   +input_topo_file   \
         +' --output-topography '  +output_topo_file2 \
         +' --smoothed-topography '+smoothed_topo_file
         # +' --smoothed-topography '+output_topo_file1
   print('\n'+cmd+'\n')
   if execute: 
      os.system(cmd)
      print('Done running cube_to_target.')

#---------------------------------------------------------------------------------------------------
# Print informative stuff again
print(info_str)
#---------------------------------------------------------------------------------------------------