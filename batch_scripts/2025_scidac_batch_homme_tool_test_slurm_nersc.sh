#!/bin/bash
#SBATCH --account=m4310
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --job-name=homme_tool_test
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=0:30:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# Make sure all these lines are correct for the machine
#-------------------------------------------------------------------------------

# Specify target resolution
NE_DST=30

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
# load env
module load python
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
#-------------------------------------------------------------------------------
# # Stop script execution on error
# set -e
# # ANSI color codes for highlighting terminal output
# RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# # start timer for entire script
# start=`date +%s`
#-------------------------------------------------------------------------------
# Generate GLL SCRIP grid file for target topo grid
cd ${homme_tool_root}
rm -f ${homme_tool_root}/input.nl
cat > ${homme_tool_root}/input.nl <<EOF
&ctl_nl
ne = ${NE_DST}
mesh_file = "none"
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
io_stride = 16
/
EOF
# run homme_tool to generate np4 scrip file
srun -n 8 ${e3sm_root}/cmake_homme/src/tool/homme_tool < ${homme_tool_root}/input.nl

#-------------------------------------------------------------------------------
# # Indicate overall run time for this script
# end=`date +%s`
# runtime_sc=$(( end - start ))
# runtime_mn=$(( runtime_sc/60 ))
# runtime_hr=$(( runtime_mn/60 ))
# echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
# echo
#-------------------------------------------------------------------------------
