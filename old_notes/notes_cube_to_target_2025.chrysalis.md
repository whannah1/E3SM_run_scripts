
```shell
e3sm_root=~/E3SM/E3SM_SRC2

cd ${e3sm_root}/components/eam/tools/topo_tool/cube_to_target
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
make
```


```shell chrysalis interactive job:
srun --pty --nodes=1 --time=08:00:00 /bin/bash
```

```shell chrysalis batch job:
sbatch /home/ac.whannah/E3SM/test_cube_to_target_2025.chrysalis.sh --time 4:00:00
```

```shell
#---------------------------------------------------------------------------
# e3sm_root=${SCRATCH}/tmp_e3sm_src
e3sm_root=${HOME}/E3SM/E3SM_SRC2

# source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh

# Specify source and target resolutions
NE_SRC=3000 ; NE_DST=30
# NE_SRC=90 ; NE_DST=30 # low-res grid combination for testing
# Specify time stamp for creation date
timestamp=$(date +%Y%m%d)
# Specify E3SM source code path - preferably a fresh clone
SCRATCH=/lcrc/group/e3sm/${USER}/scratch/chrys



# Specify root paths
grid_root=${SCRATCH}/files_grid
map_root=${SCRATCH}/files_map
topo_root=${SCRATCH}/files_topo
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
# argument for ncremap to select TempestRemap or mbtempest backend
# MAP_ARGS=
# MAP_ARGS+="--mpi_nbr=32"
#---------------------------------------------------------------------------
# Specify topo file names - including temporary files that will be deleted
topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
topo_file_1=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_2=${topo_root}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
topo_file_3=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc
# topo_file_3=${topo_root}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}-ORO-BASELINE.nc
# Specify map file name
map_file_src_to_np4=${map_root}/map_ne${NE_SRC}pg1_to_ne${NE_DST}np4_fv2se_flx.nc
#---------------------------------------------------------------------------
echo; echo $topo_file_0; echo $topo_file_1; echo $topo_file_2; echo $topo_file_3; echo
#---------------------------------------------------------------------------
time ${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${grid_root}/scrip_ne${NE_DST}pg2.nc \
  --input-topography ${topo_file_0} \
  --smoothed-topography ${topo_file_2} \
  --output-topography ${topo_file_3} --add-oro-shape ; echo ${topo_file_3}


# time ${e3sm_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
#   --target-grid ${grid_root}/scrip_ne${NE_DST}pg2.nc \
#   --input-topography ${topo_file_0} \
#   --smoothed-topography ${topo_file_2} \
#   --output-topography ${topo_file_3} ; echo ${topo_file_3}

```

```shell
#./cube_to_target --target-grid /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_grid/scrip_ne30pg2.nc --input-topography /lcrc/group/e3sm/data/inputdata/atm/cam/hrtopo/USGS-topo-cube90.nc --smoothed-topography /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_topo/tmp_USGS-topo_ne30np4_smoothedx6t.nc --output-topography /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_topo/USGS-topo_ne30np4_smoothedx6t_20250109.nc

./cube_to_target --target-grid /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_grid/scrip_ne30pg2.nc --input-topography /lcrc/group/e3sm/data/inputdata/atm/cam/hrtopo/USGS-topo-cube3000.nc --smoothed-topography /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_topo/tmp_USGS-topo_ne30np4_smoothedx6t.nc --output-topography /lcrc/group/e3sm/ac.whannah/scratch/chrys/files_topo/USGS-topo_ne30np4_smoothedx6t_20250122.nc --add-oro-shape
```




