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

# NE=16 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh
# NE=24 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh
# NE=30 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh
# NE=60 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh
# NE=70 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh
# NE=72 ; sbatch --job-name=gen_topo_all_ne$NE --output=${HOME}/E3SM/logs_slurm/gen_topo_all_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_all_steps.nersc.sh

# Load the python environment
# source activate hiccup_env
# source activate hiccup_env_moab
#-------------------------------------------------------------------------------
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m3312
#-------------------------------------------------------------------------------

# NE=16

# Load env to get NCO
source activate hiccup_env

cd /global/cfs/projectdirs/m3312/whannah/HICCUP

e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC4
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh

HICCUP_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP
DATA_FILE_ROOT=${HICCUP_ROOT}/files_topo
GRID_FILE_ROOT=${HICCUP_ROOT}/files_grid
MAP_FILE_ROOT=${HICCUP_ROOT}/files_map

DST_GRID_PG2=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc
SRC_TOPO_FILE=/global/cfs/cdirs/e3sm/inputdata/atm/cam/hrtopo/USGS-topo-cube3000.nc

TOPO_FILE_0=${DATA_FILE_ROOT}/USGS-topo_ne${NE}np4.nc
TOPO_FILE_1=${DATA_FILE_ROOT}/USGS-topo_ne${NE}np4_phis.nc
TOPO_FILE_2=${DATA_FILE_ROOT}/USGS-topo_ne${NE}np4_phis_x6t_tmp
TOPO_FILE_3=${DATA_FILE_ROOT}/USGS-topo_ne${NE}np4_smoothed_x6tensor.nc

SRC_GRID=${GRID_FILE_ROOT}/scrip_ne3000pg1.nc
DST_GRID=${GRID_FILE_ROOT}/exodus_ne${NE}.g
MAP_FILE=${MAP_FILE_ROOT}/map_ne3000pg1_to_ne${NE}np4.nc


set -v

# #-------------------------------------------------------------------------------
# echo
# echo Creating ne3000 grid file...
# echo
# GenerateCSMesh --alt --res 3000  --file ne3000.g
# ConvertExodusToSCRIP --in ne3000.g  --out ne3000pg1.scrip.nc 

#-------------------------------------------------------------------------------
echo
echo Creating ne${NE} grid file...
echo
GenerateCSMesh --alt --res ${NE} --file ${GRID_FILE_ROOT}/exodus_ne${NE}.g
GenerateVolumetricMesh --in ${GRID_FILE_ROOT}/exodus_ne${NE}.g --out ${GRID_FILE_ROOT}/exodus_ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_FILE_ROOT}/exodus_ne${NE}pg2.g --out ${DST_GRID_PG2}
#-------------------------------------------------------------------------------
# Create map file
echo
echo Creating map file from high-res topo to target grid...
echo
ncremap -a fv2se_flx --fl_fmt=64bit_data --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}
#-------------------------------------------------------------------------------
# Apply map to USGS-topo-cube3000.nc get new topo files
echo
echo Apply map to high-res topo data...
echo
ncremap --fl_fmt=64bit_data -m ${MAP_FILE} -i ${SRC_TOPO_FILE} -o ${TOPO_FILE_0}
#-------------------------------------------------------------------------------
# rename grid_size dimension to ncol
echo
echo rename grid_size dimension...
echo
ncrename -d grid_size,ncol ${TOPO_FILE_0}
#-------------------------------------------------------------------------------
# Calculate geopotential
echo
echo Calculate geopotential...
echo
ncap2 -O -s 'PHIS=terr*9.80616' ${TOPO_FILE_0} ${TOPO_FILE_1}
#-------------------------------------------------------------------------------
# Run homme_tool to smooth topo
cat <<EOF > input_NE${NE}.nl
&ctl_nl
ne = ${NE}
smooth_phis_p2filt = 0
smooth_phis_numcycle = 6
smooth_phis_nudt = 4e-16
hypervis_scaling = 2
se_ftype = 2 ! actually output NPHYS; overloaded use of ftype
/
&vert_nl
/
&analysis_nl
tool = 'topo_pgn_to_smoothed'
infilenames = '${TOPO_FILE_1}', '${TOPO_FILE_2}'
/
EOF
echo
echo Running homme_tool...
echo
${e3sm_root}/components/homme/src/tool/homme_tool < input_NE${NE}.nl
#-------------------------------------------------------------------------------
# Run cube_to_target to calculate standard deviation of sub-grid topography
echo
echo Running cube_to_target...
echo
${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${DST_GRID_PG2} \
  --input-topography ${SRC_TOPO_FILE} \
  --smoothed-topography ${TOPO_FILE_2}1.nc \
  --output-topography ${TOPO_FILE_3}
#-------------------------------------------------------------------------------
# Append the GLL phi_s data to the output of previous step

ncks -A ${TOPO_FILE_2}1.nc ${TOPO_FILE_3}

#-------------------------------------------------------------------------------
set +v

echo
echo NE           : $NE
echo DST_GRID_PG2 : $DST_GRID_PG2
echo TOPO_FILE_0  : $TOPO_FILE_0
echo TOPO_FILE_1  : $TOPO_FILE_1
echo TOPO_FILE_2  : $TOPO_FILE_2
echo TOPO_FILE_3  : $TOPO_FILE_3
echo