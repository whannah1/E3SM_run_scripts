
# Summary

One first needs the new user-defined grid in SCRIP format.
Then, the process of creating ELM surface dataset involves the
following steps:

1. Creating 17 mapping files to remap ELM's raw datasets onto the new user-defined.
2. Creating surface dataset using `mksurfdata_map`
  2.1 Creating a namelist file that uses the 17 maps created in step-1.
  2.2 Compile `mksurfdata_map`
  2.3 Run `mksurfdata_map`

# Step-1: Creating maps

I have created a script that generates 17 batch scripts
to generate the maps. The script only works on NERSC

```shell
# Creating an ELM surface dataset for a new user-defined grid
git clone git@github.com:bishtgautam/elm-surface-dataset
cd elm-surface-dataset

HGRID_NAME=<name-for-your-new-hgrid>
SCRIP_FNAME=<new-grid.nc>
SCRIP_FPATH=<path-to-new-grid.nc>

./create_mapping_scripts.sh      \
-hgrid_name $HGRID_NAME           \
-scrip_filename $SCRIP_FNAME \
-scrip_filepath $SCRIP_FPATH

cd $HGRID_NAME
```

Then, submit the 17 run files via `sbatch *01.run`. 
Out of 17 batch scripts, 16 are using debug queue on Perlmutter.
So, you will be able to submit 5 of them at a time. The 15th file
uses regular queue and uses 40 nodes because it is creating the map
for a 1K dataset. After the jobs finished, you would have 17 maps
with names like the following:

```shell
map_360x720_cruncep_to_<HGRID_NAME>_nomask_aave_da_c<YYMMDD>.nc

USR_MAPDIR=$PWD
```

# Step-2.1: Creating the namelist file

```shell
cd <your-e3sm>
cd components/elm/tools/mksurfdata_map/
```

Copy the placeholder namelist file from https://gist.github.com/bishtgautam/3b220bce9de550d8e2c49377243feb61
and do a find/replace for following
- USR_MAPDIR
- HGRID_NAME
- YYMMDD

# Step-2.2: Compile the code

```shell
cd src

# Compile the code using instructions lines 1 -40 on
# https://gist.github.com/bishtgautam/712261d33d650dac70c9a8dbfa094899.
# Don't do the srun command.
```

# Step-2.3 Run the code

```shell
# Get on an interactive queue
salloc --nodes 1 --qos interactive --time 00:15:00 --constraint cpu --account e3sm

# Load modules and export environmental variables mentioned in lines 1-37 of
https://gist.github.com/bishtgautam/712261d33d650dac70c9a8dbfa094899.

cd ..
# (i.e. cd components/elm/tools/mksurfdata_map/)

# Now run the mksurfdata_map
srun -n 1 ./mksurfdata_map < namelist
```




# create_mapping_scripts.sh

```shell
#!/bin/sh

YYMMDD=`date +"%y%m%d"`
#scrip_file_name=northamericax4v1pg2_scrip.nc
#hgrid_name=northamericax4v1pg2

scrip_filename=
scrip_filepath=
hgrid_name=
verbose=0

##################################################
# The command line help
##################################################
display_help() {
    echo "Usage: $0 " >&2
    echo
    echo "   -hgrid_name     <name>             The hgrid name (e.g. northamericax4v1pg2)"
    echo "   -scrip_filename <netcdf_filename>  The SCRIP filename (e.g. northamericax4v1pg2_scrip.nc)"
    echo "   -scrip_filepath <path>             The path to SCRIP file (e.g. /global/cfs/cdirs/e3sm/inputdata on NERSC"
    echo "   -v, --verbose                      Set verbosity option true"
    echo
    echo "Example: "
    echo "   ./create_mapping_scripts.sh                  \\"
    echo "   -hgrid_name northamericax4v1pg2              \\"
    echo "   -scrip_filename northamericax4v1pg2_scrip.nc \\"
    echo "   -scrip_filepath ~/data"
    echo
    exit 1
}


##################################################
# Get command line arguments
##################################################
while [ $# -gt 0 ]
do
  case "$1" in
    -hgrid_name )    hgrid_name="$2"; shift ;;
    -scrip_filename) scrip_filename="$2"; shift ;;
    -scrip_filepath)   scrip_filepath="$2"; shift ;;
    -v | --verbose)  verbose=1;;
    -*)
      echo "Unknown option: $1"
      display_help
      exit 0
      ;;
    -h | --help)
      display_help
      exit 0
      ;;
    *)  break;; # terminate while loop
  esac
  shift
done

if [ $verbose -eq 1 ]
then
  echo "Verbosity: On"
  echo " "
fi

if [ -z $hgrid_name ]
then
  echo "hgrid_name is not specified"
  display_help
  exit 0
fi

if [ -z $scrip_filename ]
then
  echo "scrip_filename is not specified"
  display_help
  exit 0
else
  if [ ! -f "$scrip_filepath/$scrip_filename" ]
  then
    echo "$scrip_filepath/$scrip_filename does not exist"
    exit 0
  fi
fi

rm -rf $hgrid_name
mkdir -p $hgrid_name
echo "Creating batch scripts:"
for filename in map_*run; do
  echo "  $hgrid_name/$hgrid_name.$filename"
  cp $filename $hgrid_name/$hgrid_name.$filename
  sed -i "s/YYMMDD/${YYMMDD}/g"                  ${hgrid_name}/${hgrid_name}.$filename
  sed -i "s/SCRIP_FILE_NAME/${scrip_filename}/g" ${hgrid_name}/${hgrid_name}.$filename
  sed -i "s#SCRIP_FILE_PATH#${scrip_filepath}#g" ${hgrid_name}/${hgrid_name}.$filename
  sed -i "s/HGRID_NAME/${hgrid_name}/g"          ${hgrid_name}/${hgrid_name}.$filename
done

```





```shell
GRID_ROOT=/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids

==> map_01.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_AVHRR_c110228.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_AVHRR_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_02.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_MODIS_c110228.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_MODIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_03.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_LandScan2004_c120517.nc           -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_LandScan2004_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                  --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_04.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_MODIS_c110915.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_MODIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                         --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_05.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3x3_USGS_c120912.nc                         -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_USGS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                          --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_06.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_nomask_c110530.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_07.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_IGBP-GSDP_c110228.nc                 -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_IGBP-GSDP_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                     --src_type SCRIP --dst_type SCRIP
==> map_08.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_5x5min_ISRIC-WISE_c111114.nc                -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_5x5min_ISRIC-WISE_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                    --src_type SCRIP --dst_type SCRIP
==> map_09.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_10x10min_nomask_c110228.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_10x10min_nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                      --src_type SCRIP --dst_type SCRIP
==> map_10.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_10x10min_IGBPmergeICESatGIS_c110818.nc      -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_10x10min_IGBPmergeICESatGIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc          --src_type SCRIP --dst_type SCRIP
==> map_11.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_GLOBE-Gardner_c120922.nc          -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_GLOBE-Gardner_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                 --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_12.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_3minx3min_GLOBE-Gardner-mergeGIS_c120922.nc -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_3x3min_GLOBE-Gardner-mergeGIS_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc        --src_type SCRIP --dst_type SCRIP --64bit_offset
==> map_13.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.9x1.25_GRDC_c130307.nc                    -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.9x1.25_GRDC_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                        --src_type SCRIP --dst_type SCRIP
==> map_14.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_360x720_cruncep_c120830.nc                  -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_360x720_cruncep_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                      --src_type SCRIP --dst_type SCRIP
==> map_15.run <== srun -n 40 -c 256 ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/UGRID_1km-merge-10min_HYDRO1K-merge-nomask_c130402.nc -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_1km-merge-10min_HYDRO1K-merge-nomask_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc --src_type UGRID --dst_type SCRIP --src_meshname landmesh --64bit_offset
==> map_16.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.5x0.5_GSDTG2000_c240125.nc                -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.5x0.5_GSDTG2000_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                    --src_type SCRIP --dst_type SCRIP
==> map_17.run <== srun -n 8         ESMF_RegridWeightGen --ignore_unmapped -s ${GRID_ROOT}/SCRIPgrid_0.1x0.1_nomask_c110712.nc                   -d SCRIP_FILE_PATH/SCRIP_FILE_NAME -m conserve -w map_0.1x0.1_to_HGRID_NAME_nomask_aave_da_${CDATE}.nc                              --src_type SCRIP --dst_type SCRIP

```