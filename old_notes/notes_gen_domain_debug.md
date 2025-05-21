
--------------------------------------------------------------------------------
# Important paths 

## LLNL

```shell
conda activate e3sm-unified
DIN_LOC_ROOT=/usr/workspace/e3sm/ccsm3data/inputdata
# DIN_LOC_ROOT=/p/lustre1/hannah6/inputdata
E3SM_ROOT=${HOME}/E3SM/E3SM_SRC0
GRID_ROOT=/p/lustre1/hannah6/hiccup_scratch/files_grid
MAPS_ROOT=/p/lustre1/hannah6/hiccup_scratch/files_map
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

## LCRC

```shell
source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
E3SM_ROOT=
DATA_ROOT=/global/cfs/cdirs/m3312/whannah
GRID_ROOT=/lcrc/group/e3sm/ac.whannah/HICCUP/files_grid
MAPS_ROOT=/lcrc/group/e3sm/ac.whannah/HICCUP/files_map

/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_1.9x2.5_aave_esmf.241210.nc
/lcrc/group/e3sm/data/inputdata/lnd/clm2/mappingdata/grids/1.9x2.5_c110308.nc
/compyfs/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc
```
--------------------------------------------------------------------------------
## Adding support for 2D grids

```shell
# LCRC test case
python ${HOME}/E3SM/E3SM_SRC3/tools/generate_domain_files/generate_domain_files_E3SM.py -m /lcrc/group/e3sm/data/inputdata/cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_1.9x2.5_aave_esmf.241210.nc -o oEC60to30v3 -l f19 --date-stamp=20250204 --output-root=/lcrc/group/e3sm/ac.whannah/scratch/chrys/files_domain --fix-pole
```

```shell
> ncdump -h /lcrc/group/e3sm/data/inputdata/share/domains/domain.lnd.0.9x1.25_oEC60to30v3.231108.nc
netcdf domain.lnd.0.9x1.25_oEC60to30v3.231108 {
dimensions:
  n = 55296 ;
  ni = 288 ;
  nj = 192 ;
  nv = 4 ;
variables:
  double xc(nj, ni) ;
    xc:long_name = "longitude of grid cell center" ;
    xc:units = "degrees_east" ;
    xc:bounds = "xv" ;
  double yc(nj, ni) ;
    yc:long_name = "latitude of grid cell center" ;
    yc:units = "degrees_north" ;
    yc:bounds = "yv" ;
  double xv(nj, ni, nv) ;
    xv:long_name = "longitude of grid cell verticies" ;
    xv:units = "degrees_east" ;
  double yv(nj, ni, nv) ;
    yv:long_name = "latitude of grid cell verticies" ;
    yv:units = "degrees_north" ;
  int mask(nj, ni) ;
    mask:long_name = "domain mask" ;
    mask:note = "unitless" ;
    mask:coordinates = "xc yc" ;
    mask:comment = "0 value indicates cell is not active" ;
  double area(nj, ni) ;
    area:long_name = "area of grid cell in radians squared" ;
    area:coordinates = "xc yc" ;
    area:units = "radian2" ;
  double frac(nj, ni) ;
    frac:long_name = "fraction of grid cell that is active" ;
    frac:coordinates = "xc yc" ;
    frac:note = "unitless" ;
    frac:filter1 = "error if frac> 1.0+eps or frac < 0.0-eps; eps = 0.1000000E-11" ;
    frac:filter2 = "limit frac to [fminval,fmaxval]; fminval= 0.1000000E-02 fmaxval=  1.000000" ;

// global attributes:
    :title = "CESM domain data:" ;
    :Conventions = "CF-1.0" ;
    :source_code = "SVN $Id: gen_domain.F90 65202 2014-11-06 21:07:45Z mlevy@ucar.edu $" ;
    :SVN_url = " $URL: https://svn-ccsm-models.cgd.ucar.edu/tools/mapping/gen_domain/trunk/src/gen_domain.F90 $" ;
    :Compiler_Optimized = "TRUE" ;
    :hostname = "chrlogin2.lcrc.anl.gov" ;
    :history = "created by ac.jwolfe, 2023-11-08 11:17:45" ;
    :source = "map_oEC60to30v3_to_0.9x1.25_aave.20231107_esmf.nc" ;
    :map_domain_a = "/compyfs/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc" ;
    :map_domain_b = "/compyfs/inputdata/lnd/clm2/mappingdata/grids/0.9x1.25_c110307.nc" ;
    :map_grid_file_ocn = "/compyfs/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc" ;
    :map_grid_file_atm = "/compyfs/inputdata/lnd/clm2/mappingdata/grids/0.9x1.25_c110307.nc" ;
}
```

--------------------------------------------------------------------------------
## Misc Commands

```shell

DATESTAMP=20250129

ATM_GRID=${GRID_ROOT}/ne${NE}pg2_scrip.nc
OCN_GRID=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
MAP_FILE=${MAPS_ROOT}/map_ICOS10_to_${atm_grid_name}_traave.${DATESTAMP}.nc
ncremap -a traave --src_grd=${OCN_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE}

OUTPUT_ROOT=${DATA_ROOT}/files_domain
python ${E3SM_ROOT}/tools/generate_domain_files/generate_domain_files_E3SM.py -m ${MAP_FILE} -o ICOS10 -l ${atm_grid_name}-pg2 --date-stamp=${DATESTAMP} --output-root=${OUTPUT_ROOT}
```
--------------------------------------------------------------------------------
## Building the old tool

```shell
e3sm_root=${HOME}/E3SM/E3SM_SRC0
gen_domain=${HOME}/E3SM/E3SM_SRC0/cime/tools/mapping/gen_domain_files/gen_domain
cd `dirname ${gen_domain}`/src
eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
${e3sm_root}/cime/CIME/scripts/configure --macros-format Makefile --mpilib mpi-serial
# ${e3sm_root}/cime/CIME/scripts/configure && source .env_mach_specific.sh
gmake
```
--------------------------------------------------------------------------------

