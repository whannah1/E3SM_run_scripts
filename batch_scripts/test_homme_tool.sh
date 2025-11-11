#!/bin/bash
#SBATCH --account=m4842
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --job-name=test_homme_tool
#SBATCH --output=/global/homes/w/whannah/E3SM/logs_slurm/test_homme_tool_slurm-%x-%j.out 
#SBATCH --time=0:05:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# sbatch ${HOME}/E3SM/batch_scripts/test_homme_tool.sh
#-------------------------------------------------------------------------------
grid_name=2025-sohip-32x3-patagonia
timestamp=20250904
e3sm_root=/pscratch/sd/w/whannah/tmp_e3sm_src
data_root=/global/cfs/cdirs/m4842/whannah
grid_root=${data_root}/files_grid
maps_root=${data_root}/files_map
topo_root=${data_root}/files_topo
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
homme_tool_root=${e3sm_root}/cmake_homme
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube3000.nc
topo_file_1=${topo_root}/tmp_USGS-topo_${grid_name}-np4.nc
topo_file_2=${topo_root}/tmp_USGS-topo_${grid_name}-np4_smoothedx6t.nc
topo_file_3=${topo_root}/USGS-topo_${grid_name}-np4_smoothedx6t_${timestamp}.nc
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
echo --------------------------------------------------------------------------------; echo
echo "   grid_name           = ${grid_name}"; echo
echo "   e3sm_root           = $e3sm_root"
echo "   grid_root           = $grid_root"
echo "   maps_root           = $maps_root"
echo "   topo_root           = $topo_root"
echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"; echo
echo "   topo_file_0         = $topo_file_0"
echo "   topo_file_1         = $topo_file_1"
echo "   topo_file_2         = $topo_file_2"
echo "   topo_file_3         = $topo_file_3"; echo
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#---------------------------------------------------------------------------
# if [ -z "${NE_SRC}" ]; then echo -e ${RED}ERROR: NE_SRC is not defined${NC}; exit ; fi
# if [ -z "${NE_DST}" ]; then echo -e ${RED}ERROR: NE_DST is not defined${NC}; exit ; fi
if [ -z "${grid_name}" ]; then echo -e ${RED}ERROR: grid_name is not defined${NC}; exit ; fi
#---------------------------------------------------------------------------
# Make sure paths exist
mkdir -p ${grid_root} ${maps_root} ${topo_root}
if [ ! -d ${DIN_LOC_ROOT} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${DIN_LOC_ROOT} ; fi
if [ ! -d ${e3sm_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${e3sm_root} ; fi
if [ ! -d ${grid_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${grid_root} ; fi
if [ ! -d ${maps_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${maps_root} ; fi
if [ ! -d ${topo_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${topo_root} ; fi
#-------------------------------------------------------------------------------
unified_bin=/global/common/software/e3sm/anaconda_envs/base/envs/e3sm_unified_1.11.1_login/bin
module load python
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
ulimit -s unlimited
#-------------------------------------------------------------------------------
set -x
#-------------------------------------------------------------------------------
cd ${e3sm_root}/cmake_homme
#-------------------------------------------------------------------------------
rm -f ${e3sm_root}/cmake_homme/input.nl
cat > ${e3sm_root}/cmake_homme/input.nl <<EOF
&ctl_nl
ne = 0
mesh_file = "/global/cfs/cdirs/m4842/whannah/files_grid/2025-sohip-32x3-patagonia.g"
/
&vert_nl    
/
&analysis_nl
tool = 'grid_template_tool'
output_dir = "./"
output_timeunits=1
output_frequency=1
output_varnames1='area','corners','cv_lat','cv_lon'
output_type='netcdf'    
io_stride = 1
/
EOF
#-------------------------------------------------------------------------------
srun -n 4 ${e3sm_root}/cmake_homme/src/tool/homme_tool < ${e3sm_root}/cmake_homme/input.nl
#-------------------------------------------------------------------------------
echo ; echo Successfully finished homme_tool grid generation ; echo
exit
#-------------------------------------------------------------------------------
