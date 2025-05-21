#!/bin/bash

## Setup environment
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

eval $(/global/homes/w/whannah/E3SM/E3SM_SRC4/cime/CIME/Tools/get_case_env)

e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC4

## Build gen_domain tool
```shell
gen_domain=${e3sm_root}/cime/tools/mapping/gen_domain_files/gen_domain
cd `dirname ${gen_domain}`/src
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
${e3sm_root}/cime/CIME/scripts/configure --macros-format Makefile --mpilib mpi-serial
# ${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
gmake
```

<<<<<<<< HEAD:notes_gen_domain.md
```shell
========
gmake clean; gmake

>>>>>>>> d0f5fab6ccf6c975f4dacf2aee74bf69482df2f1:old_notes/notes_gen_domain.txt
# NOTE - Mar 13 2024 
# edit the Makefile to set USE_MACROS=FALSE
# and add the following lines
# SFC := gfortran
# OS=LINUX
# USER_FFLAGS :=  -g -ffree-line-length-none -I`nc-config --includedir`
# USER_LDFLAGS := -L`nc-config --libdir` -lnetcdf -lnetcdff
```

#-------------------------------------------------------------------------------
## Ben's example commands

```shell
# Set paths to mapping files
mapping_root="/global/homes/b/bhillma/cscratch/e3sm/grids/ne4"
ocn_grid_name=oQU240
atm_grid_name=ne4np4
lnd_grid_name=${atm_grid_name}
```

```shell
# run domain generation tool (from output directory)
domain_root=${mapping_root} 
mkdir -p ${domain_root} && cd ${domain_root}
for target_grid_name in ${lnd_grid_name} ${atm_grid_name}; do
    
    # Find conservative mapping files, use the latest file generated    
    map_ocn_to_target=`ls ${mapping_root}/map_${ocn_grid_name}_to_${target_grid_name}_monotr.*.nc | tail -n1`

    # Run domain tool code
    ${gen_domain} -m ${map_ocn_to_target} -o ${ocn_grid_name} -l ${target_grid_name}

done
```

#-------------------------------------------------------------------------------

<<<<<<<< HEAD:notes_gen_domain.md
```shell
NE=16
========
# NE=16
>>>>>>>> d0f5fab6ccf6c975f4dacf2aee74bf69482df2f1:old_notes/notes_gen_domain.txt
# NE=24
NE=30
# NE=60
# NE=70

e3sm_root=/global/homes/w/whannah/E3SM/E3SM_SRC0
gen_domain=${e3sm_root}/cime/tools/mapping/gen_domain_files/gen_domain
# HICCUP_ROOT=/pscratch/sd/w/whannah/HICCUP/data_scratch
HICCUP_ROOT=/global/cfs/projectdirs/m3312/whannah/HICCUP
MAPS_FILE_ROOT=${HICCUP_ROOT}/files_map
GRID_FILE_ROOT=${HICCUP_ROOT}/files_grid
OCN_GRID=/global/cfs/cdirs/e3sm/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc
ATM_GRID=${GRID_FILE_ROOT}/scrip_ne${NE}pg2.nc
MAP_FILE=${MAPS_FILE_ROOT}/map_oEC60to30v3_to_ne${NE}pg2_traave.20240313.nc



ncremap -5 -a traave --src_grd=${OCN_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}

${gen_domain} -m ${MAP_FILE} -o oEC60to30v3 -l ne${NE}pg2


cp  *230203* /global/cfs/cdirs/m3312/whannah/init_files/domain_files/

/global/cfs/cdirs/e3sm/inputdata
```

python generate_domain_files_E3SM.py -m $MAP_FILE -o oEC60to30v3 -l ne${NE}pg2

# local mac mini tests:

python generate_domain_files_E3SM.py -m /Users/hannah6/HICCUP/files_map/map_oEC60to30v3_to_ne16pg2_traave.20240313.nc -o oEC60to30v3 -l ne16pg2

#-------------------------------------------------------------------------------
```shell
mv domain.lnd.ne16pg2_oEC60to30v3.240318.nc domain.lnd.ne16pg2_oEC60to30v3.20240313.nc
mv domain.ocn.ne16pg2_oEC60to30v3.240318.nc domain.ocn.ne16pg2_oEC60to30v3.20240313.nc
mv domain.ocn.ne24pg2_oEC60to30v3.240318.nc domain.ocn.ne24pg2_oEC60to30v3.20240313.nc
mv domain.lnd.ne24pg2_oEC60to30v3.240318.nc domain.lnd.ne24pg2_oEC60to30v3.20240313.nc
mv domain.ocn.ne60pg2_oEC60to30v3.240318.nc domain.ocn.ne60pg2_oEC60to30v3.20240313.nc
mv domain.lnd.ne60pg2_oEC60to30v3.240318.nc domain.lnd.ne60pg2_oEC60to30v3.20240313.nc
mv domain.ocn.ne70pg2_oEC60to30v3.240318.nc domain.ocn.ne70pg2_oEC60to30v3.20240313.nc
mv domain.lnd.ne70pg2_oEC60to30v3.240318.nc domain.lnd.ne70pg2_oEC60to30v3.20240313.nc
```
#-------------------------------------------------------------------------------



