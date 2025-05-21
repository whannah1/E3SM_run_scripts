#!/usr/bin/env python3
import os
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
grid_opt_list = []
def add_grid( **kwargs ):
  case_opts = {}
  for k, val in kwargs.items(): case_opts[k] = val
  grid_opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------

datestamp = 20240205

# ne=18
ne=22
# ne=26
# ne=30

grid_root = '/global/cfs/cdirs/m4310/whannah/files_grid'
maps_root = '/global/cfs/cdirs/m4310/whannah/files_fsurdat'

dst_grid_name = f'ne{ne}pg2'
dst_grid_file = f'{grid_root}/{dst_grid_name}_scrip.nc'

#---------------------------------------------------------------------------------------------------
# build list of source grids

src_grid_root='/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids'

add_grid(id='00', name='0.5x0.5_AVHRR',                       file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_AVHRR_c110228.nc' )
add_grid(id='01', name='0.5x0.5_MODIS',                       file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_MODIS_c110228.nc' )
add_grid(id='02', name='3minx3min_LandScan2004',              file=f'{src_grid_root}/SCRIPgrid_3minx3min_LandScan2004_c120517.nc' )
add_grid(id='03', name='3minx3min_MODIS',                     file=f'{src_grid_root}/SCRIPgrid_3minx3min_MODIS_c110915.nc' )
add_grid(id='04', name='3x3_USGS',                            file=f'{src_grid_root}/SCRIPgrid_3x3_USGS_c120912.nc' )
add_grid(id='05', name='5x5min_nomask',                       file=f'{src_grid_root}/SCRIPgrid_5x5min_nomask_c110530.nc' )
add_grid(id='06', name='5x5min_IGBP-GSDP',                    file=f'{src_grid_root}/SCRIPgrid_5x5min_IGBP-GSDP_c110228.nc' )
add_grid(id='07', name='5x5min_ISRIC-WISE',                   file=f'{src_grid_root}/SCRIPgrid_5x5min_ISRIC-WISE_c111114.nc' )
add_grid(id='08', name='10x10min_nomask',                     file=f'{src_grid_root}/SCRIPgrid_10x10min_nomask_c110228.nc' )
add_grid(id='09', name='10x10min_IGBPmergeICESatGIS',         file=f'{src_grid_root}/SCRIPgrid_10x10min_IGBPmergeICESatGIS_c110818.nc' )
add_grid(id='10', name='3minx3min_GLOBE-Gardner',             file=f'{src_grid_root}/SCRIPgrid_3minx3min_GLOBE-Gardner_c120922.nc' )
add_grid(id='11', name='3minx3min_GLOBE-Gardner-mergeGIS',    file=f'{src_grid_root}/SCRIPgrid_3minx3min_GLOBE-Gardner-mergeGIS_c120922.nc' )
add_grid(id='12', name='0.9x1.25_GRDC',                       file=f'{src_grid_root}/SCRIPgrid_0.9x1.25_GRDC_c130307.nc' )
add_grid(id='13', name='360x720_cruncep',                     file=f'{src_grid_root}/SCRIPgrid_360x720_cruncep_c120830.nc' )
add_grid(id='14', name='1km-merge-10min_HYDRO1K-merge-nomask',file=f'{src_grid_root}/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc' )
add_grid(id='15', name='0.5x0.5_GSDTG2000',                   file=f'{src_grid_root}/SCRIPgrid_0.5x0.5_GSDTG2000_c240125.nc' )
add_grid(id='16', name='0.1x0.1_nomask',                      file=f'{src_grid_root}/SCRIPgrid_0.1x0.1_nomask_c110712.nc' )

#---------------------------------------------------------------------------------------------------
# loop through source grids and build a batch script to create the map
for n,opts in enumerate(grid_opt_list):
  src_grid_id   = opts['id']
  src_grid_name = opts['name']
  src_grid_file = opts['file']

  map_file = f'{maps_root}/map_{src_grid_name}_to_{dst_grid_name}_nomask_aave_da_{datestamp}.nc'
  map_opts = f'-m conserve --ignore_unmapped --src_type SCRIP --dst_type SCRIP --64bit_offset'

  #-----------------------------------------------------------------------------
  # setup text for batch script
  batch_script_path = f'{maps_root}/generate_fsurdat_map_ne{ne}_{src_grid_id}.sh'
  batch_script_text = f'''#!/bin/sh
#SBATCH --account=m4310
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
srun --ntasks=64 ESMF_RegridWeightGen {map_opts} -s {src_grid_file} -d {dst_grid_file}  -w {map_file} 
'''
  #-----------------------------------------------------------------------------
  # Write the batch script
  file = open(batch_script_path,'w')
  file.write(batch_script_text)
  file.close()
  # Submit the batch script
  run_cmd(f'sbatch  --job-name=generate_fsurdat_map_ne{ne}_{src_grid_id}  {batch_script_path}')

#---------------------------------------------------------------------------------------------------

'''
# original command from Gautam - reformatted to aide in converting to python

GRID_ROOT=/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids

==> map_01.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_AVHRR_c110228.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_AVHRR_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_02.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_MODIS_c110228.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_MODIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_03.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_LandScan2004_c120517.nc           -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_LandScan2004_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                  --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_04.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_MODIS_c110915.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_MODIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                         --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_05.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3x3_USGS_c120912.nc                         -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_USGS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                          --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_06.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_nomask_c110530.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_07.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_IGBP-GSDP_c110228.nc                 -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_IGBP-GSDP_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                     --src_type SCRIP --dst_type SCRIP
==> map_08.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_ISRIC-WISE_c111114.nc                -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_ISRIC-WISE_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                    --src_type SCRIP --dst_type SCRIP
==> map_09.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_10x10min_nomask_c110228.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_10x10min_nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                      --src_type SCRIP --dst_type SCRIP
==> map_10.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_10x10min_IGBPmergeICESatGIS_c110818.nc      -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_10x10min_IGBPmergeICESatGIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc          --src_type SCRIP --dst_type SCRIP
==> map_11.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_GLOBE-Gardner_c120922.nc          -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_GLOBE-Gardner_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                 --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_12.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_GLOBE-Gardner-mergeGIS_c120922.nc -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_GLOBE-Gardner-mergeGIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc        --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_13.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.9x1.25_GRDC_c130307.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.9x1.25_GRDC_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_14.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_360x720_cruncep_c120830.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_360x720_cruncep_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                      --src_type SCRIP --dst_type SCRIP
==> map_15.run <== srun -n 40 -c 256 ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/UGRID_1km-merge-10min_HYDRO1K-merge-nomask_c130402.nc -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_1km-merge-10min_HYDRO1K-merge-nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc --src_type UGRID --dst_type SCRIP --src_meshname landmesh --64bit_offset
==> map_16.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_GSDTG2000_c240125.nc                -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_GSDTG2000_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                    --src_type SCRIP --dst_type SCRIP
==> map_17.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.1x0.1_nomask_c110712.nc                   -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.1x0.1_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                              --src_type SCRIP --dst_type SCRIP
'''