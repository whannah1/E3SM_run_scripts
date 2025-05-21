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

# NE=16 ; sbatch --job-name=homme_tool_topo_ne$NE --output=${HOME}/E3SM/logs_slurm/homme_tool_topo_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_homme_tool.nersc.sh
# NE=24 ; sbatch --job-name=homme_tool_topo_ne$NE --output=${HOME}/E3SM/logs_slurm/homme_tool_topo_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_homme_tool.nersc.sh
# NE=70 ; sbatch --job-name=homme_tool_topo_ne$NE --output=${HOME}/E3SM/logs_slurm/homme_tool_topo_slurm-%x-%j.out --export=NE=$NE ~/E3SM/batch_topo_homme_tool.nersc.sh

#-------------------------------------------------------------------------------
# Load the python environment
# source activate hiccup_env
# source activate hiccup_env_moab

#source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
#module load fast-mkl-amd
#-------------------------------------------------------------------------------
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m3312
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint gpu --account=m3312
#-------------------------------------------------------------------------------

# NE=16

cd /global/cfs/projectdirs/m3312/whannah/HICCUP

e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC4
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh

DATA_FILE_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_topo
GRID_FILE_PATH=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid
TOPO_FILE_0=${DATA_FILE_ROOT}/USGS-topo_${NE}np4.nc
TOPO_FILE_1=${DATA_FILE_ROOT}/USGS-topo_${NE}np4_phis.nc
TOPO_FILE_2=${DATA_FILE_ROOT}/USGS-topo_${NE}np4_phis_x6t_tmp

source activate hiccup_env
ncap2 -s 'PHIS=terr*9.80616' ${TOPO_FILE_0} ${TOPO_FILE_1}
ncrename -d grid_size,ncol ${TOPO_FILE_1}
conda deactivate

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

${e3sm_root}/components/homme/src/tool/homme_tool < input_NE${NE}.nl

# srun --ntasks 8  ${e3sm_root}/components/homme/src/tool/homme_tool < input.nl

# mpirun -np 8 ${e3sm_root}/components/homme/src/tool/homme_tool < input.nl

echo
echo topo files: 
echo   ${TOPO_FILE_1}
echo   ${TOPO_FILE_2}
echo
