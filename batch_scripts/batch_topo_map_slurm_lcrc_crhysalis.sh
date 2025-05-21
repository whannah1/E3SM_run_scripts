#!/bin/bash
#SBATCH --account=e3sm
#SBATCH --job-name=generate_topo_map
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#---------------------------------------------------------------------------

# Stop script execution on error
set -e

# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' ; NC='\033[0m'


#---------------------------------------------------------------------------
# Make sure all these lines are correct for the machine

source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh

NE_SRC=3000
NE_DST=30

SCRATCH=/lcrc/group/e3sm/${USER}/scratch/chrys
e3sm_root=${SCRATCH}/tmp_e3sm_src # make sure this contains an up-to-date clone of E3SM
grid_root=${SCRATCH}/files_grid
map_root=${SCRATCH}/files_map
topo_root=${SCRATCH}/files_topo
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata

# MAP_ARGS=
MAP_ARGS+="--mpi_nbr=32"

#---------------------------------------------------------------------------

topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_2=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
topo_file_3=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc

map_file_src_to_np4=${map_root}/map_ne${NE_SRC}pg1_to_ne${NE_DST}np4_fv2se_flx_mb.nc

#---------------------------------------------------------------------------  
# print some useful things

echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo 
echo   NE_SRC              = $NE_SRC
echo   NE_DST              = $NE_DST
echo
echo   e3sm_root           = $e3sm_root
echo   grid_root           = $grid_root
echo   map_root            = $map_root
echo   topo_root           = $topo_root
echo   DIN_LOC_ROOT        = $DIN_LOC_ROOT
echo
echo   topo_file_0         = $topo_file_0
echo   topo_file_1         = $topo_file_1
echo   topo_file_2         = $topo_file_2
echo   topo_file_3         = $topo_file_3
echo
echo   map_file_src_to_np4 = $map_file_src_to_np4
echo
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------

#---------------------------------------------------------------------------

mkdir -p ${grid_root} ${map_root} ${topo_root}

if [ ! -d ${grid_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${grid_root} ; fi
if [ ! -d ${map_root}  ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${map_root} ; fi
if [ ! -d ${topo_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${topo_root} ; fi

#---------------------------------------------------------------------------

# set to echo commands
set -x

#---------------------------------------------------------------------------
# Create Grid and Map Files

# # Grid for source high res topo
# GenerateCSMesh --alt --res ${NE_SRC}  --file ${grid_root}/exodus_ne${NE_SRC}.g
# ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_SRC}.g  --out ${grid_root}/scrip_ne${NE_SRC}pg1.nc

# Grid for target EAM grid
GenerateCSMesh --alt --res ${NE_DST} --file ${grid_root}/exodus_ne${NE_DST}.g
GenerateVolumetricMesh --in ${grid_root}/exodus_ne${NE_DST}.g --out ${grid_root}/exodus_ne${NE_DST}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_DST}pg2.g --out ${grid_root}/scrip_ne${NE_DST}pg2.nc

# Map from source to target np4 
time ncremap ${MAP_ARGS} -a fv2se_flx \
--src_grd=${grid_root}/scrip_ne${NE_SRC}pg1.nc  \
--dst_grd=${grid_root}/exodus_ne${NE_DST}.g \
--map_file=${map_file_src_to_np4} \
--tmp_dir=${map_root}

#---------------------------------------------------------------------------

set +x

if [ ! -f ${map_file_src_to_np4} ]; then
  echo
  echo -e ${RED} Failed to create map file - Errors ocurred ${NC}
  echo
else
  echo
  echo -e ${GRN} Sucessfully created new map file  ${NC}
  echo $map_file_src_to_np4
  echo
fi
#---------------------------------------------------------------------------