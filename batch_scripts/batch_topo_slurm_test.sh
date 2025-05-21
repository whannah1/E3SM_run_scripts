#!/bin/bash
#SBATCH --account=m3312
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=generate_topo
#SBATCH --output=slurm-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#---------------------------------------------------------------------------
e3sm_root=/pscratch/sd/w/whannah/e3sm_scratch/tmp_clone
grid_root=${SCRATCH}/e3sm_scratch/files_grid
map_root=${SCRATCH}/e3sm_scratch/files_map
topo_root=${SCRATCH}/e3sm_scratch/files_topo
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata

NE=30
#---------------------------------------------------------------------------
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube3000.nc
topo_file_1=${topo_root}/USGS-topo_ne${NE}np4.nc
topo_file_2=${topo_root}/USGS-topo_ne${NE}np4_phis.nc
topo_file_3=${topo_root}/USGS-topo_ne${NE}np4_smoothed.nc
topo_file_4=${topo_root}/USGS-topo_ne${NE}np4_smoothed_ne3000pg1.nc
topo_file_5=${topo_root}/USGS-topo_ne${NE}np4_smoothed_ne3000pg1_anomalies.nc
topo_file_6=${topo_root}/USGS-topo_ne${NE}np4_smoothed_anomalies.nc
#---------------------------------------------------------------------------
# print some useful things to the log file
echo e3sm_root    = $e3sm_root
echo grid_root    = $grid_root
echo map_root     = $map_root
echo topo_root    = $topo_root
echo DIN_LOC_ROOT = $DIN_LOC_ROOT
echo topo_file_0  = $topo_file_0
echo topo_file_1  = $topo_file_1
echo topo_file_2  = $topo_file_2
echo topo_file_3  = $topo_file_3
echo topo_file_4  = $topo_file_4
echo topo_file_5  = $topo_file_5
echo topo_file_6  = $topo_file_6
#---------------------------------------------------------------------------
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
#---------------------------------------------------------------------------
# Create grid files for the input high res topo
GenerateCSMesh --alt --res 3000  --file ${grid_root}/exodus_ne3000.g
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne3000.g  --out ${grid_root}/scrip_ne3000pg1.nc
#---------------------------------------------------------------------------
# Create grid files target EAM grid
GenerateCSMesh --alt --res ${NE} --file ${grid_root}/exodus_ne${NE}.g
GenerateVolumetricMesh --in ${grid_root}/exodus_ne${NE}.g --out ${grid_root}/exodus_ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE}pg2.g --out ${grid_root}/scrip_ne${NE}pg2.nc
#---------------------------------------------------------------------------
# Create map files
# source to target
time ncremap -a fv2se_flx -5 --src_grd=${grid_root}/scrip_ne3000pg1.nc  --dst_grd=${grid_root}/exodus_ne${NE}.g --map_file=${map_root}/map_ne3000pg1_to_ne${NE}np4.nc
# target to source pg2
time ncremap -a traave -5 --src_grd=${grid_root}/scrip_ne3000pg1.nc  --dst_grd=${grid_root}/scrip_ne${NE}pg2.nc --map_file=${map_file_src_to_pg2}
# target pg2 to source
time ncremap -a traave -5 --src_grd=${grid_root}/scrip_ne${NE}pg2.nc  --dst_grd=${grid_root}/scrip_ne3000pg1.nc --map_file=${map_root}/map_ne${NE}pg2_to_ne3000pg1.nc
#---------------------------------------------------------------------------
# Map high-res topo to target np4 grid
time ncremap -m ${map_file_src_to_np4} -i ${topo_file_0} -o ${topo_file_1}
#---------------------------------------------------------------------------
# Compute phi_s on the np4 grid
time ncap2 -s 'PHIS=terr*9.80616' ${topo_file_1} ${topo_file_2}
# #---------------------------------------------------------------------------
# # Use homme_tool to smooth topography
# cat <<EOF > input.nl
# &ctl_nl
# ne = ${NE}
# mesh_file = "${grid_root}/exodus_ne${NE}.g"
# smooth_phis_p2filt = 0
# smooth_phis_numcycle = 12  # v3 uses 6 for less smoothing
# smooth_phis_nudt = 4e-16
# hypervis_scaling = 2
# se_ftype = 2 ! actually output NPHYS; overloaded use of ftype
# /
# &vert_nl
# /
# &analysis_nl
# tool = 'topo_pgn_to_smoothed'
# infilenames = '${topo_file_2}', '${topo_file_3::-3}'
# /
# EOF

# mpirun -np 8 ${e3sm_root}/components/homme/src/tool/homme_tool < input.nl
# #---------------------------------------------------------------------------
# # Compute SGH and SGH30 on the pg2 grid, using the pg2 phi_s data
# ncremap -v PHIS -m ${map_file_pg2_to_src} -i ${topo_file_3} -o ${topo_file_4}
# ncks -A ${topo_file_0} ${topo_file_4}
# ncdiff ${topo_file_0} ${topo_file_4} ${topo_file_5}
# ncremap -m ${map_file_src_to_pg2} -i ${topo_file_0} -o ${topo_file_6}
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------