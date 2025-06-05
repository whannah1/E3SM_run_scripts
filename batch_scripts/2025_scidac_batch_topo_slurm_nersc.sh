#!/bin/bash
#SBATCH --account=m4310
#SBATCH --constraint=cpu
###SBATCH --qos=regular
#SBATCH --qos=debug
####SBATCH --job-name=generate_topo
#SBATCH --job-name=generate_topo_ne22
#SBATCH --output=slurm-%x-%j.out
###SBATCH --time=1:00:00
#SBATCH --time=0:10:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# Make sure all these lines are correct for the machine
#-------------------------------------------------------------------------------

# unified_src=/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
unified_bin=/global/common/software/e3sm/anaconda_envs/base/envs/e3sm_unified_1.11.1_login/bin

# Specify source and target/destination resolutions
NE_SRC=3000
# NE_DST=22 # don't set here - just supply from command line arg

# Specify time stamp for creation date
timestamp=20250513 # or timestamp=$(date +%Y%m%d)

# Specify E3SM source code path - preferably a fresh clone
e3sm_root=/pscratch/sd/w/whannah/tmp_e3sm_src

# Specify root paths
data_root=/global/cfs/cdirs/m4310/whannah 
grid_root=${data_root}/files_grid
map_root=${data_root}/files_map
topo_root=${data_root}/files_topo
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
homme_tool_root=${e3sm_root}/cmake_homme

#-------------------------------------------------------------------------------
# Specify topo file names - including temporary files that will be deleted
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_2=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
topo_file_3=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc
#-------------------------------------------------------------------------------
# load env
module load python
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
#-------------------------------------------------------------------------------
# Stop script execution on error
set -e
# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# start timer for entire script
start=`date +%s`
#-------------------------------------------------------------------------------  
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
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#---------------------------------------------------------------------------
if [ -z "${NE_SRC}" ]; then echo -e ${RED}ERROR: NE_SRC is not defined ; fi
if [ -z "${NE_DST}" ]; then echo -e ${RED}ERROR: NE_DST is not defined ; fi
#---------------------------------------------------------------------------
# Make sure paths exist
mkdir -p ${grid_root} ${map_root} ${topo_root}
if [ ! -d ${DIN_LOC_ROOT} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${DIN_LOC_ROOT} ; fi
if [ ! -d ${e3sm_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${e3sm_root} ; fi
if [ ! -d ${grid_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${grid_root} ; fi
if [ ! -d ${map_root}     ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${map_root} ; fi
if [ ! -d ${topo_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${topo_root} ; fi
#-------------------------------------------------------------------------------
# set to echo commands
set -x
#-------------------------------------------------------------------------------
# # Create grid for source high res topo
# if [ ! -d ${grid_root}/ne${NE_SRC}_exodus.g    ]; then
#   ${unified_bin}/GenerateCSMesh --alt --res ${NE_SRC} \
#   --file ${grid_root}/ne${NE_SRC}_exodus.g
# fi
# if [ ! -d ${grid_root}/ne${NE_SRC}pg2_scrip.nc ]; then
#   ${unified_bin}/ConvertMeshToSCRIP \
#   --in ${grid_root}/ne${NE_SRC}_exodus.g  \
#   --out ${grid_root}/ne${NE_SRC}pg2_scrip.nc
# fi
# #-------------------------------------------------------------------------------
# # Create grid for target EAM grid
# if [ ! -d ${grid_root}/ne${NE_DST}_exodus.g    ]; then
#   ${unified_bin}/GenerateCSMesh --alt --res ${NE_DST} \
#   --file ${grid_root}/ne${NE_DST}_exodus.g
# fi
# if [ ! -d ${grid_root}/ne${NE_DST}pg2_exodus.g ]; then
#   ${unified_bin}/GenerateVolumetricMesh \
#   --in ${grid_root}/ne${NE_DST}_exodus.g \
#   --out ${grid_root}/ne${NE_DST}pg2_exodus.g --np 2 --uniform
# fi
# if [ ! -d ${grid_root}/ne${NE_DST}pg2_scrip.nc ]; then
#   ${unified_bin}/ConvertMeshToSCRIP \
#   --in ${grid_root}/ne${NE_DST}pg2_exodus.g \
#   --out ${grid_root}/ne${NE_DST}pg2_scrip.nc
# fi
#-------------------------------------------------------------------------------
# Generate GLL SCRIP grid file for target topo grid

# cd ${homme_tool_root}
# rm -f ${homme_tool_root}/input.nl
# cat > ${homme_tool_root}/input.nl <<EOF
# &ctl_nl
# ne = ${NE_DST}
# mesh_file = "none"
# /
# &vert_nl    
# /
# &analysis_nl
# tool = 'grid_template_tool'
# output_dir = "./"
# output_timeunits=1
# output_frequency=1
# output_varnames1='area','corners','cv_lat','cv_lon'
# output_type='netcdf'    
# io_stride = 16
# /
# EOF
# # run homme_tool to generate np4 scrip file
# srun -n 8 ${e3sm_root}/cmake_homme/src/tool/homme_tool < ${homme_tool_root}/input.nl

#-------------------------------------------------------------------------------
# echo Successfully finished homme_tool
# exit
#-------------------------------------------------------------------------------
# run python utility to perform format conversion
${unified_bin}/python ${e3sm_root}/components/homme/test/tool/python/HOMME2SCRIP.py  \
        --src_file ${homme_tool_root}/ne${NE_DST}np4_tmp1.nc \
        --dst_file ${grid_root}/ne${NE_DST}np4_scrip.nc
#-------------------------------------------------------------------------------
# use cube_to_target to do the remapping
${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${grid_root}/ne${NE_DST}np4_scrip.nc \
  --input-topography ${topo_file_0} \
  --output-topography ${topo_file_1}
#-------------------------------------------------------------------------------
# Apply Smoothing
cd ${homme_tool_root}
# Create namelist file for HOMME
rm -f ${homme_tool_root}/input.nl
cat > ${homme_tool_root}/input.nl <<EOF
&ctl_nl
mesh_file = "${grid_root}/ne${NE_DST}.g"
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
srun -n 8 ${homme_tool_root}/src/tool/homme_tool < ${homme_tool_root}/input.nl
# rename output file to remove "1.nc" suffix
mv ${topo_file_2}1.nc ${topo_file_2}
#-------------------------------------------------------------------------------
# Compute SGH with cube_to_target
${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${grid_root}/ne${NE_DST}pg2_scrip.nc \
  --input-topography ${topo_file_0} \
  --smoothed-topography ${topo_file_2} \
  --output-topography ${topo_file_3} \
  --add-oro-shape
#-------------------------------------------------------------------------------
# source {unified_src} # this is problematic - just use unified_bin
#-------------------------------------------------------------------------------
# Append the GLL phi_s data to the output
${unified_bin}/ncks -A ${topo_file_2} ${topo_file_3}
#-------------------------------------------------------------------------------
# # Clean up Temporary Files
# rm ${topo_root}/tmp_USGS-topo_ne${NE_DST}*
#-------------------------------------------------------------------------------
# stop echoing commands
set +x
#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#-------------------------------------------------------------------------------
