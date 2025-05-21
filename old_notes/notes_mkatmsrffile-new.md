# Set paths and file names

```shell
# LCRC paths
source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
SCRATCH=/lcrc/group/e3sm/${USER}/scratch/chrys
e3sm_root=${SCRATCH}/tmp_e3sm_src
GRID_ROOT=${SCRATCH}/files_grid
MAP_ROOT=${SCRATCH}/files_map
atmsrf_root=${SCRATCH}/files_atmsrf
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata

NE=30
SRC_GRID=${DIN_LOC_ROOT}/../mapping/grids/1x1d.nc
DST_GRID=${GRID_ROOT}/scrip_ne${NE}pg2.nc
```

```shell
# Perlmutter paths
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
SCRATCH=/pscratch/sd/w/${USER}/e3sm_scratch/
e3sm_root=${HOME}/E3SM/E3SM_SRC1
GRID_ROOT=${SCRATCH}/files_grid
MAP_ROOT=${SCRATCH}/files_map
atmsrf_root=${SCRATCH}/files_atmsrf
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
```

# Create map file

```shell
# MAP_FILE=${MAP_ROOT}/map_1x1_to_ne${NE}pg2_traave.nc
# ncremap -a traave --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}

MAP_FILE=${MAP_ROOT}/map_1x1_to_ne${NE}pg2_aave.nc
ncremap -a aave --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}
```

# Create atmsrf file

```shell
VEGE_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/regrid_vegetation.nc
SOIL_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/clim_soilw.nc

python ${e3sm_root}/components/eam/tools/mkatmsrffile/mkatmsrffile.py --map_file=${MAP_FILE} --vegetation_file=${VEGE_FILE} --soil_water_file=${SOIL_FILE} --output_root=${atmsrf_root} --dst_grid=ne${NE}pg2 --date-stamp=20240613
```


# Compare to old atmsrf files

```shell
${DIN_LOC_ROOT}/atm/cam/chem/trop_mam/atmsrf_ne30np4_110920.nc

${DIN_LOC_ROOT}/atm/cam/chem/trop_mam/atmsrf_ne30pg2_200129.nc 

${SCRATCH}/files_atmsrf/atm_srf_ne30pg2_20240613.nc

${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
module load netcdf-fortran/4.5.3-pdrzgqj 

# cd /lcrc/group/e3sm/ac.whannah/scratch/chrys/tmp_e3sm_src/cime/CIME/non_py/cprnc/bld
cd ${e3sm_root}/cime/CIME/non_py/cprnc/bld
cmake ../
make clean ; make

alias cprnc=${SCRATCH}/tmp_e3sm_src/cime/CIME/non_py/cprnc/bld/cprnc

./cprnc ${DIN_LOC_ROOT}/atm/cam/chem/trop_mam/atmsrf_ne30pg2_200129.nc ${SCRATCH}/files_atmsrf/atm_srf_ne30pg2_20240613.nc


# Perlmutter
/global/cfs/cdirs/e3sm/tools/cprnc/cprnc -m ${DIN_LOC_ROOT}/atm/cam/chem/trop_mam/atmsrf_ne30pg2_200129.nc ${SCRATCH}/files_atmsrf/atm_srf_ne30pg2_20240613.nc

```

# File paths from old guide

```shell
srfFileName: /project/projectdirs/e3sm/mapping/grids/1x1d.nc
atmFileName: /project/projectdirs/e3sm/mapping/grids/ne30np4_pentagons.091226.nc
landFileName: /project/projectdirs/e3sm/inputdata/atm/cam/chem/trop_mozart/dvel/regrid_vegetation.nc
soilwFileName: /project/projectdirs/e3sm/inputdata/atm/cam/chem/trop_mozart/dvel/clim_soilw.nc
srf2atmFmapname: /project/projectdirs/e3sm/bhillma/grids/ne30np4/atmsrffile/map_1x1_to_ne30np4_aave.nc
```

# Check gen_domain for similar file writing errors on Chrysalis

```shell

source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
SCRATCH=/lcrc/group/e3sm/${USER}/scratch/chrys
# e3sm_root=${SCRATCH}/tmp_e3sm_src
e3sm_root=${HOME}/E3SM/E3SM_SRC0
GRID_ROOT=${SCRATCH}/files_grid
MAP_ROOT=${SCRATCH}/files_map
atmsrf_root=${SCRATCH}/files_atmsrf
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata

OCN_NAME=oEC60to30v3
OCN_FILE=${DIN_LOC_ROOT}/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.161222.nc

NE=30
ATM_FILE=${GRID_ROOT}/scrip_ne${NE}pg2.nc

MAP_FILE=${MAP_ROOT}/map_${OCN_NAME}_to_ne${NE}pg2_traave.nc
```

```shell
ncremap -5 -a traave --src_grd=${OCN_FILE} --dst_grd=${ATM_FILE} --map_file=${MAP_FILE}
```

```shell
OUTPUT_ROOT=${SCRATCH}/files_domain
python ${e3sm_root}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o oEC60to30v3 -l ne${NE}pg2 --date-stamp=9999 --output-root=${OUTPUT_ROOT}
```
