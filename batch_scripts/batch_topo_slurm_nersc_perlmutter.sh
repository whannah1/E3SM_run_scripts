#!/bin/bash
#SBATCH --account=m3312
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=generate_topo
#SBATCH --output=generate_topo_slurm-%x-%j.out
#SBATCH --time=1:00:00
#SBATCH --nodes=1
#---------------------------------------------------------------------------

# Stop script execution on error
set -e

#---------------------------------------------------------------------------
# Make sure all these lines are correct for the machine

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

NE_SRC=90
NE_DST=4

e3sm_root=${SCRATCH}/tmp_e3sm_src
grid_root=${SCRATCH}/e3sm_scratch/files_grid
map_root=${SCRATCH}/e3sm_scratch/files_map
topo_root=${SCRATCH}/e3sm_scratch/files_topo
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata

MAP_ARGS=
# MAP_ARGS+="--mpi_nbr=32"

#---------------------------------------------------------------------------

topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${topo_root}/tmp_USGS-topo_ne${NE_SRC}pg1.nc
topo_file_2=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_3=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
topo_file_4=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t_ne${NE_SRC}pg1.nc
topo_file_5=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t_ne${NE_SRC}pg1_anomalies.nc
topo_file_6=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t_sgh.nc
topo_file_7=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t_ne${NE_DST}pg2.nc
topo_file_8=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t.nc

map_file_src_to_np4=${map_root}/map_ne${NE_SRC}pg1_to_ne${NE_DST}np4_fv2se_flx.nc
map_file_src_to_pg2=${map_root}/map_ne${NE_SRC}pg1_to_ne${NE_DST}pg2_traave.nc
map_file_pg2_to_src=${map_root}/map_ne${NE_DST}pg2_to_ne${NE_SRC}pg1_traave.nc
map_file_np4_to_pg2=${map_root}/map_ne${NE_DST}np4_to_ne${NE_DST}pg2_se2fv_flx.nc

#---------------------------------------------------------------------------  
# print some useful things

echo 
echo NE_SRC              = $NE_SRC
echo NE_DST              = $NE_DST
echo
echo e3sm_root           = $e3sm_root
echo grid_root           = $grid_root
echo map_root            = $map_root
echo topo_root           = $topo_root
echo DIN_LOC_ROOT        = $DIN_LOC_ROOT
echo
echo topo_file_0         = $topo_file_0
echo topo_file_1         = $topo_file_1
echo topo_file_2         = $topo_file_2
echo topo_file_3         = $topo_file_3
echo topo_file_4         = $topo_file_4
echo topo_file_5         = $topo_file_5
echo topo_file_6         = $topo_file_6
echo topo_file_7         = $topo_file_7
echo topo_file_8         = $topo_file_8
echo
echo map_file_src_to_np4 = $map_file_src_to_np4
echo map_file_src_to_pg2 = $map_file_src_to_pg2
echo map_file_pg2_to_src = $map_file_pg2_to_src
echo map_file_np4_to_pg2 = $map_file_np4_to_pg2
echo

#---------------------------------------------------------------------------

# set to echo commands
set -x

#---------------------------------------------------------------------------

mkdir -p ${grid_root} ${map_root} ${topo_root}
ls -ld ${grid_root} ${map_root} ${topo_root} ${e3sm_root} ${DIN_LOC_ROOT}

#---------------------------------------------------------------------------
# Create Grid Files

# Grid for source high res topo
GenerateCSMesh --alt --res ${NE_SRC}  --file ${grid_root}/exodus_ne${NE_SRC}.g
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_SRC}.g  --out ${grid_root}/scrip_ne${NE_SRC}pg1.nc

# Grid for target EAM grid
GenerateCSMesh --alt --res ${NE_DST} --file ${grid_root}/exodus_ne${NE_DST}.g
GenerateVolumetricMesh --in ${grid_root}/exodus_ne${NE_DST}.g --out ${grid_root}/exodus_ne${NE_DST}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/exodus_ne${NE_DST}pg2.g --out ${grid_root}/scrip_ne${NE_DST}pg2.nc

#---------------------------------------------------------------------------
# Create Map files

# from source to target np4 
ncremap ${MAP_ARGS} -5 -a fv2se_flx --src_grd=${grid_root}/scrip_ne${NE_SRC}pg1.nc  --dst_grd=${grid_root}/exodus_ne${NE_DST}.g --map_file=${map_file_src_to_np4}

# from source to target pg2
ncremap ${MAP_ARGS} -5 -a traave --src_grd=${grid_root}/scrip_ne${NE_SRC}pg1.nc  --dst_grd=${grid_root}/scrip_ne${NE_DST}pg2.nc --map_file=${map_file_src_to_pg2}

# Use TempestRemap to generate transpose of previous map (for calculating sub-grid anomalies on target grid)
GenerateTransposeMap --in ${map_file_src_to_pg2} --out ${map_file_pg2_to_src}

# from target np4 to target pg2
ncremap ${MAP_ARGS} -5 -a se2fv_flx --src_grd=${grid_root}/exodus_ne${NE_DST}.g  --dst_grd=${grid_root}/scrip_ne${NE_DST}pg2.nc --map_file=${map_file_np4_to_pg2}

#---------------------------------------------------------------------------
# Remap Topograpy

# Compute phi_s on the source np4 grid
ncap2 -O -s 'PHIS=terr*9.80616' ${topo_file_0} ${topo_file_1}

# rename the column dimension to be "ncol"
ncrename -d grid_size,ncol ${topo_file_1}

# Map high-res topo to target np4 grid
ncremap -m ${map_file_src_to_np4} -i ${topo_file_1} -o ${topo_file_2}

#---------------------------------------------------------------------------
# Apply Smoothing

cd ${e3sm_root}/components/homme

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
infilenames = '${topo_file_2}', '${topo_file_3}'
/
EOF

mpirun -np 8 ${e3sm_root}/components/homme/src/tool/homme_tool < input.nl

# rename output file to remove "1.nc" suffix
mv ${topo_file_3}1.nc ${topo_file_3}

#---------------------------------------------------------------------------
# Compute SGH

# Remap smoothed data back to source grid
ncremap -v PHIS -m ${map_file_pg2_to_src} -i ${topo_file_3} -o ${topo_file_4}

# Calculate anomalies on source grid
ncdiff -O ${topo_file_1} ${topo_file_4} ${topo_file_5}

# Square the anomaly values
ncap2 -O -s 'PHIS_ANOM_SQ=PHIS^2' ${topo_file_5} ${topo_file_5}

# Remap squared anomalies back to target pg2 grid
ncremap -v PHIS_ANOM_SQ -m ${map_file_src_to_pg2} -i ${topo_file_5} -o ${topo_file_6}

# Take the square root of the remapped to get standard deviation (SGH)
ncap2 -O -s 'SGH=sqrt(PHIS_ANOM_SQ)' ${topo_file_6} ${topo_file_6}

#---------------------------------------------------------------------------
# Create Final Topo File

# Create final topo file starting with smoothed PHIS data
cp ${topo_file_3} ${topo_file_8}

# Append the SGH data
ncks -A -v SGH ${topo_file_6} ${topo_file_8}

# rename GLL coordinate to ncol_d
ncrename -d ncol,ncol_d ${topo_file_2}

# Map np4 LANDFRAC and SGH30 to the target pg2 grid
ncremap -v SGH30,LANDFRAC -m ${map_file_np4_to_pg2} -i ${topo_file_2} -o ${topo_file_7}

# Append the pg2 LANDFRAC and SGH30 data to final file
ncks -A -v SGH30,LANDFRAC --hdr_pad=100000 ${topo_file_7} ${topo_file_8}

#---------------------------------------------------------------------------
# Clean up Temporary Files

rm ${topo_root}/tmp_USGS-topo*

#---------------------------------------------------------------------------
echo
echo Sucessfully created new topography data file:
echo $topo_file_8
echo
#---------------------------------------------------------------------------