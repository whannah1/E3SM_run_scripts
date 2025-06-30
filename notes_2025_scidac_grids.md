--------------------------------------------------------------------------------

# Checklist

- domain files      DONE
- topo files        DONE
- atm srf files     DONE
- coupler maps      DONE
- fsurdat           INCOMPLETE
- finidat           INCOMPLETE
- xml grid def      ???

--------------------------------------------------------------------------------

# interactive job commands

```shell
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m4310
```
--------------------------------------------------------------------------------

# Important paths - NERSC

```shell

# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

E3SM_ROOT=/pscratch/sd/w/whannah/tmp_e3sm_src
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
DATA_ROOT=/global/cfs/cdirs/m4310/whannah
TOPO_ROOT=/global/cfs/cdirs/m4310/whannah/files_topo
GRID_ROOT=${DATA_ROOT}/files_grid
MAPS_ROOT=${DATA_ROOT}/files_map

eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)

cd /global/cfs/cdirs/m4310/whannah


# ### local mac mini paths
# DATA_ROOT=~/E3SM/init_scratch
# GRID_ROOT=${DATA_ROOT}/files_grid
# MAPS_ROOT=${DATA_ROOT}/files_map

```

--------------------------------------------------------------------------------

# Target Grids

```shell
# bi-grids
ne18pg2_IcoswISC30E3r5
ne22pg2_IcoswISC30E3r5
ne26pg2_IcoswISC30E3r5
ne30pg2_IcoswISC30E3r5

# tri-grids
ne18pg2_r05_IcoswISC30E3r5
ne22pg2_r05_IcoswISC30E3r5
ne26pg2_r05_IcoswISC30E3r5
ne30pg2_r05_IcoswISC30E3r5
```

--------------------------------------------------------------------------------

# Grid File Generation

## target model grid files 

```shell
NE=18
# NE=22
# NE=26
# NE=30
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc

```

```shell
NE=18
# NE=22
# NE=26
# NE=30
ncap2 -s 'grid_imask=int(grid_imask)' ${GRID_ROOT}/ne${NE}.g           ${GRID_ROOT}/ne${NE}_tmp.g
ncap2 -s 'grid_imask=int(grid_imask)' ${GRID_ROOT}/ne${NE}pg2_scrip.nc ${GRID_ROOT}/ne${NE}pg2_scrip_tmp.nc

mv ${GRID_ROOT}/ne${NE}_tmp.g           ${GRID_ROOT}/ne${NE}.g
mv ${GRID_ROOT}/ne${NE}pg2_scrip_tmp.nc ${GRID_ROOT}/ne${NE}pg2_scrip.nc

```

## ne3000 grid for topo

```shell
NE_SRC=3000
GenerateCSMesh --alt --res ${NE_SRC} --file ${GRID_ROOT}/exodus_ne${NE_SRC}.g
ConvertMeshToSCRIP --in ${GRID_ROOT}/exodus_ne${NE_SRC}.g  --out ${GRID_ROOT}/scrip_ne${NE_SRC}pg1.nc

ncap2 -s 'grid_imask=int(grid_imask)' ${GRID_ROOT}/scrip_ne3000pg1.nc ${GRID_ROOT}/scrip_ne3000pg1_tmp.nc
mv ${GRID_ROOT}/scrip_ne3000pg1_tmp.nc ${GRID_ROOT}/scrip_ne3000pg1.nc
```
--------------------------------------------------------------------------------

# Domain files

## use new domain file tool

```shell
# NE=18
NE=22
# NE=26
# NE=30

atm_grid_name=ne${NE}pg2
DATESTAMP=20240205

atm_grid_file=${GRID_ROOT}/${atm_grid_name}_scrip.nc
ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/IcoswISC30E3r5/ocean.IcoswISC30E3r5.mask.scrip.20231120.nc
MAP_FILE=${MAPS_ROOT}/map_IcoswISC30E3r5_to_${atm_grid_name}_traave.${DATESTAMP}.nc

# ncremap -a traave --src_grd=${ocn_grid_file} --dst_grd=${atm_grid_file} --map_file=${MAP_FILE}

OUTPUT_ROOT=${DATA_ROOT}/files_domain
python ${E3SM_ROOT}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o IcoswISC30E3r5 -l ${atm_grid_name} --date-stamp=${DATESTAMP} --output-root=${OUTPUT_ROOT}
```

--------------------------------------------------------------------------------

# Topography

## Build `homme_tool`

```shell
# Set the machine specific environment
# ${E3SM_ROOT}/cime/CIME/scripts/configure && source .env_mach_specific.sh

eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)

# cd ${E3SM_ROOT}/components/homme

mkdir ${E3SM_ROOT}/cmake_homme
cd ${E3SM_ROOT}/cmake_homme

# mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/perlmutter-nocuda-gnu.cmake
mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/pm-cpu.cmake

### is this responsible for linking errors????
# cmake -C ${mach_file}  \
# -DBUILD_HOMME_THETA_KOKKOS=FALSE  \
# -DBUILD_HOMME_PREQX_KOKKOS=FALSE  \
# -DHOMME_ENABLE_COMPOSE=FALSE  \
# -DHOMME_BUILD_EXECS=FALSE  \
# -DBUILD_HOMME_TOOL=TRUE  \
# -DBUILD_HOMME_WITHOUT_PIOLIBRARY=FALSE  \
# -DPREQX_PLEV=26  \
# ${E3SM_ROOT}/components/homme

cmake -C ${mach_file}  \
-DBUILD_HOMME_WITHOUT_PIOLIBRARY=OFF \
-DPREQX_PLEV=26  \
${E3SM_ROOT}/components/homme

make -j4 homme_tool
# make homme_tool
# make -j4 homme_tool > make.out 2>&1

```

```shell
# clean up previous homme_tool build
git clean -f 
rm -rf CMakeFiles/ src/preqx/CMakeFiles/ src/preqx_acc/CMakeFiles/ src/sweqx/CMakeFiles/ src/theta-l/CMakeFiles/ src/tool/CMakeFiles/ test/unit_tests/CMakeFiles/ utils/csm_share/CMakeFiles/
rm -rf ${E3SM_ROOT}/cime
rm -rf ${E3SM_ROOT}/externals/scorpio
git submodule sync ; git submodule update --init --recursive
git status
```

## Build `cube_to_target`

```shell
# build cube_to_target
cd ${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target
eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)
make
```

## Generate np4 scrip grid file

```shell
# Generate GLL SCRIP file for target grid: for RRM grids, this SCRIP files are good enough
# for topo downsampling, but not conservative enough for use in the coupled model:
eval $( ${E3SM_ROOT}/cime/CIME/Tools/get_case_env )
homme_tool_root=${E3SM_ROOT}/components/homme/test/tool
cd ${E3SM_ROOT}/components/homme/test/tool

# cmake \
#     -C ${homme_tool_root}/../../cmake/machineFiles/{machine}.cmake \
#     -DBUILD_HOMME_WITHOUT_PIOLIBRARY=OFF \
#     -DPREQX_PLEV=26 ${homme_tool_root}/../../
# make -j4 homme_tool

```

```shell

salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m4310

cd ${E3SM_ROOT}/cmake_homme

NE=18
# NE=22
# NE=26
# NE=30

rm -f input.nl

cat > input.nl <<EOF
&ctl_nl
ne = ${NE}
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

# srun -n 8 ${E3SM_ROOT}/components/homme/src/tool/homme_tool < input.nl
srun -n 8 ${E3SM_ROOT}/cmake_homme/src/tool/homme_tool < input.nl


python ${E3SM_ROOT}/components/homme/test/tool/python/HOMME2SCRIP.py  --src_file ne${NE}np4_tmp1.nc --dst_file ${GRID_ROOT}/scrip_ne${NE}np4.nc

### old method
# # retain specific variables
# ncks -O -v lat,lon,area,cv_lat,cv_lon ne${NE}np4_tmp1.nc ne${NE}np4_tmp.nc
# # make the 'scrip' format file from the HOMME grid output
# ncl ${E3SM_ROOT}/components/homme/test/tool/ncl/HOMME2SCRIP.ncl  name=\"ne${NE}np4\"  ne=${NE}  np=4

#NE=18 ; ncl /pscratch/sd/w/whannah/tmp_e3sm_src/components/homme/test/tool/ncl/HOMME2SCRIP.ncl  name=\"ne${NE}np4\"  ne=${NE}  np=4


```

## Run Topo Tools

```shell
NE=18
# NE=22
# NE=26
# NE=30

atm_grid_name=ne${NE}
DATESTAMP=20240205

NE_SRC=3000

map_file_src_to_np4=${MAPS_ROOT}/map_ne${NE_SRC}pg1_to_${atm_grid_name}np4_fv2se_flx.${DATESTAMP}.nc

# Create map from source to target np4
time ncremap ${MAP_ARGS} -a fv2se_flx \
  --src_grd=${GRID_ROOT}/scrip_ne${NE_SRC}pg1.nc \
  --dst_grd=${GRID_ROOT}/${atm_grid_name}.g \
  --map_file=${map_file_src_to_np4} \
  --tmp_dir=${MAPS_ROOT}
```

```shell
# remap topo with cube_to_target
${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${GRID_ROOT}/scrip_ne${NE_DST}np4.nc \
  --input-topography ${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc \
  --output-topography ${TOPO_ROOT}/tmp_USGS-topo_ne${NE_DST}np4.nc

```

```shell
# Apply Smoothing
cd ${E3SM_ROOT}/cmake_homme

NE=18
# NE=22
# NE=26
# NE=30

topo_file_1=${TOPO_ROOT}/tmp_USGS-topo_ne${NE}np4.nc
topo_file_2=${TOPO_ROOT}/tmp_USGS-topo_ne${NE}np4_smoothedx6t.nc

# Create namelist file for HOMME
cat <<EOF > input.nl
&ctl_nl
mesh_file = "${GRID_ROOT}/ne${NE_DST}.g"
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
srun -n 8 ${E3SM_ROOT}/cmake_homme/src/tool/homme_tool < input.nl

# mv ${TOPO_ROOT}/tmp_USGS-topo_ne${NE}np4_smoothedx6t.nc1.nc ${TOPO_ROOT}/tmp_USGS-topo_ne${NE}np4_smoothedx6t.nc
mv ${topo_file_2}1.nc ${topo_file_2}

```

```shell
# Calculate SGH and topo shape parameters
NE_SRC=3000
NE_DST=18

topo_file_0=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube${NE_SRC}.nc
# topo_file_1=${TOPO_ROOT}/tmp_USGS-topo_ne${NE_DST}np4.nc
topo_file_2=${TOPO_ROOT}/tmp_USGS-topo_ne${NE_DST}np4_smoothedx6t.nc
# topo_file_3=${TOPO_ROOT}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc
timestamp=$(date +%Y%m%d)
topo_file_3=${TOPO_ROOT}/USGS-topo_ne${NE_DST}np4_smoothedx6t_${timestamp}.nc

# Compute SGH with cube_to_target
${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target/cube_to_target \
  --target-grid ${GRID_ROOT}/ne${NE_DST}pg2_scrip.nc \
  --input-topography ${topo_file_0} \
  --smoothed-topography ${topo_file_2} \
  --output-topography ${topo_file_3} \
  --add-oro-shape

# Append the GLL phi_s data to the output
ncks -A ${topo_file_2} ${topo_file_3}

```

```shell

# For testing:
# NE_DST=18 ./batch_topo_slurm_nersc.sh

# NE=18; srun --export=NE_DST=$NE  ~/E3SM/batch_topo_slurm_nersc.sh

# sbatch ~/E3SM/batch_scripts/2025_scidac_batch_homme_tool_test_slurm_nersc.sh

# # run this test when PM comes back online
# NE=22; sbatch ~/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh

# NE=18; sbatch  --job-name=generate_topo_ne${NE}  --export=NE_DST=$NE  ~/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
NE=22; sbatch  --job-name=generate_topo_ne${NE}  --export=NE_DST=$NE  ~/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
NE=26; sbatch  --job-name=generate_topo_ne${NE}  --export=NE_DST=$NE  ~/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
NE=30; sbatch  --job-name=generate_topo_ne${NE}  --export=NE_DST=$NE  ~/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
qjob

# alt commands to run from interactive session
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m4310 
export NE_DST=18; /global/homes/w/whannah/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
export NE_DST=22; /global/homes/w/whannah/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
export NE_DST=26; /global/homes/w/whannah/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh
export NE_DST=30; /global/homes/w/whannah/E3SM/batch_scripts/2025_scidac_batch_topo_slurm_nersc.sh

```

```shell
export NE=18 ; bash ~/E3SM/batch_topo_slurm_nersc.sh
```

--------------------------------------------------------------------------------

# Dry Deposition File

```shell
mkdir ${DATA_ROOT}/files_atmsrf

# NE=18
# NE=22
# NE=26
NE=30

atm_grid_name=ne${NE}pg2
DATESTAMP=20240205
DST_GRID=${GRID_ROOT}/${atm_grid_name}_scrip.nc
SRC_GRID=${DIN_LOC_ROOT}/../mapping/grids/1x1d.nc
MAP_FILE=${MAPS_ROOT}/map_1x1_to_${atm_grid_name}_traave.${DATESTAMP}.nc
# ncremap -5 -a traave --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}

VEGE_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/regrid_vegetation.nc
SOIL_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/clim_soilw.nc

python ${E3SM_ROOT}/components/eam/tools/mkatmsrffile/mkatmsrffile.py --map_file=${MAP_FILE} --vegetation_file=${VEGE_FILE} --soil_water_file=${SOIL_FILE} --output_root=${DATA_ROOT}/files_atmsrf --dst_grid=${atm_grid_name}-pg2 --date-stamp=${DATESTAMP}

```

--------------------------------------------------------------------------------

# Land Input (fsurdat)

```shell
# NE=18
NE=22
# NE=26
# NE=30

atm_grid_name=ne${NE}pg2

DATESTAMP=20240205
# DATESTAMP=20250601
GRID_FILE=${GRID_ROOT}/${atm_grid_name}_scrip.nc

mkdir ${DATA_ROOT}/files_fsurdat
cd ${DATA_ROOT}/files_fsurdat

```

## mkmapdata.sh

```shell

### don't use this!!! (2025-05-29)
# cd ${DATA_ROOT}/files_fsurdat
# ${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name} --gridtype global --output-filetype 64bit_offset --debug -v --list
# # change HYDRO file to SCRIP format version
# sed -i  's/UGRID_1km-merge-10min_HYDRO1K-merge-nomask_c130402.nc/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc/' clm.input_data_list
# ${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name} --gridtype global --output-filetype 64bit_offset -v
# # nohup ${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset -v > mkmapdata.out &

# Use this script instead!
python ~/E3SM/create_fsurdat_maps.py

# and then create the namelist with this:
python ~/E3SM/create_fsurdat_namelist.py

```

## Build mksurfdata_map

```shell
# 
cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map/src

eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)

# make clean
# export LIB_NETCDF="`nc-config --libdir`" 
# export INC_NETCDF="`nf-config --includedir`"
# export USER_LDFLAGS="`nf-config --flibs`"
# export USER_FC=gfortran
# export USER_CC=gcc
# export USER_FFLAGS="-ffree-line-length-none -fallow-argument-mismatch -fallow-invalid-boz" 
# # export LD_LIBRARY_PATH="$LIB_NETCDF:$LD_LIBRARY_PATH"
# make

# this worked as of May 29, 2025
make clean
export LIB_NETCDF="`nc-config --libdir`" 
export INC_NETCDF="`nf-config --includedir`"
export USER_LDFLAGS="`nf-config --flibs`"
export USER_FC=ifort
export USER_CC=icc
export USER_FFLAGS="-I/opt/cray/libfabric/1.20.1/include"
export USER_LDFLAGS="-L${LIB_NETCDF} -lnetcdf -lnetcdff -L/opt/cray/libfabric/1.20.1/lib64 -lfabric "
make

# echo; echo LIB_NETCDF   : $LIB_NETCDF; echo USER_LDFLAGS : $USER_LDFLAGS; echo
# unset LD_LIBRARY_PATH
# export LD_LIBRARY_PATH="$LIB_NETCDF:$LD_LIBRARY_PATH"

```


```shell
# alt build for testing
E3SM_ROOT=/pscratch/sd/w/whannah/tmp_v3HR_src

cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map/src

eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)

make clean
export LIB_NETCDF="`nc-config --libdir`" 
export INC_NETCDF="`nf-config --includedir`"
export USER_LDFLAGS="`nf-config --flibs`"
export USER_FC=ifort
export USER_CC=icc
export USER_FFLAGS="-I/opt/cray/libfabric/1.20.1/include"
export USER_LDFLAGS="-L${LIB_NETCDF} -lnetcdf -lnetcdff -L/opt/cray/libfabric/1.20.1/lib64 -lfabric "
make

```

## mksurfdata.pl - "debug" to generate namelist

```shell
# cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map


cd ${DATA_ROOT}/files_fsurdat

${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata.pl \
-res usrspec -usr_gname ${atm_grid_name} \
-usr_gdate ${DATESTAMP} -y 2010 -d \
-dinlc ${DIN_LOC_ROOT} \
-usr_mapdir ${DATA_ROOT}/files_fsurdat \
-exedir ${E3SM_ROOT}/components/elm/tools/mksurfdata_map 

```

## Create fsurdat

```shell

# ${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata_map < ${DATA_ROOT}/files_fsurdat/namelist

${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata_map < ${DATA_ROOT}/files_fsurdat/fsurdat_namelist_ne18pg2

```

```shell
NE=18
# NE=22
# NE=26
# NE=30

cd ${DATA_ROOT}/files_fsurdat
rm -f mksurfdata_map_ne${NE}.bash
cat <<EOF >> mksurfdata_map_ne${NE}.bash
#!/bin/bash
#SBATCH --account=m4310
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=mksurfdata_map_ne${NE}
#SBATCH --output=slurm.mksurfdata_map_ne${NE}.o%j
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL

eval \$(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)

# mksurfdata_map is dynamically linked
export LIB_NETCDF="`nc-config --libdir`" 
export INC_NETCDF="`nf-config --includedir`"
export USER_LDFLAGS="`nf-config --flibs`"
export USER_FC=ifort
export USER_CC=icc
export USER_FFLAGS="-I/opt/cray/libfabric/1.20.1/include"
export USER_LDFLAGS="-L${LIB_NETCDF} -lnetcdf -lnetcdff -L/opt/cray/libfabric/1.20.1/lib64 -lfabric "

# set LD_LIBRARY_PATH to get rid of this error:
# mksurfdata_map: error while loading shared libraries: libnetcdff.so.7: cannot open shared object file: No such file or directory
export LD_LIBRARY_PATH="\$LIB_NETCDF:\$LD_LIBRARY_PATH"

CDATE=$DATESTAMP

${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata_map < ${DATA_ROOT}/files_fsurdat/fsurdat_namelist_ne${NE}pg2

EOF
sbatch mksurfdata_map_ne${NE}.bash
```


```shell
# cd ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}
# rm -f mksurfdata_map_ne${BASE_RES}.bash
# cat <<EOF >> mksurfdata_map_ne${BASE_RES}.bash
# #!/bin/bash
# #SBATCH  --job-name=mksurfdata_map_ne${BASE_RES}
# #SBATCH  --account=nhclilab
# #SBATCH  --nodes=1
# #SBATCH  --output=slurm.mksurfdata_map_ne${BASE_RES}.o%j
# #SBATCH  --time=02:00:00

# source /p/lustre1/hannah6/anaconda3/bin/activate e3sm-unified

# # mksurfdata_map is dynamically linked
# export LIB_NETCDF=`nc-config --libdir`
# export INC_NETCDF=`nf-config --includedir`
# export USER_LDFLAGS=`nf-config --flibs`
# export USER_FC=ifort
# export USER_CC=icc

# # set LD_LIBRARY_PATH to get rid of this error:
# # mksurfdata_map: error while loading shared libraries: libnetcdff.so.7: cannot open shared object file: No such file or directory
# export LD_LIBRARY_PATH="$LIB_NETCDF:$LD_LIBRARY_PATH"

# # echo
# # which nc-config
# # echo
# # echo nc-config --libdir : `nc-config --libdir`
# # echo LIB_NETCDF=$LIB_NETCDF
# # echo INC_NETCDF=$INC_NETCDF
# # echo LD_LIBRARY_PATH=$LD_LIBRARY_PATH

# # CDATE=c`date +%y%m%d` # current date
# CDATE=$DATESTAMP

# # cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map
# # ./mksurfdata_map < ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}/namelist
# # mv surfdata_2024-nimbus-iraq-${BASE_RES}x3-pg2_simyr2010* ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}/

# ${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata_map < namelist

# EOF
# sbatch mksurfdata_map_ne${BASE_RES}.bash
```

```shell
# https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata/

cd /p/lustre1/hannah6/2024-nimbus-iraq-data/tmp_inputdata/lnd/clm2/rawdata

# wget --no-host-directories --recursive --no-parent --reject="index.html*" https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata

nohup wget --mirror --execute robots=off --no-host-directories --cut-dirs=5 --no-parent --reject="index.html*" https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata > wget.out & 
# nohup wget --no-clobber --recursive --execute robots=off --no-host-directories --cut-dirs=5 --no-parent --reject="index.html*" https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata > wget.out & 

# wget --recursive --no-parent --execute robots=off --no-host-directories --reject="index.html*"  https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata/LUT_LUH2_HIST_LUH1f_07082020

wget https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata/LUT_LUH2_HIST_LUH1f_07082020/LUT_LUH2_historical_1850_c07082020.nc

wget https://web.lcrc.anl.gov/public/e3sm/inputdata/lnd/clm2/rawdata/mksrf_vocef_0.5x0.5_simyr2000.c110531.nc

chmod go+r /usr/gdata/e3sm/ccsm3data/inputdata/lnd/clm2/rawdata/*

# scp /lcrc/group/acme/public_html/inputdata/lnd/clm2/rawdata/

scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/rawdata/*.nc /p/lustre1/hannah6/2024-nimbus-iraq-data/tmp_inputdata/lnd/clm2/rawdata/

scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/rawdata/LUT_LUH2_HIST_LUH1f_07082020/*2010* /p/lustre1/hannah6/2024-nimbus-iraq-data/tmp_inputdata/lnd/clm2/rawdata/LUT_LUH2_HIST_LUH1f_07082020/


wget https://web.lcrc.anl.gov/public/e3sm/inputdata/cpl/cpl6/map_r0125_to_ICOS10_smoothed.r50e100.220302.nc /usr/gdata/e3sm/ccsm3data/inputdata/cpl/cpl6/

scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/cpl/cpl6/map_r0125_to_ICOS10_smoothed.r50e100.220302.nc /usr/gdata/e3sm/ccsm3data/inputdata/cpl/cpl6/

scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/cpl/cpl6/map_r0125_to_ICOS10_smoothed.r50e100.220302.nc /p/lustre1/hannah6/2024-nimbus-iraq-data/files_map


```

--------------------------------------------------------------------------------

# Coupler Mapping Files

## OCN maps

```shell atm/ocn
# NE=18
NE=22
# NE=26
# NE=30

atm_grid_name=ne${NE}pg2
DATESTAMP=20240205
atm_grid_file=${GRID_ROOT}/${atm_grid_name}_scrip.nc
ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/IcoswISC30E3r5/ocean.IcoswISC30E3r5.mask.scrip.20231120.nc
cd ${MAPS_ROOT}
time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=IcoswISC30E3r5 --nm_dst=${atm_grid_name} --dt_sng=${DATESTAMP}
# nohup time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=ICOS10 --nm_dst=${atm_grid_name} --dt_sng=${DATESTAMP} > log.ne${NE}pg2 & 
```

https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/178848194/Recommended+Mapping+Procedures+for+E3SM+Atmosphere+Grids#RecommendedMappingProceduresforE3SMAtmosphereGrids-E3SMv2withpg2

## ROF maps - r05

```shell
NE=30 # 18 / 22 / 26 / 30
DATESTAMP=20240205
atm_grid_name=ne${NE}pg2
rof_grid_name=r05
atm_grid_file=${GRID_ROOT}/${atm_grid_name}_scrip.nc
rof_grid_file=${DIN_LOC_ROOT}/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc

map_file_A2R=${MAPS_ROOT}/map_${atm_grid_name}_to_${rof_grid_name}_trfv2.${DATESTAMP}.nc
map_file_R2A=${MAPS_ROOT}/map_${rof_grid_name}_to_${atm_grid_name}_trfv2.${DATESTAMP}.nc
ncremap --alg_typ=trfv2 --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap --alg_typ=trfv2 --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A

# map_file_A2R=${MAPS_ROOT}/map_${atm_grid_name}_to_${rof_grid_name}_mono.${DATESTAMP}.nc
# map_file_R2A=${MAPS_ROOT}/map_${rof_grid_name}_to_${atm_grid_name}_mono.${DATESTAMP}.nc
# map_opts="--wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'"
# ncremap -a tempest --a2o --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R} ${map_opts}
# ncremap -a tempest       --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A} ${map_opts}

# map_file_A2R=${MAPS_ROOT}/map_${atm_grid_name}_to_${rof_grid_name}_traave.${DATESTAMP}.nc
# map_file_R2A=${MAPS_ROOT}/map_${rof_grid_name}_to_${atm_grid_name}_traave.${DATESTAMP}.nc
# ncremap -a tempest --a2o --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
# ncremap -a tempest       --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
# ls -l $map_file_A2R $map_file_R2A


map_file_A2R=${MAPS_ROOT}/map_${atm_grid_name}_to_${rof_grid_name}_traave.${DATESTAMP}.nc
map_file_R2A=${MAPS_ROOT}/map_${rof_grid_name}_to_${atm_grid_name}_traave.${DATESTAMP}.nc
ncremap -a traave --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap -a traave --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A


map_file_A2R=${MAPS_ROOT}/map_${atm_grid_name}_to_${rof_grid_name}_trbilin.${DATESTAMP}.nc
map_file_R2A=${MAPS_ROOT}/map_${rof_grid_name}_to_${atm_grid_name}_trbilin.${DATESTAMP}.nc
ncremap -a trbilin --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap -a trbilin --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A



```

--------------------------------------------------------------------------------

# XML grid definition

## cime_config/config_grids.xml

### bi-grid

```xml
    <model_grid alias="ne18pg2_IcoswISC30E3r5">
      <grid name="atm">ne18np4.pg2</grid>
      <grid name="lnd">ne18np4.pg2</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>

    <model_grid alias="ne22pg2_IcoswISC30E3r5">
      <grid name="atm">ne22np4.pg2</grid>
      <grid name="lnd">ne22np4.pg2</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>

    <model_grid alias="ne26pg2_IcoswISC30E3r5">
      <grid name="atm">ne26np4.pg2</grid>
      <grid name="lnd">ne26np4.pg2</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>

    <model_grid alias="ne30pg2_IcoswISC30E3r5">
      <grid name="atm">ne30np4.pg2</grid>
      <grid name="lnd">ne30np4.pg2</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>
```

```xml

    <domain name="ne18np4.pg2">
      <nx>7776</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne18pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne18pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne18pg2</desc>
    </domain>

    <domain name="ne22np4.pg2">
      <nx>11616</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne22pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne22pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne22pg2</desc>
    </domain>

    <domain name="ne26np4.pg2">
      <nx>16224</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne26pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne26pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne26pg2</desc>
    </domain>

    <domain name="ne30np4.pg2">
      <nx>21600</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne30pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne30pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne30pg2</desc>
    </domain>

```

### tri-grid

```xml
    <!--=====================================================================-->
    <!-- 2025 SciDAC grids for multi-fidelity study  -->
    <model_grid alias="ne18pg2_r05_IcoswISC30E3r5">
      <grid name="atm">ne18np4.pg2</grid>
      <grid name="lnd">r05</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>
    <model_grid alias="ne22pg2_r05_IcoswISC30E3r5">
      <grid name="atm">ne22np4.pg2</grid>
      <grid name="lnd">r05</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>
    <model_grid alias="ne26pg2_r05_IcoswISC30E3r5">
      <grid name="atm">ne26np4.pg2</grid>
      <grid name="lnd">r05</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>
    <model_grid alias="ne30pg2_r05_IcoswISC30E3r5">
      <grid name="atm">ne30np4.pg2</grid>
      <grid name="lnd">r05</grid>
      <grid name="ocnice">IcoswISC30E3r5</grid>
      <grid name="rof">r05</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>IcoswISC30E3r5</mask>
    </model_grid>
    <!--=====================================================================-->
```

```xml

    <!--=====================================================================-->
    <!-- 2025 SciDAC grids for multi-fidelity study  -->
    <domain name="ne18np4.pg2">
      <nx>7776</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne18pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne18pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne18pg2</desc>
    </domain>
    <domain name="ne22np4.pg2">
      <nx>11616</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne22pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne22pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne22pg2</desc>
    </domain>
    <domain name="ne26np4.pg2">
      <nx>16224</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne26pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne26pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne26pg2</desc>
    </domain>
    <domain name="ne30np4.pg2">
      <nx>21600</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.lnd.ne30pg2_IcoswISC30E3r5.20240205.nc</file>
      <file grid="ice|ocn" mask="IcoswISC30E3r5">/global/cfs/cdirs/m4310/whannah/files_domain/domain.ocn.ne30pg2_IcoswISC30E3r5.20240205.nc</file>
      <desc>ne30pg2</desc>
    </domain>

```

```xml
    <!--=====================================================================-->
    <!-- 2025 SciDAC grids for multi-fidelity study  -->
    <!--=====================================================================-->
    <!-- ne18 -->
    <gridmap atm_grid="ne18np4.pg2" ocn_grid="IcoswISC30E3r5">
      <map name="ATM2OCN_FMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_IcoswISC30E3r5_traave.20240205.nc</map>
      <map name="ATM2OCN_VMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_IcoswISC30E3r5_trbilin.20240205.nc</map>
      <map name="ATM2OCN_SMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_IcoswISC30E3r5_trbilin.20240205.nc</map>
      <map name="OCN2ATM_FMAPNAME"          >cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne18pg2_traave.20240205.nc</map>
      <map name="OCN2ATM_SMAPNAME"          >cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne18pg2_traave.20240205.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne18pg2/map_ne18pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne18pg2/map_ne18pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne18np4.pg2" lnd_grid="r05">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trbilin.20240205.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne18pg2/map_r05_to_ne18pg2_traave.20240205.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne18pg2/map_r05_to_ne18pg2_traave.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne18np4.pg2" rof_grid="r05">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trbilin.20240205.nc</map>
    </gridmap>
    <!--=====================================================================-->
    <!-- ne22 -->
    <gridmap atm_grid="ne22np4.pg2" ocn_grid="IcoswISC30E3r5">
      <map name="ATM2OCN_FMAPNAME">cpl/gridmaps/ne22pg2/map_ne22pg2_to_IcoswISC30E3r5_traave.20240205.nc</map>
      <map name="ATM2OCN_VMAPNAME">cpl/gridmaps/ne22pg2/map_ne22pg2_to_IcoswISC30E3r5_trbilin.20240205.nc</map>
      <map name="ATM2OCN_SMAPNAME">cpl/gridmaps/ne22pg2/map_ne22pg2_to_IcoswISC30E3r5-nomask_trbilin.20240205.nc</map>
      <map name="OCN2ATM_FMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne22pg2_traave.20240205.nc</map>
      <map name="OCN2ATM_SMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne22pg2_traave.20240205.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne22pg2/map_ne22pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne22pg2/map_ne22pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne22np4.pg2" lnd_grid="r05">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_trbilin.20240205.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne22pg2/map_r05_to_ne22pg2_traave.20240205.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne22pg2/map_r05_to_ne22pg2_traave.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne22np4.pg2" rof_grid="r05">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne22pg2/map_ne22pg2_to_r05_trbilin.20240205.nc</map>
    </gridmap>
    <!--=====================================================================-->
    <!-- ne26 -->
    <gridmap atm_grid="ne26np4.pg2" ocn_grid="IcoswISC30E3r5">
      <map name="ATM2OCN_FMAPNAME">cpl/gridmaps/ne26pg2/map_ne26pg2_to_IcoswISC30E3r5_traave.20240205.nc</map>
      <map name="ATM2OCN_VMAPNAME">cpl/gridmaps/ne26pg2/map_ne26pg2_to_IcoswISC30E3r5_trbilin.20240205.nc</map>
      <map name="ATM2OCN_SMAPNAME">cpl/gridmaps/ne26pg2/map_ne26pg2_to_IcoswISC30E3r5-nomask_trbilin.20240205.nc</map>
      <map name="OCN2ATM_FMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne26pg2_traave.20240205.nc</map>
      <map name="OCN2ATM_SMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne26pg2_traave.20240205.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne26pg2/map_ne26pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne26pg2/map_ne26pg2_to_IcoswISC30E3r5_trfv2.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne26np4.pg2" lnd_grid="r05">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_trbilin.20240205.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne26pg2/map_r05_to_ne26pg2_traave.20240205.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne26pg2/map_r05_to_ne26pg2_traave.20240205.nc</map>
    </gridmap>
    <gridmap atm_grid="ne26np4.pg2" rof_grid="r05">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_traave.20240205.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_trfv2.20240205.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne26pg2/map_ne26pg2_to_r05_trbilin.20240205.nc</map>
    </gridmap>
    <!--=====================================================================-->
    <!-- ne30 -->
    <gridmap atm_grid="ne30np4.pg2" ocn_grid="IcoswISC30E3r5">
      <map name="ATM2OCN_FMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_IcoswISC30E3r5_traave.20231121.nc</map>
      <map name="ATM2OCN_VMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_IcoswISC30E3r5_trbilin.20231121.nc</map>
      <map name="ATM2OCN_SMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_IcoswISC30E3r5-nomask_trbilin.20231121.nc</map>
      <map name="OCN2ATM_FMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne30pg2_traave.20231121.nc</map>
      <map name="OCN2ATM_SMAPNAME">cpl/gridmaps/IcoswISC30E3r5/map_IcoswISC30E3r5_to_ne30pg2_traave.20231121.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne30pg2/map_ne30pg2_to_IcoswISC30E3r5_trfvnp2.20231121.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne30pg2/map_ne30pg2_to_IcoswISC30E3r5_trfvnp2.20231121.nc</map>
    </gridmap>
    <gridmap atm_grid="ne30np4.pg2" lnd_grid="r05">
      <map name="ATM2LND_FMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc</map>
      <map name="ATM2LND_SMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trbilin.20231130.nc</map>
      <map name="LND2ATM_FMAPNAME">cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_traave.20231130.nc</map>
      <map name="LND2ATM_SMAPNAME">cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_traave.20231130.nc</map>
    </gridmap>
    <gridmap atm_grid="ne30np4.pg2" rof_grid="r05">
      <map name="ATM2ROF_FMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc</map>
      <map name="ATM2ROF_SMAPNAME">cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trbilin.20231130.nc</map>
    </gridmap>
    <!--=====================================================================-->

```

## components/eam/bld/config_files/horiz_grid.xml

```xml
<!--=====================================================================-->
<!-- 2025 SciDAC grids for multi-fidelity study  -->
<horiz_grid dyn="se"    hgrid="ne18np4.pg2"  ncol="7776"    csne="18"  csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne22np4.pg2"  ncol="11616"   csne="22"  csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne26np4.pg2"  ncol="16224"   csne="26"  csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne30np4.pg2"  ncol="21600"   csne="30"  csnp="4" npg="2" />
<!--=====================================================================-->
```

## components/eam/bld/namelist_files/namelist_defaults_eam.xml
<!-- ## components/eamxx/cime_config/namelist_defaults_scream.xml -->

```xml

<!--=====================================================================-->
<!-- 2025 SciDAC grids for multi-fidelity study  -->

<ncdata dyn="se" hgrid="ne18np4"  nlev="80"  ic_ymd="101" >atm/cam/inic/homme/eami_mam4_Linoz_ne30np4_L80_c20231010.nc</ncdata>
<ncdata dyn="se" hgrid="ne22np4"  nlev="80"  ic_ymd="101" >atm/cam/inic/homme/eami_mam4_Linoz_ne30np4_L80_c20231010.nc</ncdata>
<ncdata dyn="se" hgrid="ne26np4"  nlev="80"  ic_ymd="101" >atm/cam/inic/homme/eami_mam4_Linoz_ne30np4_L80_c20231010.nc</ncdata>
<ncdata dyn="se" hgrid="ne30np4"  nlev="80"  ic_ymd="101" >atm/cam/inic/homme/eami_mam4_Linoz_ne30np4_L80_c20231010.nc</ncdata>

<bnd_topo hgrid="ne18np4" npg="2">atm/cam/topo/USGS-topo_ne18np4_smoothedx6t_20250205.nc</bnd_topo>
<bnd_topo hgrid="ne22np4" npg="2">atm/cam/topo/USGS-topo_ne22np4_smoothedx6t_20250205.nc</bnd_topo>
<bnd_topo hgrid="ne26np4" npg="2">atm/cam/topo/USGS-topo_ne26np4_smoothedx6t_20250205.nc</bnd_topo>

<drydep_srf_file hgrid="ne18np4" npg="2">atm/cam/chem/trop_mam/atm_srf_ne18pg2-pg2_20240205.nc</drydep_srf_file>
<drydep_srf_file hgrid="ne22np4" npg="2">atm/cam/chem/trop_mam/atm_srf_ne22pg2-pg2_20240205.nc</drydep_srf_file>
<drydep_srf_file hgrid="ne26np4" npg="2">atm/cam/chem/trop_mam/atm_srf_ne26pg2-pg2_20240205.nc</drydep_srf_file>
<drydep_srf_file hgrid="ne30np4" npg="2">atm/cam/chem/trop_mam/atm_srf_ne30pg2-pg2_20240205.nc</drydep_srf_file>


<!-- <se_ne hgrid="ne18np4"> 0 </se_ne> -->
<!-- <se_ne hgrid="ne22np4"> 0 </se_ne> -->
<!-- <se_ne hgrid="ne26np4"> 0 </se_ne> -->

<se_tstep            dyn_target="theta-l" hgrid="ne18np4"> 10 </se_tstep>
<se_tstep            dyn_target="theta-l" hgrid="ne22np4"> 10 </se_tstep>
<se_tstep            dyn_target="theta-l" hgrid="ne26np4"> 10 </se_tstep>

<dt_remap_factor     dyn_target="theta-l" hgrid="ne18np4"> 1 </dt_remap_factor>
<dt_remap_factor     dyn_target="theta-l" hgrid="ne22np4"> 1 </dt_remap_factor>
<dt_remap_factor     dyn_target="theta-l" hgrid="ne26np4"> 1 </dt_remap_factor>

<dt_tracer_factor    dyn_target="theta-l" hgrid="ne18np4"> 6 </dt_tracer_factor>
<dt_tracer_factor    dyn_target="theta-l" hgrid="ne22np4"> 6 </dt_tracer_factor>
<dt_tracer_factor    dyn_target="theta-l" hgrid="ne26np4"> 6 </dt_tracer_factor>

<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne18np4"> 6 </hypervis_subcycle_q>
<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne22np4"> 6 </hypervis_subcycle_q>
<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne26np4"> 6 </hypervis_subcycle_q>

<mesh_file hgrid="ne18np4">atm/cam/inic/homme/ne18.g</mesh_file>
<mesh_file hgrid="ne22np4">atm/cam/inic/homme/ne22.g</mesh_file>
<mesh_file hgrid="ne26np4">atm/cam/inic/homme/ne26.g</mesh_file>

<nu_top dyn_target="theta-l" hgrid="ne18np4"> 1e5 </nu_top>
<nu_top dyn_target="theta-l" hgrid="ne22np4"> 1e5 </nu_top>
<nu_top dyn_target="theta-l" hgrid="ne26np4"> 1e5 </nu_top>

<!--=====================================================================-->

```


```xml
<rad_frequency hgrid="ne0np4-2024-nimbus-iraq-128x8">3</rad_frequency>
<number_of_subcycles hgrid="ne0np4-2024-nimbus-iraq-128x8">1</number_of_subcycles>
<Filename hgrid="ne0np4-2024-nimbus-iraq-128x8" nlev="128"></Filename>
<topography_filename hgrid="ne0np4-2024-nimbus-iraq-128x8">/global/cfs/cdirs/m2637/jsgoodni/USGS-gtopo30_Saomai2006ne128x8np4pg2_x6t.nc</topography_filename>
<o3_volume_mix_ratio hgrid="ne0np4-2024-nimbus-iraq-128x8">0.0</o3_volume_mix_ratio>
<hv_ref_profiles hgrid="ne0np4-2024-nimbus-iraq-128x8">0</hv_ref_profiles>
<nu_top hgrid="ne0np4-2024-nimbus-iraq-128x8">1.0e4</nu_top>
<pgrad_correction hgrid="1">0</pgrad_correction>
<se_ne hgrid="ne0np4-2024-nimbus-iraq-128x8">0</se_ne>
<se_tstep hgrid="ne0np4-2024-nimbus-iraq-128x8" constraints="gt 0">8.3333333333333</se_tstep>
<mesh_file hgrid="ne0np4-2024-nimbus-iraq-128x8">/global/cfs/cdirs/m2637/jsgoodni/Saomai_2006_ne128x8_lon130E_lat25N.g</mesh_file>
```

## components/elm/bld/namelist_files/namelist_defaults.xml

```xml
<fsurdat hgrid="ne0np4-2024-nimbus-iraq-128x8.pg2"   sim_year="2010" use_crop=".false." >/global/cfs/cdirs/m2637/jsgoodni/surfdata_Saomai2006ne128x8pg2_simyr2006_c240105.nc</fsurdat>
```

## components/elm/bld/namelist_files/namelist_definition.xml

```xml
???
```

--------------------------------------------------------------------------------

# Commands to copy data for namelist defaults

```shell

cp /global/cfs/cdirs/m4310/whannah/files_topo/USGS-topo_ne18np4_smoothedx6t_20250513.nc   /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/
cp /global/cfs/cdirs/m4310/whannah/files_topo/USGS-topo_ne22np4_smoothedx6t_20250513.nc   /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/
cp /global/cfs/cdirs/m4310/whannah/files_topo/USGS-topo_ne26np4_smoothedx6t_20250513.nc   /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/
cp /global/cfs/cdirs/m4310/whannah/files_topo/USGS-topo_ne30np4_smoothedx6t_20250513.nc   /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/

cp /global/cfs/cdirs/m4310/whannah/files_grid/ne18.g  /global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/
cp /global/cfs/cdirs/m4310/whannah/files_grid/ne22.g  /global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/
cp /global/cfs/cdirs/m4310/whannah/files_grid/ne26.g  /global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/
# cp /global/cfs/cdirs/m4310/whannah/files_grid/ne30.g  /global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/

cp /global/cfs/cdirs/m4310/whannah/files_atmsrf/atm_srf_ne18pg2-pg2_20240205.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/chem/trop_mam/
cp /global/cfs/cdirs/m4310/whannah/files_atmsrf/atm_srf_ne22pg2-pg2_20240205.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/chem/trop_mam/
cp /global/cfs/cdirs/m4310/whannah/files_atmsrf/atm_srf_ne26pg2-pg2_20240205.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/chem/trop_mam/
cp /global/cfs/cdirs/m4310/whannah/files_atmsrf/atm_srf_ne30pg2-pg2_20240205.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/chem/trop_mam/

cp /global/cfs/cdirs/m4310/whannah/files_init/HICCUP.eam_i_mam3_Linoz_ne18np4_L80_c20250530.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/


NE=18 # 18 / 22 / 26 / 30
mkdir -p /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne${NE}pg2
cp /global/cfs/cdirs/m4310/whannah/files_map/map_IcoswISC30E3r5_to_ne${NE}pg2_*  /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/IcoswISC30E3r5/
cp /global/cfs/cdirs/m4310/whannah/files_map/map_ne${NE}pg2_to_IcoswISC30E3r5_*  /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne${NE}pg2/
cp /global/cfs/cdirs/m4310/whannah/files_map/map_ne${NE}pg2_to_r05_*             /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne${NE}pg2/
cp /global/cfs/cdirs/m4310/whannah/files_map/map_r05_to_ne${NE}pg2_*             /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne${NE}pg2/

# NE=18 # 18 / 22 / 26 / 30
# cp /global/cfs/cdirs/m4310/whannah/files_map/map_*_trfv2.*             /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne${NE}pg2/

```


```shell
### what is causing this error???

/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-MF-test-00.ne18pg2.F20TR.NN_8/run/e3sm.log.39288197.250603-145245

  17:  (seq_nlmap_check_matrices) ERROR: low-order map non-0 structure not a subset of
  17:   high-order map non-0 structure: /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/
  17:  ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc /global/cfs/cdirs/e3sm/inputdata/
  17:  cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc


<map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc</map>
<map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc</map>

/global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc
/global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc

/global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc
/global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc


ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc | tail -n 30 
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc  | tail -n 30 
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc | tail -n 30 
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc  | tail -n 30 


ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc | grep ":domain_"
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc  | grep ":domain_"
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc | grep ":domain_"
ncdump -h /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc  | grep ":domain_"

ncks --chk_map /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_traave.20240205.nc | grep "non-zero" -A2
ncks --chk_map /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne18pg2/map_ne18pg2_to_r05_trfv2.20240205.nc  | grep "non-zero" -A2
ncks --chk_map /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_traave.20231130.nc | grep "non-zero" -A2
ncks --chk_map /global/cfs/cdirs/e3sm/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_trfvnp2.230516.nc  | grep "non-zero" -A2


ncks --chk_map /global/cfs/cdirs/m4310/whannah/files_map/map_ne18pg2_to_r05_traave.20240205.nc

```
--------------------------------------------------------------------------------

# Maps for analysis

```shell
DATESTAMP=20240618
atm_grid_name=ne20pg2

ATM_GRID=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc
OBS_GRID=${GRID_ROOT}/MODIS_3600x7200_scrip.nc
MAP_FILE=${MAPS_ROOT}/map_${atm_grid_name}_to_MODIS_3600x7200_traave.${DATESTAMP}.nc

echo $RRM_GRID
echo $OBS_GRID
echo $MAP_FILE
```

```shell
ncremap -G ttl='MODIS grid 3600x7200'#latlon=3600,7200#lat_typ=uni#lon_typ=180_wst -g $OBS_GRID

ncremap -a traave --src_grd=${OBS_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}
```

--------------------------------------------------------------------------------
