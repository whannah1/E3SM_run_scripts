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

allocation = 'm4310'
datestamp  = 20240205

# ne=18
# ne=22
ne=26
# ne=30

grid_root  = '/global/cfs/cdirs/m4310/whannah/files_grid'
maps_root  = '/global/cfs/cdirs/m4310/whannah/files_fsurdat/files_map'
batch_root = '/global/cfs/cdirs/m4310/whannah/files_fsurdat/files_batch'

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
# add_grid(id='00', name='0.5x0.5_AVHRR',                       file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_AVHRR_c110228.nc' )
# add_grid(id='01', name='0.5x0.5_MODIS',                       file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_MODIS_c110228.nc' )
# add_grid(id='02', name='3minx3min_LandScan2004',              file=f'{src_grid_root}/SCRIPgrid_3minx3min_LandScan2004_c120517.nc' )
# add_grid(id='03', name='3minx3min_MODIS',                     file=f'{src_grid_root}/SCRIPgrid_3minx3min_MODIS_c110915.nc' )
# add_grid(id='04', name='3x3_USGS',                            file=f'{src_grid_root}/SCRIPgrid_3x3_USGS_c120912.nc' )
# add_grid(id='05', name='5x5min_nomask',                       file=f'{src_grid_root}/SCRIPgrid_5x5min_nomask_c110530.nc' )
# add_grid(id='06', name='5x5min_IGBP-GSDP',                    file=f'{src_grid_root}/SCRIPgrid_5x5min_IGBP-GSDP_c110228.nc' )
# add_grid(id='07', name='5x5min_ISRIC-WISE',                   file=f'{src_grid_root}/SCRIPgrid_5x5min_ISRIC-WISE_c111114.nc' )
# add_grid(id='08', name='10x10min_nomask',                     file=f'{src_grid_root}/SCRIPgrid_10x10min_nomask_c110228.nc' )
# add_grid(id='09', name='10x10min_IGBPmergeICESatGIS',         file=f'{src_grid_root}/SCRIPgrid_10x10min_IGBPmergeICESatGIS_c110818.nc' )
# add_grid(id='10', name='3minx3min_GLOBE-Gardner',             file=f'{src_grid_root}/SCRIPgrid_3minx3min_GLOBE-Gardner_c120922.nc' )
# add_grid(id='11', name='3minx3min_GLOBE-Gardner-mergeGIS',    file=f'{src_grid_root}/SCRIPgrid_3minx3min_GLOBE-Gardner-mergeGIS_c120922.nc' )
# add_grid(id='12', name='0.9x1.25_GRDC',                       file=f'{src_grid_root}/SCRIPgrid_0.9x1.25_GRDC_c130307.nc' )
# add_grid(id='13', name='360x720_cruncep',                     file=f'{src_grid_root}/SCRIPgrid_360x720_cruncep_c120830.nc' )
add_grid(id='14', name='1km-merge-10min_HYDRO1K-merge-nomask',file=f'{src_grid_root}/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc', num_nodes=20, num_tasks_per_node=1 )
# add_grid(id='15', name='0.5x0.5_GSDTG2000',                   file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_GSDTG2000_c240125.nc' )
# add_grid(id='16', name='0.1x0.1_nomask',                      file=f'{src_grid_root}/SCRIPgrid_0.1x0.1_nomask_c110712.nc' )
add_grid(id='17', name='0.01x0.01_nomask',                    file=f'{src_grid_root}/SCRIPgrid_0.01x0.01_nomask_c250510.nc', num_nodes=20, num_tasks_per_node=1 )


#---------------------------------------------------------------------------------------------------
def get_batch_script_text(map_opts,src_grid_file,dst_grid_file,map_file,num_nodes=1,num_tasks_per_node=32):
  global allocation
  num_tasks = num_nodes*num_tasks_per_node
  return f'''#!/bin/sh
#SBATCH --account={allocation}
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=08:00:00
#SBATCH --nodes={num_nodes}
#SBATCH --mail-type=END,FAIL
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
srun --ntasks={num_tasks} ESMF_RegridWeightGen {map_opts} -s {src_grid_file} -d {dst_grid_file}  -w {map_file} 
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
  batch_script_path = f'{batch_root}/generate_fsurdat_map_ne{ne}_{src_grid_id}.sh'
  file = open(batch_script_path,'w')
  num_nodes = opts['num_nodes'] if 'num_nodes' in opts else 1
  file.write(get_batch_script_text(map_opts,src_grid_file,dst_grid_file,map_file,num_nodes=num_nodes))
  file.close()
  #-----------------------------------------------------------------------------
  # Submit the batch script
  run_cmd(f'sbatch  --job-name=generate_fsurdat_map_ne{ne}_{src_grid_id}  {batch_script_path}')

#---------------------------------------------------------------------------------------------------
