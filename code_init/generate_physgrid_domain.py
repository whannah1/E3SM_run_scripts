#!/usr/bin/env python3
import os, subprocess as sp
create_grid, create_maps, create_domain, suppress_output = False, False, False, False
#-------------------------------------------------------------------------------
# Command to generate pg2 grid file:
'''
NE_DST=128 ; GenerateCSMesh --alt --res ${NE_DST} --file ~/HICCUP/data_scratch/files_grid/exodus_ne${NE_DST}.g; GenerateVolumetricMesh --in ~/HICCUP/data_scratch/files_grid/exodus_ne${NE_DST}.g --out ~/HICCUP/data_scratch/files_grid/exodus_ne${NE_DST}pg2.g --np 2 --uniform ; ConvertExodusToSCRIP --in ~/HICCUP/data_scratch/files_grid/exodus_ne${NE_DST}pg2.g --out ~/HICCUP/data_scratch/files_grid/scrip_ne${NE_DST}pg2.nc
'''
#-------------------------------------------------------------------------------

inputdata_root = '/global/cfs/cdirs/e3sm'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC3'

# create_grid       = True
create_maps       = True
create_domain     = True


# ne,npg =   8,2
# ne,npg =  16,2
# ne,npg =  32,2
# ne,npg =  64,2
ne,npg = 128,2
# ne,npg = 256,2

if npg==0 : atm_grid_name = f'ne{ne}'
if npg>0  : atm_grid_name = f'ne{ne}pg{npg}'
# atm_grid_file = os.getenv('HOME')+f'/Tempest/files_exodus/{atm_grid_name}.g'
# atm_grid_file = os.getenv('HOME')+f'/HICCUP/data_scratch/files_grid/exodus_{atm_grid_name}.g'
atm_grid_file = os.getenv('HOME')+f'/HICCUP/data_scratch/files_grid/scrip_{atm_grid_name}.nc'


# ne,npg=0,2;atm_grid_name='RRM_cubeface_grad_ne30x3'; atm_grid_file=f'$HOME/E3SM/data_grid/{atm_grid_name}pg{npg}_scrip.nc'


ocn_grid_name = atm_grid_name
# ocn_grid_name = 'oQU240'
# ocn_grid_name = 'oEC60to30v3'
# ocn_grid_name = 'oRRS15to5'
# ocn_grid_name = 'oRRS18to6v3'

#-------------------------------------------------------------------------------
if ocn_grid_name == atm_grid_name : ocn_grid_file = atm_grid_file
if ocn_grid_name == 'oQU240': ocn_grid_file = 'files_scrip/ocean.QU.240km.scrip.151209.nc'
if ocn_grid_name == 'oEC60to30v3': ocn_grid_file = f'{inputdata_root}/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc'
if ocn_grid_name == 'oRRS15to5'  : ocn_grid_file = f'{inputdata_root}/inputdata/ocn/mpas-o/oRRS15to5/ocean.RRS.15-5km_scrip_151209.nc'
if ocn_grid_name == 'oRRS18to6v3': ocn_grid_file = f'{inputdata_root}/inputdata/ocn/mpas-o/oRRS18to6v3/ocean.oRRS18to6v3.scrip.181106.nc'
#-------------------------------------------------------------------------------
# mapping_dir   = os.getenv('SCRATCH')+'/Tempest/files_maps'
mapping_dir = '/global/cfs/projectdirs/m3312/whannah/HICCUP/files_map'

if npg>0 : output_map    = mapping_dir+f'/map_{ocn_grid_name}_to_{atm_grid_name}_monotr.nc'

#-------------------------------------------------------------------------------
# clean shit up first
os.system(f'rm {output_map}')
#-------------------------------------------------------------------------------
# Define run command and terminal colors
class tcolor: ENDC,RED,GREEN = '\033[0m','\033[31m','\033[32m'
def run_cmd(cmd):
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print('\n'+msg+'\n')
   try:
      output = sp.check_output(cmd,shell=True,universal_newlines=True)
      for line in output.split('\n'):
         if 'EXCEPTION' in line: line = tcolor.RED + line + tcolor.ENDC
         print(line)
      if 'EXCEPTION' in output: exit()
   except sp.CalledProcessError as error:
      for line in error.output.split('\n'):
         if 'ERROR' in line: line = tcolor.RED + line + tcolor.ENDC
         print(line)
      exit()
   return
#-------------------------------------------------------------------------------
# Create exodus file

# if create_grid and ne>0 :
#    cmd = f'GenerateCSMesh --alt --res {ne} --file {atm_grid_file}'
#    run_cmd(cmd)

#-------------------------------------------------------------------------------
if create_maps :

   # if npg>0 : run_cmd(f'ncap2 -s \'grid_imask=int(grid_imask)\' {atm_grid_file} {atm_grid_file}')

   cmd = 'ncremap'
   cmd += f' --src_grd={ocn_grid_file}'
   cmd += f' --dst_grd={atm_grid_file}'
   cmd += f' --map_file={output_map}'
   # if ne==0: cmd += ' --a2o'
   # cmd += ' --a2o'
   if npg>0 :
      cmd +=' -a tempest --wgt_opt=\'--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic \' '
      # cmd +=' --wgt_opt=\'--in_type fv --in_np 2 --out_type fv --out_np 2 --out_double --mono --volumetric \' '
   if npg<=0 :
      cmd +=' -a tempest --wgt_opt=\'--in_type cgll --in_np 4 --out_type fv --out_np 1 --out_double \' '
   run_cmd(cmd)

#-------------------------------------------------------------------------------
if create_domain :
   fminval = 0.001 # default
   # if ne==30 and npg==2 : fminval = 1.
   cmd = f'{src_dir}/cime/tools/mapping/gen_domain_files/gen_domain'
   cmd = cmd + ' -m '+output_map
   cmd = cmd + ' -o '+ocn_grid_name
   cmd = cmd + ' -l '+atm_grid_name
   cmd = cmd + ' --fminval '+str(fminval)
   run_cmd(cmd)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
