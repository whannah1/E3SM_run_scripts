#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp

ne_list = []
ne_list.append(30)
ne_list.append(45)
ne_list.append(60)
ne_list.append(90)
ne_list.append(120)
ne_list.append(180)
ne_list.append(240)


SCRATCH = os.getenv('SCRATCH')

grid_root    = f'{SCRATCH}/e3sm_scratch/files_grid'
map_root     = f'{SCRATCH}/e3sm_scratch/files_map'
domain_root  = f'{SCRATCH}/e3sm_scratch/files_domain'

src_root = os.getenv('HOME')+f'/E3SM/E3SM_SRC0'
gen_domain = f'{src_root}/tools/generate_domain_files/generate_domain_files_E3SM.py'

#---------------------------------------------------------------------------------------------------
'''
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
'''
#---------------------------------------------------------------------------------------------------
for NE in ne_list:

  date_stamp = '20240607'

  # OCN_GRID = '/global/cfs/cdirs/e3sm/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc'
  # MAP_FILE = f'{map_root}/map_oEC60to30v3_to_ne{NE}pg2_traave.{date_stamp}.nc'

  OCN_GRID = 'oRRS18to6v3'
  OCN_FILE = '/global/cfs/cdirs/e3sm/inputdata/ocn/mpas-o/oRRS18to6v3/ocean.oRRS18to6v3.scrip.181106.nc'
  MAP_FILE = f'{map_root}/map_oRRS18to6v3_to_ne{NE}pg2_traave.{date_stamp}.nc'

  #-----------------------------------------------------------------------------
  # Create grid files

  # run_cmd(f'GenerateCSMesh --alt --res {NE} --file {grid_root}/ne{NE}.g')
  # run_cmd(f'GenerateVolumetricMesh --in {grid_root}/ne{NE}.g --out {grid_root}/ne{NE}pg2.g --np 2 --uniform')
  # run_cmd(f'ConvertMeshToSCRIP --in {grid_root}/ne{NE}pg2.g --out {grid_root}/ne{NE}pg2_scrip.nc')

  #-------------------------------------------------------------------------------
  # Create map files

  ATM_FILE = f'{grid_root}/ne{NE}pg2_scrip.nc'
  run_cmd(f'ncremap -5 -a traave --src_grd={OCN_FILE} --dst_grd={ATM_FILE} --map_file={MAP_FILE}')

  print(f'  {MAP_FILE}')
  if not os.path.exists(f'{MAP_FILE}'): raise FileNotFoundError(f'File does not exist: {MAP_FILE}')

  #-------------------------------------------------------------------------------
  # Create domain files

  run_cmd(f'python {gen_domain} -m {MAP_FILE} -o {OCN_GRID} -l ne{NE}pg2 --date-stamp={date_stamp} --output-root={domain_root}')

  #-------------------------------------------------------------------------------
  # Check that files were created

  file_list = []
  # file_list.append(f'{grid_root}/ne{NE}.g')
  # file_list.append(f'{grid_root}/ne{NE}pg2_scrip.nc')
  # file_list.append(f'{MAP_FILE}')
  file_list.append(f'{domain_root}/domain.lnd.ne{NE}pg2_oEC60to30v3.{date_stamp}.nc')
  file_list.append(f'{domain_root}/domain.ocn.ne{NE}pg2_oEC60to30v3.{date_stamp}.nc')
  print()
  for tfile in file_list:
    print(f'  {tfile}')
    if not os.path.exists(f'{tfile}'): raise FileNotFoundError(f'File does not exist: {tfile}')

#---------------------------------------------------------------------------------------------------
