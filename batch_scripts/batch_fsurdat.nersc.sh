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

# NE=16 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh
# NE=24 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh
# NE=30 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh
# NE=60 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh
# NE=70 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh
# NE=72 ; sbatch --job-name=fsurdat_ne$NE --output=${HOME}/E3SM/logs_slurm/%x_slurm-%j.out --export=NE=$NE ~/E3SM/batch_fsurdat.nersc.sh


# ESMF_RegridWeightGen --ignore_unmapped -s /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_AVHRR_c110228.nc   -d /global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid/scrip_ne16pg2.nc -m conserve -w map_0.5x0.5_AVHRR_to_ne16pg2_nomask_aave_da_c240325.nc --src_type SCRIP --dst_type SCRIP --64bit_offset
# ESMF_RegridWeightGen                   -s "/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_MODIS_c110228.nc" -d "/global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid/scrip_ne16pg2.nc" -w "map_0.5x0.5_MODIS_to_ne16pg2_nomask_aave_da_c240322.nc" --method conserve --no_log --ignore_unmapped --ignore_degenerate --netcdf4 --debug

# ncremap --alg_typ=aave -5 --src_grd=/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_MODIS_c110228.nc --dst_grd=/global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid/scrip_ne16pg2.nc --map_file=map_0.5x0.5_MODIS_to_ne16pg2_nomask_aave_da_c240322.nc
#-------------------------------------------------------------------------------
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=m3312
#-------------------------------------------------------------------------------

start=$(date +%s)

source activate ncl_env
# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh # need serial ESMF

# NE=24
e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC4
INPUTDATA_ROOT=/global/cfs/cdirs/e3sm/inputdata
HICCUP_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP
DATA_FILE_ROOT=${HICCUP_ROOT}/files_fsurdat/ne${NE}_data
GRID_FILE_ROOT=${HICCUP_ROOT}/files_grid
MAP_FILE_ROOT=${DATA_FILE_ROOT}
DST_GRID=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc

#-------------------------------------------------------------------------------
# # PM command that is failing (segfault):
# cd ${MAP_FILE_ROOT}
# /global/homes/w/whannah/.conda/envs/ncl_env/bin/ESMF_RegridWeightGen --ignore_unmapped -s /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc -d /global/cfs/projectdirs/m3312/whannah/HICCUP/files_grid/scrip_ne16pg2.nc -m conserve -w map_1km-merge-10min_HYDRO1K-merge-nomask_to_ne16pg2_nomask_aave_da_c240328.nc --src_type SCRIP --dst_type SCRIP --64bit_offset
#-------------------------------------------------------------------------------
# # macos commands
# e3sm_root=~/E3SM_SRC1
# INPUTDATA_ROOT=/global/cfs/cdirs/e3sm/inputdata
# INPUTDATA_ROOT=~/inputdata
# HICCUP_ROOT=~/HICCUP/data_scratch
# DATA_FILE_ROOT=${HICCUP_ROOT}/files_fsurdat/ne${NE}_data
# GRID_FILE_ROOT=${HICCUP_ROOT}/files_grid
# MAP_FILE_ROOT=${DATA_FILE_ROOT}
# DST_GRID=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc
# mkdir -p ${DATA_FILE_ROOT}
# GRID1=${INPUTDATA_ROOT}/lnd/clm2/mappingdata/grids/SCRIPgrid_1km-merge-10min_HYDRO1K-merge-nomask_c20200415.nc
# GRID2=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc
# MAP_FILE=${DATA_FILE_ROOT}/map_1km-merge-10min_HYDRO1K-merge-nomask_to_ne${NE}pg2_nomask_aave_da_c240328.nc
# ESMF_RegridWeightGen --ignore_unmapped -s ${GRID1} -d ${GRID2} -m conserve -w ${MAP_FILE} --src_type SCRIP --dst_type SCRIP --64bit_offset
#-------------------------------------------------------------------------------
# # Build mksurfdata
# # might need to manually add mkFertMod.F90 to src/Srcfiles
# cd ${e3sm_root}/components/elm/tools/mksurfdata_map/src/
# ${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
# make clean
# INC_NETCDF="`nf-config --includedir`"  \
# LIB_NETCDF="`nc-config --libdir`"  \
# USER_FC="`nc-config --fc`"  \
# USER_LDFLAGS="-L`nc-config --libdir` -lnetcdf -lnetcdff" \
# make
#-------------------------------------------------------------------------------
set -v
#-------------------------------------------------------------------------------
# Create map files

mkdir -p ${DATA_FILE_ROOT}
cd ${MAP_FILE_ROOT}

# ${e3sm_root}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${DST_GRID} --inputdata-path ${INPUTDATA_ROOT} --res ne${NE}pg2 --gridtype global --output-filetype 64bit_offset -v --debug --list
${e3sm_root}/components/elm/tools/mkmapdata/mkmapdata.sh --gridfile ${DST_GRID} --inputdata-path ${INPUTDATA_ROOT} --res ne${NE}pg2 --gridtype global --output-filetype 64bit_offset -v

#-------------------------------------------------------------------------------
# use maps to create new fsurdat

CDATE=240401
# CDATE=`date +%y%m%d` # creation date

# ./mksurfdata.pl -res ne${NE}pg2 -y 2010 -d -dinlc ${INPUTDATA_ROOT} -usr_mapdir ${MAP_FILE_ROOT}
# ./mksurfdata.pl -res usrspec -usr_gname ne${NE}pg2 -usr_gdate ${CDATE} -y 2010 -d -dinlc ${INPUTDATA_ROOT} -usr_mapdir ${MAP_FILE_ROOT} -usrname=${MAP_FILE_ROOT}/clm.input_data_list

cd ${MAP_FILE_ROOT}

${e3sm_root}/components/elm/tools/mksurfdata_map/mksurfdata.pl \
-res usrspec \
-usr_gname ne${NE}pg2 \
-usr_gdate ${CDATE} \
-y 2010 -d \
-dinlc ${INPUTDATA_ROOT} \
-usr_mapdir ${MAP_FILE_ROOT} \
-usrname=${MAP_FILE_ROOT}/clm.input_data_list

# Create the new fsurdat file
${e3sm_root}/components/elm/tools/mksurfdata_map/mksurfdata_map < namelist

#-------------------------------------------------------------------------------
set +v
#-------------------------------------------------------------------------------
# /global/homes/w/whannah/E3SM/E3SM_SRC4/components/elm/tools/mksurfdata_map/surfdata_ne16pg2.nc /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne16pg2_simyr2010_c240322.nc
# /global/homes/w/whannah/E3SM/E3SM_SRC4/components/elm/tools/mksurfdata_map/surfdata_ne24pg2.nc /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne16pg2_simyr2010_c240322.nc
# /global/homes/w/whannah/E3SM/E3SM_SRC4/components/elm/tools/mksurfdata_map/surfdata_ne60pg2.nc /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne16pg2_simyr2010_c240322.nc
# /global/homes/w/whannah/E3SM/E3SM_SRC4/components/elm/tools/mksurfdata_map/surfdata_ne70pg2.nc /global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne16pg2_simyr2010_c240322.nc
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
echo
echo NE             : $NE
echo DST_GRID       : $DST_GRID
echo DATA_FILE_ROOT : $DATA_FILE_ROOT
echo
#-------------------------------------------------------------------------------
end=$(date +%s)
duration_sec=$(($end - $start))
duration_min=$((($end - $start)/60))
echo; echo total duration: ${duration_sec} sec   \(${duration_min} min\)
#-------------------------------------------------------------------------------