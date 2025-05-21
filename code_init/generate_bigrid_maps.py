#!/usr/bin/env python
import os
import subprocess as sp
home = os.getenv('HOME')

# E3SM unified environment
# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_cori-knl.sh
# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

#-------------------------------------------------------------------------------
# Set scratch path or OLCF (Summit/Rhea)
# if 'SCRATCH' not in os.environ and 'MEMBERWORK' in os.environ : 
#    os.environ['SCRATCH'] = os.environ['MEMBERWORK']+'/cli115'
#    inputdata_root = '/gpfs/alpine/cli115/scratch/hannah6'
# else:
#    inputdata_root = '/project/projectdirs/e3sm'

inputdata_root = '/global/cfs/cdirs/e3sm'
#-------------------------------------------------------------------------------

execute           = True
suppress_output   = False

# Make sure imask is an integer: FILE=ne30pg3_scrip.nc ; ncap2 --ovr -s 'grid_imask=int(grid_imask)' $FILE $FILE

# date_stamp = '200331' 
# date_stamp = '200610' 
# date_stamp = '20200612'
# date_stamp = '20210817'
date_stamp = '20230201'

output_dir = '${SCRATCH}/e3sm_scratch/init_scratch/maps'

print()
print(f'  output_dir: {output_dir}')
print()

#-------------------------------------------------------------------------------
# ATM grid setup
#-------------------------------------------------------------------------------
ne,npg = 16,2

if ne==0:
   if npg==0 : atm_grid_name = 'conusx4v1'
   if npg>0  : atm_grid_name = f'conusx4v1pg{npg}'
else:
   if npg==0 : atm_grid_name = f'ne{ne}'
   if npg>0  : atm_grid_name = f'ne{ne}pg{npg}'

atm_grid_file  = f'{home}/E3SM/data_grid/{atm_grid_name}_scrip.nc'
# atm_exodus_file = f'{home}/E3SM/data_grid/{atm_grid_name}.g'

#-------------------------------------------------------------------------------
# OCN/LND grid setup
#-------------------------------------------------------------------------------
# ocn_grid_name,lnd_grid_name = 'oEC60to30v3','r05'
ocn_grid_name,lnd_grid_name = 'oEC60to30v3',atm_grid_name

e3sm_grid_dir = f'{inputdata_root}/mapping/grids'
mpas_grid_dir = f'{inputdata_root}/inputdata/ocn/mpas-o'
clm_grid_dir  = f'{inputdata_root}/inputdata/lnd/clm2/mappingdata/grids'


if ocn_grid_name=='oQU240':      ocn_grid_file = f'{home}/E3SM/files_scrip/ocean.QU.240km.scrip.151209.nc'
if ocn_grid_name=='gx1v6' :      ocn_grid_file = f'{e3sm_grid_dir}/gx1v6_090205.nc'
if ocn_grid_name=='oEC60to30v3': ocn_grid_file = f'{mpas_grid_dir}/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc'
if ocn_grid_name==atm_grid_name: ocn_grid_file = atm_grid_file

if lnd_grid_name=='r05': lnd_grid_file = f'{clm_grid_dir}/SCRIPgrid_0.5x0.5_nomask_c110308.nc'
if lnd_grid_name==atm_grid_name: lnd_grid_file = atm_grid_file

map_file_list = []
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor: ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
def run_cmd(cmd):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print('\n'+msg+'\n')
   if execute: 
      try:
         sp.check_output(cmd,shell=True,universal_newlines=True)
      except sp.CalledProcessError as error:
         for line in error.output.split('\n'):
            if 'ERROR' in line: line = tcolor.RED + line + tcolor.ENDC
            print(line)
         exit()
   return
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def get_map_name(src_grid, dst_grid, alg_name, map_file_list):
   """ Generate consistent map file names and add to list """
   map_file = f'{output_dir}/map_{src_grid}_to_{dst_grid}_{alg_name}.{date_stamp}.nc'
   map_file_list.append(map_file)
   return map_file
#-------------------------------------------------------------------------------
# Conservative, monotone maps
#-------------------------------------------------------------------------------
alg_name = 'mono'

# ATM to OCN
map_file = get_map_name(atm_grid_name, ocn_grid_name, alg_name, map_file_list)
atm2ocn_map_file = map_file # use for transpose map
cmd  = f'ncremap'
cmd += f' --src_grd={atm_grid_file}'
cmd += f' --dst_grd={ocn_grid_file}'
cmd += f' --map_file={map_file}'
cmd += f' --a2o'
run_cmd(cmd)

# OCN to ATM
map_file = get_map_name(ocn_grid_name, atm_grid_name, alg_name, map_file_list)
cmd  = f'ncremap'
cmd += f' --src_grd={ocn_grid_file}'
cmd += f' --dst_grd={atm_grid_file}'
cmd += f' --map_file={map_file}'
run_cmd(cmd)

#-------------------------------------------------------------------------------
# Nonconservative, monotone maps - use ESMF until TR can do this type of map
#-------------------------------------------------------------------------------
alg_name,alg_flag = 'bilin','bilinear'
wgt_opts = '--extrap_method  nearestidavg'

# ATM to OCN
map_file = get_map_name(atm_grid_name, ocn_grid_name, alg_name, map_file_list)
cmd  = f'ncremap'
cmd += f' -a {alg_flag}'
cmd += f' --src_grd={atm_grid_file}'
cmd += f' --dst_grd={ocn_grid_file}'
cmd += f' --map_file={map_file}'
cmd += f' -W \'{wgt_opts}\' '
run_cmd(cmd)

#-------------------------------------------------------------------------------
# Print list of map files created
#-------------------------------------------------------------------------------
print()
for map_file in map_file_list: print(f'{map_file}')
print()
# print(' '.join(map_file_list))
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------