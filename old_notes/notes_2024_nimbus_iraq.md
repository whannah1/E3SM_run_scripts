
LC bank: nhclilab

LC interactive job command:

```shell
salloc -A nhclilab -p pbatch -N 1 -t 0:10:00
```

--------------------------------------------------------------------------------
# Important paths 

## LLNL

```shell
# source activate /usr/gdata/e3sm/install/dane/e3sm-unified
conda activate e3sm-unified
DIN_LOC_ROOT=/usr/gdata/e3sm/ccsm3data/inputdata
E3SM_ROOT=${HOME}/E3SM/E3SM_SRC0
DATA_ROOT=/p/lustre1/hannah6/2024-nimbus-iraq-data
GRID_ROOT=${DATA_ROOT}/files_grid
MAPS_ROOT=${DATA_ROOT}/files_map
```

## NERSC

```shell
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
DIN_LOC_ROOT=
E3SM_ROOT=
DATA_ROOT=/global/cfs/cdirs/m3312/whannah
GRID_ROOT=${DATA_ROOT}/files_grid
MAPS_ROOT=${DATA_ROOT}/files_map
```
--------------------------------------------------------------------------------
# sponge layer guidance

https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/2967798203/EAM+Top+of+Model+Sponge+Layer

values used in the run script:

```shell
nu_top = 1e4
tom_sponge_start = 10
```

--------------------------------------------------------------------------------
# Nudging Tutorial

https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/20153276/How+to+perform+nudging+simulations+with+the+regional+refined+model+RRM

--------------------------------------------------------------------------------
# SQuadGen Grid Generation

```shell
BASE_RES=32; REFINE_LVL=3
# BASE_RES=64; REFINE_LVL=3
# BASE_RES=128; REFINE_LVL=3
export GRIDNAME=2024-nimbus-iraq-${BASE_RES}x${REFINE_LVL}
./SQuadGen --refine_rect 35,8,45,52,${REFINE_LVL} --lon_ref 45 --lat_ref 35 --orient_ref 30 --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist 3 --smooth_iter 20 --output ${GRIDNAME}.g
# source activate ncl_env
ncl test/gridplot.ncl
```

```shell
BASE_RES=32;  REFINE_LVL=3
# BASE_RES=64;  REFINE_LVL=3
# BASE_RES=128; REFINE_LVL=3
GRIDNAME=2024-nimbus-iraq-${BASE_RES}x${REFINE_LVL}
# GenerateVolumetricMesh --in ${GRIDNAME}.g --out ${GRIDNAME}_pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRIDNAME}_pg2.g --out ${GRIDNAME}_pg2_scrip.nc
```

Unrefined grids for comparison:

```shell
NE=32
# NE=64
# NE=128
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```

--------------------------------------------------------------------------------
# Coupler Mapping Files

```shell
# BASE_RES=32
# BASE_RES=64
BASE_RES=128
DATESTAMP=20240618
atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3
atm_grid_file=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc
ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
cd ${MAPS_ROOT}
nohup time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=ICOS10 --nm_dst=${atm_grid_name}-pg2 --dt_sng=${DATESTAMP} > log.${atm_grid_name}-pg2 & 
```

--------------------------------------------------------------------------------
# Domain files

```shell
# BASE_RES=32
# BASE_RES=64
BASE_RES=128

atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3
DATESTAMP=20240618

ATM_GRID=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc
OCN_GRID=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
MAP_FILE=${MAPS_ROOT}/map_ICOS10_to_${atm_grid_name}_traave.${DATESTAMP}.nc
ncremap -a traave --src_grd=${OCN_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}

OUTPUT_ROOT=${DATA_ROOT}/files_domain
python ${E3SM_ROOT}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o ICOS10 -l ${atm_grid_name}-pg2 --date-stamp=${DATESTAMP} --output-root=${OUTPUT_ROOT}
```

Unrefined grids for comparison:

```shell
NE=32
# NE=64
# NE=128

DATESTAMP=20240618

ATM_GRID=${GRID_ROOT}/ne${NE}pg2_scrip.nc
OCN_GRID=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
MAP_FILE=${MAPS_ROOT}/map_ICOS10_to_${atm_grid_name}_traave.${DATESTAMP}.nc
ncremap -a traave --src_grd=${OCN_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}

OUTPUT_ROOT=${DATA_ROOT}/files_domain
python ${E3SM_ROOT}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o ICOS10 -l ${atm_grid_name}-pg2 --date-stamp=${DATESTAMP} --output-root=${OUTPUT_ROOT}
```

extra domain file for SST (SSTICE_GRID_FILENAME)

```shell
BASE_RES=32
atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3
DATESTAMP=20240618

ATM_GRID=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc
OCN_GRID=${DATA_ROOT}/scrip_1800x3600_s2n.nc
MAP_FILE=${MAPS_ROOT}/map_ICOS10_to_${atm_grid_name}_traave.${DATESTAMP}.nc
# ncremap -a traave --src_grd=${OCN_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}

OUTPUT_ROOT=${DATA_ROOT}/files_domain
python ${E3SM_ROOT}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o 1800x3600 -l ${atm_grid_name}-pg2 --date-stamp=${DATESTAMP} --output-root=${OUTPUT_ROOT}
```

--------------------------------------------------------------------------------
# Topography

```shell
# Set the machine specific environment
cd ${E3SM_ROOT}/components/homme
${E3SM_ROOT}/cime/CIME/scripts/configure && source .env_mach_specific.sh
# mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/quartz-intel.cmake
mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/dane-intel.cmake
# mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/perlmutter-gnu.cmake
# mach_file=${e3sm_root}/components/homme/cmake/machineFiles/chrysalis.cmake
cmake -C ${mach_file}  -DBUILD_HOMME_THETA_KOKKOS=FALSE  -DBUILD_HOMME_PREQX_KOKKOS=FALSE  -DHOMME_ENABLE_COMPOSE=FALSE  -DHOMME_BUILD_EXECS=FALSE  -DBUILD_HOMME_TOOL=TRUE  -DBUILD_HOMME_WITHOUT_PIOLIBRARY=FALSE  -DPREQX_PLEV=26  ${E3SM_ROOT}/components/homme
make -j4 homme_tool
```

```shell
cd ${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target
${E3SM_ROOT}/cime/CIME/scripts/configure && source .env_mach_specific.sh
make
```

```shell
NE_SRC=3000
GenerateCSMesh --alt --res ${NE_SRC} --file ${GRID_ROOT}/exodus_ne${NE_SRC}.g
ConvertMeshToSCRIP --in ${GRID_ROOT}/exodus_ne${NE_SRC}.g  --out ${GRID_ROOT}/scrip_ne${NE_SRC}pg1.nc
```

```shell
# BASE_RES=32
BASE_RES=64
# BASE_RES=128

DATESTAMP=20240618

atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3

map_file_src_to_np4=${map_root}/map_ne${NE_SRC}pg1_to_${atm_grid_name}-np4_fv2se_flx.${DATESTAMP}.nc

# Create map from source to target np4
time ncremap ${MAP_ARGS} -a fv2se_flx \
  --src_grd=${grid_root}/scrip_ne${NE_SRC}pg1.nc \
  --dst_grd=${grid_root}/${atm_grid_name}.g \
  --map_file=${map_file_src_to_np4} \
  --tmp_dir=${map_root}
```

```shell
BASE_RES=32 ; sbatch  --job-name=generate_topo_${BASE_RES}  --export=BASE_RES=$BASE_RES  ~/E3SM/batch_topo_slurm_llnl.sh
BASE_RES=64 ; sbatch  --job-name=generate_topo_${BASE_RES}  --export=BASE_RES=$BASE_RES  ~/E3SM/batch_topo_slurm_llnl.sh
BASE_RES=128; sbatch  --job-name=generate_topo_${BASE_RES}  --export=BASE_RES=$BASE_RES  ~/E3SM/batch_topo_slurm_llnl.sh
```

```shell
export BASE_RES=32 ; bash ~/E3SM/batch_topo_slurm_llnl.sh
export BASE_RES=64 ; bash ~/E3SM/batch_topo_slurm_llnl.sh
export BASE_RES=128; bash ~/E3SM/batch_topo_slurm_llnl.sh
```

--------------------------------------------------------------------------------
# Dry Deposition File

```shell
scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/mapping/grids/1x1d.nc /usr/gdata/e3sm/ccsm3data/mapping/grids/
```

```shell
# BASE_RES=32
# BASE_RES=64
BASE_RES=128
DATESTAMP=20240618
atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3
DST_GRID=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc
SRC_GRID=${DIN_LOC_ROOT}/../mapping/grids/1x1d.nc
MAP_FILE=${MAPS_ROOT}/map_1x1_to_${atm_grid_name}-pg2_traave.${DATESTAMP}.nc
ncremap -5 -a traave --src_grd=${SRC_GRID} --dst_grd=${DST_GRID} --map_file=${MAP_FILE}

VEGE_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/regrid_vegetation.nc
SOIL_FILE=${DIN_LOC_ROOT}/atm/cam/chem/trop_mozart/dvel/clim_soilw.nc

python ${HOME}/E3SM/E3SM_SRC1/components/eam/tools/mkatmsrffile/mkatmsrffile.py --map_file=${MAP_FILE} --vegetation_file=${VEGE_FILE} --soil_water_file=${SOIL_FILE} --output_root=${DATA_ROOT}/files_atmsrf --dst_grid=${atm_grid_name}-pg2 --date-stamp=${DATESTAMP}
```

--------------------------------------------------------------------------------
# Land Input (fsurdat)

```shell
# BASE_RES=32
# BASE_RES=64
BASE_RES=128
DATESTAMP=20240618
atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3
GRID_FILE=${GRID_ROOT}/${atm_grid_name}_pg2_scrip.nc

# mkdir ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}
cd ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}
```

```shell
cd ${E3SM_ROOT}/components/elm/tools/mkmapdata
./mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset --debug -v --list
# change HYDRO file to SCRIP format version
sed -i  's/UGRID_1km-merge-10min_HYDRO1K-merge-nomask_c130402.nc/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc/' clm.input_data_list

# might need to run this in the background
./mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset -v
```

```shell

${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset --debug -v --list

# change HYDRO file to SCRIP format version
sed -i  's/UGRID_1km-merge-10min_HYDRO1K-merge-nomask_c130402.nc/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc/' clm.input_data_list

${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset -v

# nohup ${E3SM_ROOT}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${GRID_FILE} --inputdata-path ${DIN_LOC_ROOT} --res ${atm_grid_name}-pg2 --gridtype global --output-filetype 64bit_offset -v > mkmapdata.out &
```


Run the mksurfdata.pl script in "debug" mode to generate the namelist

```shell
# cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map
# MAP_DATESTAMP=240624
MAP_DATESTAMP=240701

DIN_LOC_ROOT_TMP=/p/lustre1/hannah6/2024-nimbus-iraq-data/tmp_inputdata

${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata.pl -res usrspec -usr_gname ${atm_grid_name}-pg2 -usr_gdate ${MAP_DATESTAMP} -y 2010 -d -dinlc ${DIN_LOC_ROOT_TMP} -usr_mapdir ${DATA_ROOT}/files_fsurdat_ne${BASE_RES} -exedir ${E3SM_ROOT}/components/elm/tools/mksurfdata_map 
```



```shell
# Build mksurfdata_map
cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map/src

make clean
export LIB_NETCDF="`nc-config --libdir`" 
export INC_NETCDF="`nf-config --includedir`"
export USER_LDFLAGS="`nf-config --flibs`"
export USER_FC=gfortran
export USER_CC=gcc
export USER_FFLAGS="-ffree-line-length-none -fallow-argument-mismatch -fallow-invalid-boz" 
make

make clean
export LIB_NETCDF="`nc-config --libdir`" 
export INC_NETCDF="`nf-config --includedir`"
export USER_LDFLAGS="`nf-config --flibs`"
export USER_FC=ifort
export USER_CC=icc
unset USER_FFLAGS
export LD_LIBRARY_PATH="$LIB_NETCDF:$LD_LIBRARY_PATH"
make

# to test:
# ../mksurfdata_map
../mksurfdata_map < ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}/namelist

```


Create the land surface data by interactive or batch job

```shell
cd ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}
rm -f mksurfdata_map_ne${BASE_RES}.bash
cat <<EOF >> mksurfdata_map_ne${BASE_RES}.bash
#!/bin/bash
#SBATCH  --job-name=mksurfdata_map_ne${BASE_RES}
#SBATCH  --account=nhclilab
#SBATCH  --nodes=1
#SBATCH  --output=slurm.mksurfdata_map_ne${BASE_RES}.o%j
#SBATCH  --time=02:00:00

source /p/lustre1/hannah6/anaconda3/bin/activate e3sm-unified

# mksurfdata_map is dynamically linked
export LIB_NETCDF=`nc-config --libdir`
export INC_NETCDF=`nf-config --includedir`
export USER_LDFLAGS=`nf-config --flibs`
export USER_FC=ifort
export USER_CC=icc

# set LD_LIBRARY_PATH to get rid of this error:
# mksurfdata_map: error while loading shared libraries: libnetcdff.so.7: cannot open shared object file: No such file or directory
export LD_LIBRARY_PATH="$LIB_NETCDF:$LD_LIBRARY_PATH"

echo
which nc-config
echo
echo nc-config --libdir : `nc-config --libdir`
echo LIB_NETCDF=$LIB_NETCDF
echo INC_NETCDF=$INC_NETCDF
echo LD_LIBRARY_PATH=$LD_LIBRARY_PATH

# CDATE=c`date +%y%m%d` # current date
CDATE=$DATESTAMP

# cd ${E3SM_ROOT}/components/elm/tools/mksurfdata_map
# ./mksurfdata_map < ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}/namelist
# mv surfdata_2024-nimbus-iraq-${BASE_RES}x3-pg2_simyr2010* ${DATA_ROOT}/files_fsurdat_ne${BASE_RES}/

${E3SM_ROOT}/components/elm/tools/mksurfdata_map/mksurfdata_map < namelist

EOF
sbatch mksurfdata_map_ne${BASE_RES}.bash
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
# Land Initial Condition

```shell
```

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
# Coupler Mapping Files

https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/178848194/Recommended+Mapping+Procedures+for+E3SM+Atmosphere+Grids#RecommendedMappingProceduresforE3SMAtmosphereGrids-E3SMv2withpg2

## ROF map files - r0125

```shell
ATM_GRID_NAME=ne0np4-2024-nimbus-iraq-128x8
ROF_GRID_NAME=r0125
ATM_GRID=/global/cfs/cdirs/m2637/jsgoodni/Saomai_2006_ne128x8_lon130E_lat25Npg2.scrip.nc
ROF_GRID=/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.125x0.125_nomask_c170126.nc # file has clockwise elements?
MAP_FILE1=/global/cfs/cdirs/m2637/whannah/map_${ATM_GRID_NAME}_to_${ROF_GRID_NAME}_mono.20240108.nc
MAP_FILE2=/global/cfs/cdirs/m2637/whannah/map_${ROF_GRID_NAME}_to_${ATM_GRID_NAME}_mono.20240108.nc
ncremap -a tempest --a2o --src_grd=${ATM_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE1} --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
ncremap -a tempest       --src_grd=${ROF_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE2} --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
ls -l $MAP_FILE1 $MAP_FILE2

MAP_FILE1=/global/cfs/cdirs/m2637/whannah/map_${ATM_GRID_NAME}_to_${ROF_GRID_NAME}_bilinear.20240108.nc
MAP_FILE2=/global/cfs/cdirs/m2637/whannah/map_${ROF_GRID_NAME}_to_${ATM_GRID_NAME}_bilinear.20240108.nc
ncremap -a nco_idw --src_grd=${ATM_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE1}
ncremap -a nco_idw --src_grd=${ROF_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE2}
ls -l $MAP_FILE1 $MAP_FILE2
```

--------------------------------------------------------------------------------
# Grid definition

## cime_config/config_grids.xml

```xml
    <model_grid alias="ne0np4-2024-nimbus-iraq-32x3-pg2">
      <grid name="atm">ne0np4-2024-nimbus-iraq-32x3.pg2</grid>
      <grid name="lnd">ne0np4-2024-nimbus-iraq-32x3.pg2</grid>
      <grid name="ocnice">ICOS10</grid>
      <grid name="rof">r0125</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>ICOS10</mask>
    </model_grid>

    <model_grid alias="ne0np4-2024-nimbus-iraq-64x3-pg2">
      <grid name="atm">ne0np4-2024-nimbus-iraq-64x3.pg2</grid>
      <grid name="lnd">ne0np4-2024-nimbus-iraq-64x3.pg2</grid>
      <grid name="ocnice">ICOS10</grid>
      <grid name="rof">r0125</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>ICOS10</mask>
    </model_grid>

    <model_grid alias="ne0np4-2024-nimbus-iraq-128x3-pg2">
      <grid name="atm">ne0np4-2024-nimbus-iraq-128x3.pg2</grid>
      <grid name="lnd">ne0np4-2024-nimbus-iraq-128x3.pg2</grid>
      <grid name="ocnice">ICOS10</grid>
      <grid name="rof">r0125</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>ICOS10</mask>
    </model_grid>
```

```xml
    <domain name="ne0np4-2024-nimbus-iraq-32x3.pg2">
      <nx>74112</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.lnd.2024-nimbus-iraq-32x3-pg2_ICOS10.20240618.nc</file>
      <file grid="ice|ocn" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.ocn.2024-nimbus-iraq-32x3-pg2_ICOS10.20240618.nc</file>
      <desc>RRM w/ pg2:</desc>
    </domain>

    <domain name="ne0np4-2024-nimbus-iraq-64x3.pg2">
      <nx>261024</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.lnd.2024-nimbus-iraq-64x3-pg2_ICOS10.20240618.nc</file>
      <file grid="ice|ocn" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.ocn.2024-nimbus-iraq-64x3-pg2_ICOS10.20240618.nc</file>
      <desc>RRM w/ pg2:</desc>
    </domain>

    <domain name="ne0np4-2024-nimbus-iraq-128x3.pg2">
      <nx>993744</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.lnd.2024-nimbus-iraq-128x3-pg2_ICOS10.20240618.nc</file>
      <file grid="ice|ocn" mask="ICOS10">/p/lustre1/hannah6/2024-nimbus-iraq-data/files_domain/domain.ocn.2024-nimbus-iraq-128x3-pg2_ICOS10.20240618.nc</file>
      <desc>RRM w/ pg2:</desc>
    </domain>
```

## components/eam/bld/config_files/horiz_grid.xml

```xml
<horiz_grid dyn="se" hgrid="ne0np4-2024-nimbus-iraq-32x3-pg2"   ncol="74112"  csne="0" csnp="4" npg="2" />
<horiz_grid dyn="se" hgrid="ne0np4-2024-nimbus-iraq-64x3-pg2"   ncol="261024" csne="0" csnp="4" npg="2" />
<horiz_grid dyn="se" hgrid="ne0np4-2024-nimbus-iraq-128x3-pg2"  ncol="993744" csne="0" csnp="4" npg="2" />
```

## components/eam/cime_config/namelist_defaults_eam.xml
<!-- ## components/eamxx/cime_config/namelist_defaults_scream.xml -->

```xml
<bnd_topo hgrid="ne0np4-2024-nimbus-iraq-32x3"  npg="2">atm/cam/topo/USGS-topo_2024-nimbus-iraq-32x3-np4_smoothedx6t_20240618.nc</bnd_topo>
<bnd_topo hgrid="ne0np4-2024-nimbus-iraq-64x3"  npg="2">atm/cam/topo/USGS-topo_2024-nimbus-iraq-64x3-np4_smoothedx6t_20240618.nc</bnd_topo>
<bnd_topo hgrid="ne0np4-2024-nimbus-iraq-128x3" npg="2">atm/cam/topo/USGS-topo_2024-nimbus-iraq-128x3-np4_smoothedx6t_20240618.nc</bnd_topo>

<se_ne hgrid="ne0np4-2024-nimbus-iraq-32x3" > 0 </se_ne>
<se_ne hgrid="ne0np4-2024-nimbus-iraq-64x3" > 0 </se_ne>
<se_ne hgrid="ne0np4-2024-nimbus-iraq-128x3"> 0 </se_ne>

<se_tstep            dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-32x3" > 10 </se_tstep>
<se_tstep            dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-64x3" > 10 </se_tstep>
<se_tstep            dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-128x3"> 10 </se_tstep>

<dt_remap_factor     dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-32x3" > 1 </dt_remap_factor>
<dt_remap_factor     dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-64x3" > 1 </dt_remap_factor>
<dt_remap_factor     dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-128x3"> 1 </dt_remap_factor>

<dt_tracer_factor    dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-32x3" > 6 </dt_tracer_factor>
<dt_tracer_factor    dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-64x3" > 6 </dt_tracer_factor>
<dt_tracer_factor    dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-128x3"> 6 </dt_tracer_factor>

<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-x3" > 6 </hypervis_subcycle_q>
<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-x3" > 6 </hypervis_subcycle_q>
<hypervis_subcycle_q dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-x3"> 6 </hypervis_subcycle_q>


<mesh_file hgrid="ne0np4-2024-nimbus-iraq-32x3" >atm/cam/inic/homme/2024-nimbus-iraq-32x3.g</mesh_file>
<mesh_file hgrid="ne0np4-2024-nimbus-iraq-64x3" >atm/cam/inic/homme/2024-nimbus-iraq-64x3.g</mesh_file>
<mesh_file hgrid="ne0np4-2024-nimbus-iraq-128x3">atm/cam/inic/homme/2024-nimbus-iraq-128x3.g</mesh_file>

<nu_top dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-32x3" > 1e5 </nu_top>
<nu_top dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-64x3" > 1e5 </nu_top>
<nu_top dyn_target="theta-l" hgrid="ne0np4-2024-nimbus-iraq-128x3"> 1e5 </nu_top>

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



--------------------------------------------------------------------------------

## MPAS graph file

reate a conda environment with mpas_tools and the no-MPI version of ESMF:

```
conda create -y -n mpas_tools python=3.11 "mpas_tools>=0.20.0" "esmf=8.2.0=nompi*"
conda activate mpas_tools
```

Add missing files 

```shell
mkdir -p /p/lustre2/hannah6/mpas_standalonedata/mpas-seaice/partition/

scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/mpas_standalonedata/mpas-seaice/partition/* /p/lustre2/hannah6/mpas_standalonedata/mpas-seaice/partition/

/lcrc/group/e3sm/public_html/inputdata/ice/mpas-seaice/ICOS10/seaice.ICOS10.211015.nc
/p/lustre2/hannah6/mpas_standalonedata/mpas-seaice/partition/

ls /usr/gdata/e3sm/ccsm3data/inputdata/ice/mpas-seaice/ICOS10/
ls /p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/
```

Run the sea ice graph generation tools


```shell
# /p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/mpas-seaice.graph.info.220110.part.896
# DIN_LOC_ROOT=/usr/gdata/e3sm/ccsm3data/inputdata
DIN_LOC_ROOT=/p/lustre2/hannah6/inputdata
# mesh_file=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
# mesh_file=/usr/gdata/e3sm/ccsm3data/inputdata/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
mesh_file=/p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/seaice.ICOS10.211015.nc
# NTASK=896   #  8 nodes on Dane
# NTASK=1792  # 16 nodes on Dane
# NTASK=3584  # 32 nodes on Dane
NTASK=7168  # 64 nodes on Dane
cd ${DIN_LOC_ROOT}/ice/mpas-seaice/ICOS10/
# simple_seaice_partitions -m ${mesh_file} -p mpas-seaice.graph.info.20240710 -n ${NTASK} ${NTASK} ${NTASK}
nohup simple_seaice_partitions -m ${mesh_file} -p mpas-seaice.graph.info.20240710 -n ${NTASK} ${NTASK} ${NTASK} > simple_seaice_partitions.out & 



/p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/mpas-seaice.graph.info.220110.part.3584
/p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/mpas-seaice.graph.info.20240710.part.3584

TIMESTAMP1=20240710
TIMESTAMP2=220110
mv /p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/mpas-seaice.graph.info.${TIMESTAMP1}.part.${NTASK} /p/lustre2/hannah6/inputdata/ice/mpas-seaice/ICOS10/mpas-seaice.graph.info.${TIMESTAMP2}.part.${NTASK}


```

--------------------------------------------------------------------------------

## Missing P# files

```shell
scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/atm/cam/physprops/p3_lookup_table_1.dat-v4.1.2 /p/lustre2/hannah6/inputdata/atm/cam/physprops/
```
--------------------------------------------------------------------------------

## CO2 values

The following file can be used to set the value of `CCSM_CO2_PPMV`

```shell
/p/lustre1/hannah6/CESMLENS_delta/ghg_rcp85_1765-2500_c100203.nc
```

```python 
import xarray as xr, numpy as np
co2_file = '/p/lustre1/hannah6/CESMLENS_delta/ghg_rcp85_1765-2500_c100203.nc'
ds = xr.open_dataset(co2_file)
year = ds['time.year']
co2_arr = ds.CO2
for t in range(len(year)):
  yr = year[t].values
  co2 = co2_arr[t].values
  if yr<=2100 and yr%5==0:
    print(f'{yr}  {co2}')
# print()
exit()
```

--------------------------------------------------------------------------------
## Map files for analysis
```shell
BASE_RES=32
# BASE_RES=64
# BASE_RES=128
DATESTAMP=20240618
atm_grid_name=2024-nimbus-iraq-${BASE_RES}x3

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
