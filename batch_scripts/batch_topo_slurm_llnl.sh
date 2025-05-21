#!/bin/bash
#SBATCH --account=nhclilab
#SBATCH --qos=normal
#SBATCH --job-name=generate_topo
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#---------------------------------------------------------------------------
# Make sure all these lines are correct for the machine
# source activate /g/g19/hannah6/miniconda3/envs/e3sm-unified
source activate /usr/gdata/e3sm/install/dane/e3sm-unified
# Specify source and target resolutions
NE_SRC=3000

# BASE_RES=32
# BASE_RES=64
# BASE_RES=128

if [ -z "${BASE_RES:-}" ]; then
  echo "BASE_RES not set, exiting...."
  exit 1
fi

atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3

# Specify time stamp for creation date
# timestamp=$(date +%Y%m%d)
timestamp=20240618
# Specify E3SM source code path - preferably a fresh clone
SCRATCH=/p/lustre1/hannah6/2024-nimbus-iraq-data
E3SM_ROOT=${HOME}/E3SM/E3SM_SRC0
# Specify root paths
GRID_ROOT=${SCRATCH}/files_grid
MAP_ROOT=${SCRATCH}/files_map
TOPO_ROOT=${SCRATCH}/files_topo
DIN_LOC_ROOT=/usr/gdata/e3sm/ccsm3data/inputdata
# argument for ncremap to select TempestRemap or mbtempest backend
MAP_ARGS=
# MAP_ARGS+="--mpi_nbr=32"
#---------------------------------------------------------------------------
# Stop script execution on error
set -e
# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# start timer for entire script
start=`date +%s`
#---------------------------------------------------------------------------
# Specify topo file names - including temporary files that will be deleted
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${TOPO_ROOT}/tmp_USGS-topo_${atm_grid_name}-np4.nc
topo_file_2=${TOPO_ROOT}/tmp_USGS-topo_${atm_grid_name}-np4_smoothedx6t.nc
topo_file_3=${TOPO_ROOT}/USGS-topo_${atm_grid_name}-np4_smoothedx6t_${timestamp}.nc
# Specify map file name
map_file_src_to_np4=${MAP_ROOT}/map_ne${NE_SRC}pg1_to_${atm_grid_name}-np4_fv2se_flx.${timestamp}.nc
#---------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo
echo   NE_SRC              = $NE_SRC
echo   atm_grid_name       = $atm_grid_name
echo
echo   E3SM_ROOT           = $E3SM_ROOT
echo   GRID_ROOT           = $GRID_ROOT
echo   MAP_ROOT            = $MAP_ROOT
echo   TOPO_ROOT           = $TOPO_ROOT
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
# Make sure paths exist
mkdir -p ${GRID_ROOT} ${MAP_ROOT} ${TOPO_ROOT}
if [ ! -d ${DIN_LOC_ROOT} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${DIN_LOC_ROOT} ; fi
if [ ! -d ${E3SM_ROOT}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${E3SM_ROOT} ; fi
if [ ! -d ${GRID_ROOT}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${GRID_ROOT} ; fi
if [ ! -d ${MAP_ROOT}     ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${MAP_ROOT} ; fi
if [ ! -d ${TOPO_ROOT}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${TOPO_ROOT} ; fi
#---------------------------------------------------------------------------
# set to echo commands
set -x
#---------------------------------------------------------------------------
# # Create grid for source high res topo
# GenerateCSMesh --alt --res ${NE_SRC} --file ${GRID_ROOT}/exodus_ne${NE_SRC}.g
# ConvertMeshToSCRIP --in ${GRID_ROOT}/exodus_ne${NE_SRC}.g  --out ${GRID_ROOT}/scrip_ne${NE_SRC}pg1.nc
#---------------------------------------------------------------------------
# # Create map from source to target np4
# time ncremap ${MAP_ARGS} -a fv2se_flx \
#   --src_grd=${GRID_ROOT}/scrip_ne${NE_SRC}pg1.nc \
#   --dst_grd=${GRID_ROOT}/${atm_grid_name}.g \
#   --map_file=${map_file_src_to_np4} \
#   --tmp_dir=${MAP_ROOT}
#---------------------------------------------------------------------------
# Remap high-res topo to target np4 grid
ncremap -m ${map_file_src_to_np4} -i ${topo_file_0} -o ${topo_file_1}
# Compute phi_s on the target np4 grid
ncap2 -O -s 'PHIS=terr*9.80616' ${topo_file_1} ${topo_file_1}
# rename the column dimension to be "ncol"
ncrename -d grid_size,ncol ${topo_file_1}
#---------------------------------------------------------------------------
# Apply Smoothing
cd ${E3SM_ROOT}/components/homme
${E3SM_ROOT}/cime/CIME/scripts/configure && source .env_mach_specific.sh
# Create namelist file for HOMME
cat <<EOF > input_ne${BASE_RES}.nl
&ctl_nl
mesh_file = "${GRID_ROOT}/${atm_grid_name}.g"
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
srun -n 8 ${E3SM_ROOT}/components/homme/src/tool/homme_tool < input_ne${BASE_RES}.nl
# rename output file to remove "1.nc" suffix
mv ${topo_file_2}1.nc ${topo_file_2}
#---------------------------------------------------------------------------
# Compute SGH with cube_to_target
${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc \
  --input-topography ${topo_file_0} \
  --smoothed-topography ${topo_file_2} \
  --output-topography ${topo_file_3}
# Append the GLL phi_s data to the output
ncks -A ${topo_file_2} ${topo_file_3}
#---------------------------------------------------------------------------
# Clean up Temporary Files
rm ${TOPO_ROOT}/tmp_USGS-topo_${atm_grid_name}*
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