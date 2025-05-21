#!/usr/bin/env python
import os, subprocess as sp
home = os.getenv('HOME')
#-------------------------------------------------------------------------------
'''
Command sto create input grid files
NE=256
GenerateCSMesh --alt --res ${NE} --file ne${NE}.g
GenerateVolumetricMesh --in ne${NE}.g --out ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ne${NE}pg2.g --out ne${NE}pg2_scrip.nc

OLD COMMAND => ConvertExodusToSCRIP --in ne${NE}pg2.g --out ne${NE}pg2_scrip.nc

FILE=????
ncap2 -s 'grid_imask=int(grid_imask)' $FILE $FILE
'''
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

create_map_atm2ocn = False
create_map_atm2lnd = True
create_map_ocn2atm = False
create_map_lnd2atm = True

# Make sure imask is an integer: FILE=ne30pg3_scrip.nc ; ncap2 --ovr -s 'grid_imask=int(grid_imask)' $FILE $FILE

# date_stamp = '200331' 
# date_stamp = '200610' 
# date_stamp = '20200612'
# date_stamp = '20210817'
# date_stamp = '20230201'
date_stamp = '20230216'

output_dir = '${SCRATCH}/e3sm_scratch/init_scratch/maps'

print()
print(f'  output_dir: {output_dir}')
print()

#-------------------------------------------------------------------------------
# ATM grid setup
#-------------------------------------------------------------------------------
# ne,npg = 30,2
ne,npg = 256,2; use_a2o=True
# ne,npg = 0,2

if ne==0:
   if npg==0 : atm_grid_name = 'conusx4v1'
   if npg>0  : atm_grid_name = f'conusx4v1pg{npg}'
else:
   if npg==0 : atm_grid_name = f'ne{ne}'
   if npg>0  : atm_grid_name = f'ne{ne}pg{npg}'

atm_scrip_file  = f'{home}/E3SM/data_grid/{atm_grid_name}_scrip.nc'
atm_exodus_file = f'{home}/E3SM/data_grid/{atm_grid_name}.g'

#-------------------------------------------------------------------------------
# OCN/LND grid setup
#-------------------------------------------------------------------------------
ocn_grid_name,lnd_grid_name = atm_grid_name,'r0125'
# ocn_grid_name,lnd_grid_name = 'oEC60to30v3','r05'
# ocn_grid_name,lnd_grid_name = 'oEC60to30v3',atm_grid_name

e3sm_grid_dir = f'{inputdata_root}/mapping/grids'
mpas_grid_dir = f'{inputdata_root}/inputdata/ocn/mpas-o'
clm_grid_dir  = f'{inputdata_root}/inputdata/lnd/clm2/mappingdata/grids'


if ocn_grid_name=='oQU240':      ocn_grid_file = f'{home}/E3SM/files_scrip/ocean.QU.240km.scrip.151209.nc'
if ocn_grid_name=='gx1v6' :      ocn_grid_file = f'{e3sm_grid_dir}/gx1v6_090205.nc'
if ocn_grid_name=='oEC60to30v3': ocn_grid_file = f'{mpas_grid_dir}/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc'
if ocn_grid_name==atm_grid_name: ocn_grid_file = atm_scrip_file

if lnd_grid_name=='r05':  lnd_grid_file = f'{clm_grid_dir}/SCRIPgrid_0.5x0.5_nomask_c110308.nc'
if lnd_grid_name=='r0125':lnd_grid_file = f'{clm_grid_dir}/SCRIPgrid_0.125x0.125_nomask_c170126.nc'
if lnd_grid_name==atm_grid_name: lnd_grid_file = atm_scrip_file

ocn_grid_name = atm_grid_name
ocn_grid_file = atm_scrip_file

map_file_list = []
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
def run_cmd(cmd):
   """ consistent run command with colored terminal output """
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
alg_name,alg_flag = 'mono','tempest'

if 'use_a2o'not in locals(): use_a2o = False

if npg==0: wgt_opts = '--in_type cgll --in_np 4'
if npg >0: wgt_opts = '--in_type fv --in_np 1'
wgt_opts += ' --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
#------------------
# ATM to OCN
if create_map_atm2ocn:
   map_file = get_map_name(atm_grid_name, ocn_grid_name, alg_name, map_file_list)
   atm2ocn_map_file = map_file # use for transpose map
   cmd  = f'ncremap -a {alg_flag}'
   cmd += f' --src_grd={atm_exodus_file} --dst_grd={ocn_grid_file}'
   cmd += f' --map_file={map_file} --wgt_opt=\'{wgt_opts}\' '
   cmd += f' --a2o'
   run_cmd(cmd)

#------------------
# ATM to LND
if create_map_atm2lnd:
   map_file = get_map_name(atm_grid_name, lnd_grid_name, alg_name, map_file_list)
   atm2lnd_map_file = map_file # use for transpose map
   cmd  = f'ncremap -a {alg_flag}'
   cmd += f' --src_grd={atm_exodus_file} --dst_grd={lnd_grid_file}'
   cmd += f' --map_file={map_file} --wgt_opt=\'{wgt_opts}\''
   if use_a2o: cmd += f' --a2o'
   run_cmd(cmd)

# For np4 grids - use the transpose of the SE>FV map
if npg==0:

   alg_name = 'monotr'

   #------------------
   # OCN to ATM
   if create_map_ocn2atm:
      if ocn_grid_name!=atm_grid_name:
         map_file = get_map_name(ocn_grid_name, atm_grid_name, alg_name, map_file_list)
         run_cmd(f'GenerateTransposeMap --in {atm2ocn_map_file} --out {map_file}')

   #------------------
   # LND to ATM
   map_file = get_map_name(lnd_grid_name,atm_grid_name,alg_name,map_file_list)
   run_cmd(f'GenerateTransposeMap --in {atm2lnd_map_file} --out {map_file}')

# for physgrid cases - FV>FV arguments stay the same
else:

   #------------------
   # OCN to ATM
   if create_map_ocn2atm:
      if ocn_grid_name!=atm_grid_name:
         map_file = get_map_name(ocn_grid_name, atm_grid_name, alg_name, map_file_list)
         cmd  = f'ncremap -a {alg_flag}'
         cmd += f' --src_grd={ocn_grid_file} --dst_grd={atm_exodus_file}'
         cmd += f' --map_file={map_file} --wgt_opt=\'{wgt_opts}\''
         run_cmd(cmd)

   #------------------
   # LND to ATM
   if create_map_lnd2atm:
      map_file = get_map_name(lnd_grid_name, atm_grid_name, alg_name, map_file_list)
      cmd  = f'ncremap -a {alg_flag}'
      cmd += f' --src_grd={lnd_grid_file} --dst_grd={atm_exodus_file}'
      cmd += f' --map_file={map_file} --wgt_opt=\'{wgt_opts}\''
      run_cmd(cmd)

#-------------------------------------------------------------------------------
# Nonconservative, monotone maps - use ESMF until TR can do this type of map
#-------------------------------------------------------------------------------
alg_name,alg_flag = 'bilin','bilinear'
wgt_opts = '--extrap_method  nearestidavg'

#------------------
# ATM to LND
if create_map_atm2lnd:
   map_file = get_map_name(atm_grid_name, lnd_grid_name, alg_name, map_file_list)
   cmd  = f'ncremap -a {alg_flag}'
   cmd += f' --src_grd={atm_scrip_file} --dst_grd={lnd_grid_file}'
   cmd += f' --map_file={map_file} -W \'{wgt_opts}\' '
   run_cmd(cmd)

#------------------
# ATM to OCN
if create_map_atm2ocn:
   if ocn_grid_name!=atm_grid_name:
      map_file = get_map_name(atm_grid_name, ocn_grid_name, alg_name, map_file_list)
      cmd  = f'ncremap -a {alg_flag}'
      cmd += f' --src_grd={atm_scrip_file } --dst_grd={ocn_grid_file}'
      cmd += f' --map_file={map_file} -W \'{wgt_opts}\' '
      run_cmd(cmd)

#------------------
# LND to ATM
if create_map_atm2lnd:
   map_file = get_map_name(lnd_grid_name, atm_grid_name, alg_name, map_file_list)
   cmd  = f'ncremap -a {alg_flag}'
   cmd += f' --src_grd={lnd_grid_file } --dst_grd={atm_scrip_file}'
   cmd += f' --map_file={map_file} -W \'{wgt_opts}\' '
   run_cmd(cmd)

#-------------------------------------------------------------------------------
# Print list of map files created
#-------------------------------------------------------------------------------
for map_file in map_file_list: print(f'{map_file}')
print()
print(' '.join(map_file_list))
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------