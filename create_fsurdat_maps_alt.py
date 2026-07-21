#!/usr/bin/env python3
import os
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
# usage = '''
# python create_fsurdat_maps.py --grid_root     <grid_root> 
#                               --dst_grid_name <dst_grid_name>
#                               --dst_grid_file <dst_grid_file>
#                               --datestamp     <datestamp>
#                               --batch_acct    <batch_acct>
# Purpose:
#   This script reads a HOMME grid template file and writes out a SCRIP format grid description file of the np4/GLL grid.
  
#   HOMME np4 grid template files are produced by a two step procedure, which first requires running homme_tool, and then this script to convert the output into SCRIP format. This procedure is only needed for np4 files due to their use of vertex data. For cell centered pg2 files, one should instead use TempestRemap to create a grid description file. This is particularly useful when remapping topography data with cube_to_target, which can be much faster than remapping with tools like NCO due to the large size of the input topography data.
# Environment
  
#   This requires libraries such as xarray, which included in the E3SM unified environment:
#   https://e3sm.org/resources/tools/other-tools/e3sm-unified-environment/
#   Otherwise a simple conda environment can be created:
#   conda create --name example_env --channel conda-forge xarray numpy netcdf4
# '''
# from optparse import OptionParser
# parser = OptionParser(usage=usage)
# parser.add_option('--src_file',dest='src_file',default=None,help='Input HOMME grid template file')
# parser.add_option('--dst_file',dest='dst_file',default=None,help='Output scrip grid file')
# (opts, args) = parser.parse_args()
#---------------------------------------------------------------------------------------------------
# Make sure E3SM unified env is activated
E3SMU_SCRIPT = os.getenv('E3SMU_SCRIPT')
if E3SMU_SCRIPT is None:
  raise ValueError('ERROR - This tool requires the E3SM unified environement to active')
#---------------------------------------------------------------------------------------------------

allocation = 'm4310'
datestamp  = 20240205

# ne=18
# ne=22
# ne=26
ne=30

grid_root = '/global/cfs/cdirs/m4310/whannah/files_grid'
maps_root = '/global/cfs/cdirs/m4310/whannah/files_fsurdat'

src_grid_root='/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids'

dst_grid_name = f'ne{ne}pg2'
dst_grid_file = f'{grid_root}/{dst_grid_name}_scrip.nc'

#---------------------------------------------------------------------------------------------------
grid_opt_list = []
def add_grid( **kwargs ):
  case_opts = {}
  for k, val in kwargs.items(): case_opts[k] = val
  grid_opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
# build list of source grids
add_grid(id='00', name='0.5x0.5_AVHRR')
add_grid(id='01', name='0.5x0.5_MODIS')
add_grid(id='02', name='3minx3min_LandScan2004')
add_grid(id='03', name='3minx3min_MODIS')
add_grid(id='04', name='3x3_USGS')
add_grid(id='05', name='5x5min_nomask')
add_grid(id='06', name='5x5min_IGBP-GSDP')
add_grid(id='07', name='5x5min_ISRIC-WISE')
add_grid(id='08', name='10x10min_nomask')
add_grid(id='09', name='10x10min_IGBPmergeICESatGIS')
add_grid(id='10', name='3minx3min_GLOBE-Gardner')
add_grid(id='11', name='3minx3min_GLOBE-Gardner-mergeGIS')
add_grid(id='12', name='0.9x1.25_GRDC')
add_grid(id='13', name='360x720_cruncep')
add_grid(id='14', name='1km-merge-10min_HYDRO1K-merge-nomask')
add_grid(id='15', name='0.5x0.5_GSDTG2000')
add_grid(id='16', name='0.1x0.1_nomask')
add_grid(id='17', name='0.01x0.01_nomask')

#---------------------------------------------------------------------------------------------------
def get_host():
  host = None
  if os.path.exists('/global/cfs'): host = 'nersc'
  if os.path.exists('/lcrc')      : host = 'lcrc'
  if host is None: raise ValueError('ERROR: supported host not found')
  return host
#---------------------------------------------------------------------------------------------------
def get_unified_source():
  host = get_host()
  unified_source = None
  if host=='nersc': unified_source = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
  if host=='lcrc' : unified_source = '/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh'
  if unified_source is None: raise ValueError('ERROR: path for E3SM unified environment not found')
  return unified_source
#---------------------------------------------------------------------------------------------------
def get_batch_script_text( map_opts, src_grid_file, dst_grid_file, map_file ):
  global allocation
  return f'''#!/bin/sh
#SBATCH --account={allocation}
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
source {get_unified_source()}
srun --ntasks=64 ESMF_RegridWeightGen {map_opts} -s {src_grid_file} -d {dst_grid_file}  -w {map_file} 
'''
#---------------------------------------------------------------------------------------------------
# loop through source grids and build a batch script to create the map
for n,opts in enumerate(grid_opt_list):
  src_grid_id   = opts['id']
  src_grid_name = opts['name']
  src_grid_file = opts['file']

  map_file = f'{maps_root}/map_{src_grid_name}_to_{dst_grid_name}_nomask_aave_da_{datestamp}.nc'
  map_opts = f'-m conserve --ignore_unmapped --src_type SCRIP --dst_type SCRIP --64bit_offset'

  #-----------------------------------------------------------------------------
  # Write the batch script
  batch_script_path = f'{maps_root}/generate_fsurdat_map_ne{ne}_{src_grid_id}.sh'
  file = open(batch_script_path,'w')
  file.write(get_batch_script_text(map_opts,src_grid_file,dst_grid_file,map_file))
  file.close()
  #-----------------------------------------------------------------------------
  # Submit the batch script
  run_cmd(f'sbatch  --job-name=generate_fsurdat_map_ne{ne}_{src_grid_id}  {batch_script_path}')

#---------------------------------------------------------------------------------------------------
