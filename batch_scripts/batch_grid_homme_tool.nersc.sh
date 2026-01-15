#!/bin/bash
#SBATCH --account=m2637
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=homme_tool_gen_grid
#SBATCH --output=/global/homes/w/whannah/E3SM/logs_slurm/homme_tool_gen_grid_slurm-%x-%j.out
#SBATCH --time=8:00:00
#SBATCH --nodes=16
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# sbatch ${HOME}/E3SM/batch_scripts/batch_grid_homme_tool.nersc.sh
#-------------------------------------------------------------------------------

ntasks=2048

NE=1024

timestamp=20251023

e3sm_root=/pscratch/sd/w/whannah/tmp_e3sm_src

data_root=/global/cfs/cdirs/e3sm/whannah

grid_root=${data_root}/files_grid
maps_root=${data_root}/files_map

DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
homme_tool_root=${e3sm_root}/cmake_homme

#-------------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------; echo
echo "   NE                  = ${NE}"; echo
echo "   e3sm_root           = $e3sm_root"
echo "   grid_root           = $grid_root"
echo "   maps_root           = $maps_root"
echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"; echo
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# start timer for entire script
start=`date +%s`
# Stop script execution on error
set -e
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
#-------------------------------------------------------------------------------
unset ENVIRONMENT_RUNNING_E3SM_UNIFIED_USE_ANOTHER_TERMINAL
unified_bin=/global/common/software/e3sm/anaconda_envs/base/envs/e3sm_unified_1.11.1_login/bin
module load python
source activate hiccup_env
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
ulimit -s unlimited # required for larger grids
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
# Generate GLL SCRIP grid file for target topo grid
echo
echo -e ${GRN} Creating np4 grid file with homme_tool ${NC} $slurm_log_create_grid
echo
cd ${e3sm_root}/cmake_homme

homme_tool_exe=${e3sm_root}/cmake_homme/src/tool/homme_tool
namelist_file=${e3sm_root}/cmake_homme/input.nl

rm -f ${namelist_file}
cat > ${namelist_file} <<EOF
&ctl_nl
ne = 0
mesh_file = "${grid_root}/ne${NE}.g"
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

cmd="srun -n ${ntasks} ${homme_tool_exe} < ${namelist_file}"

echo ${GRN}${cmd}${NC} ; echo
eval "${cmd}"

# use python utility for format conversion
HtoS=${e3sm_root}/components/homme/test/tool/python/HOMME2SCRIP.py
src_file=${homme_tool_root}/ne0np4_tmp1.nc
dst_file=${grid_root}/ne${NE}np4_scrip.nc
cmd="${unified_bin}/python ${HtoS} --src_file ${src_file} --dst_file ${dst_file}"

echo ${GRN}${cmd}${NC} ; echo
eval "${cmd}"

#-------------------------------------------------------------------------------
if [ ! -f ${dst_file} ]; then
  echo; echo -e ${RED} Failed to create file: ${NC} ${dst_file} ; exit; echo;
else
  echo; echo -e ${GRN} Successfully created file: ${NC} ${dst_file} ; echo;
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
