#!/bin/bash
#SBATCH --constraint=cpu
#SBATCH --account=m3312
#SBATCH -q regular
#SBATCH --job-name=generate_map
#SBATCH --output=~/E3SM/logs_slurm/slurm-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL

# To run this batch script, use the command below
# sbatch ~/E3SM/batch_generate_map.nersc.sh

# NE=16 ; sbatch --job-name=gen_topo_map_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_map_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_create_map.nersc.sh
# NE=24 ; sbatch --job-name=gen_topo_map_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_map_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_create_map.nersc.sh
# NE=70 ; sbatch --job-name=gen_topo_map_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_map_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_create_map.nersc.sh

# Load the python environment
source activate hiccup_env
# source activate hiccup_env_moab

# NE=16
DATA_FILE_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_topo
GRID_FILE_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid
MAP_FILE_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_map

SRC_GRID=${GRID_FILE_ROOT}/scrip_ne3000pg1.nc
DST_GRID=${GRID_FILE_ROOT}/exodus_ne${NE}.g
MAP_FILE=${MAP_FILE_ROOT}/map_ne3000pg1_to_ne${NE}np4.nc

# ncremap --debug_level=3 --mpi_nbr=32 -a fv2se_flx --fl_fmt=64bit_data --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}
ncremap -a fv2se_flx --fl_fmt=64bit_data --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}

echo
echo map file: ${MAP_FILE}
echo