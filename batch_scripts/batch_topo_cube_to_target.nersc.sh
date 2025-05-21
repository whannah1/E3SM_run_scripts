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

# NE=16 ; sbatch --job-name=gen_topo_cube_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_cube_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_cube_to_target.nersc.sh
# NE=24 ; sbatch --job-name=gen_topo_cube_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_cube_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_cube_to_target.nersc.sh
# NE=70 ; sbatch --job-name=gen_topo_cube_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_cube_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_cube_to_target.nersc.sh

# Load the python environment
# source activate hiccup_env
# source activate hiccup_env_moab
#-------------------------------------------------------------------------------
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m3312
#-------------------------------------------------------------------------------

# NE=16

cd /global/cfs/projectdirs/m3312/whannah/HICCUP

e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC4
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh


HICCUP_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP
DATA_FILE_ROOT=${HICCUP_ROOT}/files_topo
GRID_FILE_ROOT=${HICCUP_ROOT}/files_grid
DST_GRID_PG2=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc
SRC_TOPO_FILE=/global/cfs/cdirs/e3sm/inputdata/atm/cam/hrtopo/USGS-topo-cube3000.nc

TOPO_FILE_0=${DATA_FILE_ROOT}/USGS-topo_${NE}np4.nc
TOPO_FILE_1=${DATA_FILE_ROOT}/USGS-topo_${NE}np4_phis.nc
TOPO_FILE_2=${DATA_FILE_ROOT}/USGS-topo_${NE}np4_phis_x6t_tmp1.nc
TOPO_FILE_3=${DATA_FILE_ROOT}/USGS-topo_${NE}np4_smoothed_x6tensor.nc



${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${DST_GRID_PG2} \
  --input-topography ${SRC_TOPO_FILE} \
  --smoothed-topography ${TOPO_FILE_2} \
  --output-topography ${TOPO_FILE_3}

echo
echo NE           : $NE
echo DST_GRID_PG2 : $DST_GRID_PG2
echo TOPO_FILE_0  : $TOPO_FILE_0
echo TOPO_FILE_1  : $TOPO_FILE_1
echo TOPO_FILE_2  : $TOPO_FILE_2
echo TOPO_FILE_3  : $TOPO_FILE_3
echo