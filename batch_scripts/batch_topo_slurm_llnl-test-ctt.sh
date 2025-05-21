#!/bin/bash
#SBATCH --account=e3sm
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=generate_topo_ctt
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#---------------------------------------------------------------------------
# Make sure all these lines are correct for the machine
unified_path=/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
# Specify source and target resolutions
# NE_SRC=3000 ; NE_DST=30
NE_SRC=3000 ; NE_DST=120
# NE_SRC=90 ; NE_DST=30 # low-res grid combination for testing
# Specify time stamp for creation date
timestamp=$(date +%Y%m%d)
# Specify E3SM source code path - preferably a fresh clone
e3sm_root=${SCRATCH}/tmp_e3sm_src
# Specify root paths
grid_root=${SCRATCH}/test_ctt_files_grid
map_root=${SCRATCH}/test_ctt_files_map
topo_root=${SCRATCH}/test_ctt_files_topo
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
# argument for ncremap to select TempestRemap or mbtempest backend
MAP_ARGS=
# MAP_ARGS+="--mpi_nbr=32"
#---------------------------------------------------------------------------
# Specify topo file names - including temporary files that will be deleted
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_2=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
topo_file_3=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc
# Specify map file name
map_file_src_to_np4=${map_root}/map_ne${NE_SRC}pg1_to_ne${NE_DST}np4_fv2se_flx.nc
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
# Stop script execution on error
set -e
# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# start timer for entire script
start=`date +%s`
#---------------------------------------------------------------------------
# Make sure paths exist
mkdir -p ${grid_root} ${map_root} ${topo_root}
if [ ! -d ${DIN_LOC_ROOT} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${DIN_LOC_ROOT} ; fi
if [ ! -d ${e3sm_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${e3sm_root} ; fi
if [ ! -d ${grid_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${grid_root} ; fi
if [ ! -d ${map_root}     ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${map_root} ; fi
if [ ! -d ${topo_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${topo_root} ; fi
#---------------------------------------------------------------------------
# set to echo commands
set -x
#---------------------------------------------------------------------------
# np4_grid_file=/global/cfs/cdirs/e3sm/mapping/grids/ne30np4_pentagons.091226.nc
np4_grid_file=/global/cfs/cdirs/e3sm/mapping/grids/ne120np4_pentagons.20190611.nc
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
# Remap high-res topo with cube_to_target
time ${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${np4_grid_file} \
  --input-topography ${topo_file_0} \
  --output-topography ${topo_file_1}
#---------------------------------------------------------------------------
source $unified_path
#---------------------------------------------------------------------------
# # Create grid for source high res topo
# GenerateCSMesh --alt --res ${NE_SRC} --file ${grid_root}/exodus_ne${NE_SRC}.g
# ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_SRC}.g  --out ${grid_root}/scrip_ne${NE_SRC}pg1.nc
# Create grid for target EAM grid
GenerateCSMesh --alt --res ${NE_DST} --file ${grid_root}/exodus_ne${NE_DST}.g
GenerateVolumetricMesh --in ${grid_root}/exodus_ne${NE_DST}.g --out ${grid_root}/exodus_ne${NE_DST}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_DST}pg2.g --out ${grid_root}/scrip_ne${NE_DST}pg2.nc
#---------------------------------------------------------------------------
# Apply Smoothing
cd ${e3sm_root}/components/homme
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
# Create namelist file for HOMME
cat <<EOF > input.nl
&ctl_nl
mesh_file = "${grid_root}/exodus_ne${NE_DST}.g"
smooth_phis_p2filt = 0
smooth_phis_numcycle = 6 ! v2/v3 uses 12/6 for more/less smoothing
smooth_phis_nudt = 4e-16
hypervis_scaling = 2
se_ftype = 2 ! actually output NPHYS; overloaded use of ftype
/
&vert_nl
/
&analysis_nl
tool = 'topo_pgn_to_smoothed'
infilenames = '${topo_file_1}', '${topo_file_2}'
/
EOF
# run homme_tool for topography smoothing
srun -n 8 ${e3sm_root}/components/homme/src/tool/homme_tool < input.nl
# rename output file to remove "1.nc" suffix
mv ${topo_file_2}1.nc ${topo_file_2}
#---------------------------------------------------------------------------
# Compute SGH with cube_to_target
time ${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${grid_root}/scrip_ne${NE_DST}pg2.nc \
  --input-topography ${topo_file_0} \
  --smoothed-topography ${topo_file_2} \
  --output-topography ${topo_file_3}
# Append the GLL phi_s data to the output
ncks -A ${topo_file_2} ${topo_file_3}
#---------------------------------------------------------------------------
# Clean up Temporary Files
rm ${topo_root}/tmp_USGS-topo_ne${NE_DST}*
#---------------------------------------------------------------------------
# stop echoing commands
set +x
#---------------------------------------------------------------------------
# Check that final topo output file was created
if [ ! -f ${topo_file_3} ]; then
  echo
  echo -e ${RED} Failed to create topography file - Errors ocurred ${NC}
  echo
else
  echo
  echo -e ${GRN} Sucessfully created new topography file  ${NC}
  echo $topo_file_3
  echo
fi
#---------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#---------------------------------------------------------------------------