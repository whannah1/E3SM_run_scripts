#!/bin/bash
#SBATCH --account=e3sm
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=ECOMIP_grid_and_map
#SBATCH --output=/global/homes/w/whannah/E3SM/logs_slurm/ECOMIP_grid_and_map_slurm-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# sbatch ${HOME}/E3SM/batch_scripts/2025_ECOMIP_batch_grid_and_map.sh
#-------------------------------------------------------------------------------

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

# SRC_GRID=/pscratch/sd/w/whannah/HICCUP/test_data_tmp/scrip_IFS_3601x7200.nc
# DST_GRID=/pscratch/sd/w/whannah/HICCUP/test_data_tmp/exodus_ne256.g
# MAP_FILE=/pscratch/sd/w/whannah/HICCUP/test_data_tmp/map_3601x7200_to_ne256np4.nc

SRC_GRID=/pscratch/sd/w/whannah/HICCUP/test_data_tmp/scrip_IFS_3601x7200.nc
DST_GRID=/global/cfs/cdirs/e3sm/whannah/files_grid/ne1024.g
MAP_FILE=/pscratch/sd/w/whannah/HICCUP/test_data_tmp/map_3601x7200_to_ne1024np4.nc

ncremap -a fv2se_flx --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}

#-------------------------------------------------------------------------------