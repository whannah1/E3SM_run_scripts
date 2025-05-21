#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
Below are commands to create grid and map files. 
copying and pasting all this into the terminal should work if
 - the directories ~/grids and ~/maps exist
 - NCO is installed in your path or conda environment

NE=30
SRC_GRID=ne${NE}pg2
DST_NY=180
DST_NX=360
DST_GRID=${DST_NY}x${DST_NX}

GRID_FILE_PATH=~/grids
SRC_GRID_FILE=${GRID_FILE_PATH}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_FILE_PATH}/${DST_GRID}_scrip.nc
MAP_FILE=~/maps/map_${SRC_GRID}_to_${DST_GRID}_aave.nc

# generate model grid file
GenerateCSMesh --alt --res ${NE} --file ${GRID_FILE_PATH}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_FILE_PATH}/ne${NE}.g --out ${GRID_FILE_PATH}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_FILE_PATH}/ne${NE}pg2.g --out ${GRID_FILE_PATH}/ne${NE}pg2_scrip.nc

# generate lat/lon grid file
ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst

# generate map file
ncremap -6 --alg_typ=aave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

'''
#---------------------------------------------------------------------------------------------------
'''
nohup python -u run_post.2024.scidac.L80-ensemble.py > run_post.2024.scidac.L80-ensemble.py.out &
nohup python -u run_post.2024.scidac.L80-ensemble.py > run_post.2024.scidac.L80-ensemble.py.lt_archive_check.out &
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime, sys
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n  '+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
st_archive,calc_hovmoller = False,False
run_zppy,clear_zppy_status,check_zppy_status= False,False,False
lt_archive_create,lt_archive_check,lt_archive_update,cp_post_to_cfs = False,False,False,False

acct = 'm4310'

# st_archive        = True
# clear_zppy_status = True
# check_zppy_status = True
# run_zppy          = True
# calc_hovmoller    = True
# cp_post_to_cfs    = True
# lt_archive_create = True
lt_archive_check  = True
# lt_archive_update = True
# delete_data       = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'

#-------------------------------------------------------------------------------
if calc_hovmoller:
   import xarray as xr, numpy as np
   sys.path.append('/global/homes/w/whannah/Research/E3SM/code_QBO')
   import QBO_diagnostic_methods as QBO_methods
#-------------------------------------------------------------------------------
nlev_list      = []
gweff_list     = []
cfrac_list     = []
hdpth_list     = []
hdpth_min_list = []
stspd_min_list = []
plev_srcw_list = []
case_list      = []
nyr_list       = []
def add_case( nlev=80, gweff=0.35, cfrac=10, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700,nyr=5, old_fmt=False ):
   #-----------------------------------------------------------
   compset,grid_short = 'F20TR','ne30pg2'
   ens_id = '2024-SCIDAC-00'
   if nlev==72: ens_id = ens_id+'-L72'
   case_tmp_list = ['E3SM',ens_id,compset,grid_short]
   case_tmp_list.append(f'EF_{gweff:0.2f}')
   if     old_fmt: case_tmp_list.append(f'CF_{cfrac:02.0f}')
   if not old_fmt: case_tmp_list.append(f'CF_{cfrac:05.2f}')
   case_tmp_list.append(f'HD_{hdpth:0.2f}')
   case_tmp_list.append(f'HM_{hdpth_min:04.1f}')
   case_tmp_list.append(f'SS_{stspd_min:04.1f}')
   case_tmp_list.append(f'PS_{plev_srcw:3.0f}')
   case_list.append( '_'.join(case_tmp_list) )
   #-----------------------------------------------------------
   nlev_list.append(nlev)
   nyr_list.append(nyr)
   gweff_list.append(gweff)
   cfrac_list.append(cfrac)
   hdpth_list.append(hdpth)
   hdpth_min_list.append(hdpth_min)
   stspd_min_list.append(stspd_min)
   plev_srcw_list.append(plev_srcw)
#-------------------------------------------------------------------------------

nyr_tmp = 5

### Ensemble values from => https://acme-climate.atlassian.net/wiki/spaces/QIE/pages/4791500859/2024-11-21+Initial+sample
# L80_iter0
# add_case( gweff=0.35, cfrac=10,    hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # v3 defaults
# add_case( gweff=0.18, cfrac=10.95, hdpth=0.48, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.13, cfrac=18.87, hdpth=0.55, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.09, cfrac=20.33, hdpth=0.99, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.28, cfrac= 5.86, hdpth=0.71, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.32, cfrac=15.00, hdpth=0.83, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.34, cfrac=25.64, hdpth=1.04, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.25, cfrac=33.11, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.50, cfrac= 8.76, hdpth=0.92, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.36, cfrac=14.13, hdpth=1.13, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.44, cfrac=21.60, hdpth=1.26, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.44, cfrac=32.59, hdpth=0.31, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.57, cfrac= 7.70, hdpth=1.24, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.62, cfrac=16.32, hdpth=1.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.55, cfrac=22.14, hdpth=0.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.52, cfrac=26.04, hdpth=0.57, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.69, cfrac=10.53, hdpth=1.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.71, cfrac=12.36, hdpth=0.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.78, cfrac=24.44, hdpth=0.62, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.68, cfrac=31.00, hdpth=0.85, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )
# add_case( gweff=0.76, cfrac=35.69, hdpth=1.08, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True )

### add_case( gweff=0.07, cfrac=28.99, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # BAD
### add_case( gweff=0.14, cfrac=36.95, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # BAD
### add_case( gweff=0.21, cfrac=28.28, hdpth=1.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # BAD
### add_case( gweff=0.40, cfrac=37.86, hdpth=0.66, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # BAD
### add_case( gweff=0.60, cfrac=39.84, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700, nyr=nyr_tmp, old_fmt=True ) # BAD

# L80_iter1
# add_case( gweff=0.21, cfrac=19.51, hdpth=0.36, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.10, cfrac=18.23, hdpth=1.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac= 9.11, hdpth=0.60, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.59, cfrac=15.62, hdpth=0.67, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.66, cfrac=13.34, hdpth=1.10, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.26, cfrac= 7.22, hdpth=1.06, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac=17.73, hdpth=1.32, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.44, cfrac=11.74, hdpth=0.42, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.52, cfrac= 5.58, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# add_case( gweff=0.14, cfrac= 9.89, hdpth=0.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.65, cfrac=16.85, hdpth=0.90, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.59, cfrac=11.58, hdpth=1.33, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.39, cfrac= 7.47, hdpth=0.64, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.72, cfrac=13.47, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.17, cfrac= 8.48, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.46, cfrac=14.65, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac=20.10, hdpth=1.41, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.34, cfrac=18.69, hdpth=1.01, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.26, cfrac=15.72, hdpth=0.61, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.42, cfrac= 9.54, hdpth=0.86, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=12.81, hdpth=1.22, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.55, cfrac=17.13, hdpth=0.33, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.37, cfrac= 5.96, hdpth=0.96, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.79, cfrac= 6.51, hdpth=0.77, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.22, cfrac=20.76, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# L80_iter2
# add_case( gweff=0.50, cfrac=7.00 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.49, cfrac=7.50 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=8.00 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.47, cfrac=8.50 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=7.79 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.21 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.76 , hdpth=0.70, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.32, cfrac=8.82 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.35, cfrac=8.21 , hdpth=0.72, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.58 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )


# 2024-01-10 - first ensemble to perturb new parameters
# L80_iter3
# add_case( gweff=0.40, cfrac=11.56, hdpth=0.76, hdpth_min=1.23, stspd_min=44.05, plev_srcw=779.94 )
# add_case( gweff=0.28, cfrac= 9.32, hdpth=0.59, hdpth_min=2.29, stspd_min= 6.86, plev_srcw=830.73 )
# add_case( gweff=0.15, cfrac= 6.97, hdpth=0.40, hdpth_min=1.04, stspd_min=36.36, plev_srcw=617.36 )
# add_case( gweff=0.74, cfrac=18.00, hdpth=1.27, hdpth_min=3.34, stspd_min=25.07, plev_srcw=558.72 )
# add_case( gweff=0.86, cfrac=20.28, hdpth=1.44, hdpth_min=4.20, stspd_min=13.74, plev_srcw=747.48 )
# add_case( gweff=0.43, cfrac=12.17, hdpth=0.81, hdpth_min=3.49, stspd_min=49.69, plev_srcw=936.26 )
# add_case( gweff=0.57, cfrac=14.72, hdpth=1.01, hdpth_min=4.00, stspd_min=10.90, plev_srcw=640.98 )
# add_case( gweff=0.12, cfrac= 6.22, hdpth=0.35, hdpth_min=4.49, stspd_min= 0.35, plev_srcw=821.24 )
# add_case( gweff=0.07, cfrac= 5.36, hdpth=0.28, hdpth_min=4.92, stspd_min=14.45, plev_srcw=670.28 )
# add_case( gweff=0.51, cfrac=13.69, hdpth=0.93, hdpth_min=4.56, stspd_min=16.67, plev_srcw=529.54 )
# add_case( gweff=0.85, cfrac=20.02, hdpth=1.42, hdpth_min=2.03, stspd_min=39.50, plev_srcw=760.21 )
# add_case( gweff=0.71, cfrac=17.39, hdpth=1.22, hdpth_min=3.77, stspd_min=32.90, plev_srcw=524.59 )
# add_case( gweff=0.77, cfrac=18.50, hdpth=1.30, hdpth_min=1.47, stspd_min=34.69, plev_srcw=915.59 )
# add_case( gweff=0.31, cfrac= 9.96, hdpth=0.64, hdpth_min=2.57, stspd_min= 5.24, plev_srcw=865.17 )
# add_case( gweff=0.37, cfrac=11.10, hdpth=0.73, hdpth_min=3.06, stspd_min=45.74, plev_srcw=699.25 )
# add_case( gweff=0.62, cfrac=15.75, hdpth=1.09, hdpth_min=1.70, stspd_min=20.60, plev_srcw=700.09 )
# add_case( gweff=0.61, cfrac=15.49, hdpth=1.07, hdpth_min=2.37, stspd_min=23.39, plev_srcw=599.29 )
# add_case( gweff=0.22, cfrac= 8.22, hdpth=0.50, hdpth_min=2.94, stspd_min=29.75, plev_srcw=880.35 )

# 2025-04-03 - 2nd 6 parameter ensemble - after QBOi meeting
# L80_iter3
add_case( gweff=0.02, cfrac=17.80, hdpth=1.30, hdpth_min=4.88, stspd_min=4.52, plev_srcw=851.56 )
add_case( gweff=0.05, cfrac=18.79, hdpth=0.90, hdpth_min=1.00, stspd_min=0.10, plev_srcw=500.00 )
add_case( gweff=0.06, cfrac=22.32, hdpth=0.61, hdpth_min=2.25, stspd_min=1.83, plev_srcw=584.38 )
add_case( gweff=0.09, cfrac=16.24, hdpth=0.72, hdpth_min=3.62, stspd_min=0.37, plev_srcw=935.94 )
add_case( gweff=0.11, cfrac=17.30, hdpth=0.60, hdpth_min=1.50, stspd_min=0.18, plev_srcw=668.75 )
add_case( gweff=0.13, cfrac=11.95, hdpth=0.99, hdpth_min=4.38, stspd_min=3.02, plev_srcw=795.31 )
add_case( gweff=0.15, cfrac=13.00, hdpth=1.40, hdpth_min=2.75, stspd_min=1.22, plev_srcw=640.62 )
add_case( gweff=0.18, cfrac=18.40, hdpth=0.32, hdpth_min=3.12, stspd_min=0.65, plev_srcw=767.19 )
add_case( gweff=0.20, cfrac=15.70, hdpth=1.05, hdpth_min=4.00, stspd_min=0.32, plev_srcw=612.50 )
add_case( gweff=0.23, cfrac=10.77, hdpth=0.48, hdpth_min=1.88, stspd_min=2.02, plev_srcw=739.06 )
add_case( gweff=0.25, cfrac= 9.69, hdpth=0.75, hdpth_min=3.25, stspd_min=4.09, plev_srcw=696.88 )
add_case( gweff=0.28, cfrac=11.83, hdpth=1.05, hdpth_min=2.62, stspd_min=0.12, plev_srcw=823.44 )
add_case( gweff=0.31, cfrac= 9.76, hdpth=1.03, hdpth_min=4.50, stspd_min=0.56, plev_srcw=556.25 )
add_case( gweff=0.34, cfrac=12.04, hdpth=0.43, hdpth_min=1.38, stspd_min=1.35, plev_srcw=907.81 )
add_case( gweff=0.37, cfrac= 9.84, hdpth=0.51, hdpth_min=3.75, stspd_min=2.73, plev_srcw=528.12 )
add_case( gweff=0.40, cfrac= 7.45, hdpth=1.25, hdpth_min=2.12, stspd_min=0.21, plev_srcw=879.69 )
add_case( gweff=0.43, cfrac= 9.17, hdpth=0.89, hdpth_min=3.00, stspd_min=1.00, plev_srcw=725.00 )
add_case( gweff=0.46, cfrac= 5.95, hdpth=0.47, hdpth_min=2.88, stspd_min=0.87, plev_srcw=626.56 )
add_case( gweff=0.49, cfrac= 8.57, hdpth=0.33, hdpth_min=4.25, stspd_min=0.24, plev_srcw=809.38 )
add_case( gweff=0.52, cfrac=11.62, hdpth=1.44, hdpth_min=1.62, stspd_min=2.47, plev_srcw=710.94 )
add_case( gweff=0.55, cfrac= 6.64, hdpth=1.25, hdpth_min=3.50, stspd_min=1.50, plev_srcw=893.75 )
add_case( gweff=0.58, cfrac= 8.83, hdpth=0.23, hdpth_min=2.38, stspd_min=0.49, plev_srcw=570.31 )
add_case( gweff=0.61, cfrac= 9.44, hdpth=0.57, hdpth_min=4.75, stspd_min=0.13, plev_srcw=865.62 )
add_case( gweff=0.64, cfrac= 7.27, hdpth=0.85, hdpth_min=1.12, stspd_min=3.70, plev_srcw=542.19 )
add_case( gweff=0.66, cfrac= 6.73, hdpth=0.56, hdpth_min=2.00, stspd_min=2.24, plev_srcw=837.50 )
add_case( gweff=0.69, cfrac= 8.74, hdpth=0.84, hdpth_min=3.88, stspd_min=0.27, plev_srcw=514.06 )
add_case( gweff=0.72, cfrac= 8.13, hdpth=1.11, hdpth_min=1.25, stspd_min=0.75, plev_srcw=921.88 )
add_case( gweff=0.75, cfrac= 6.23, hdpth=0.56, hdpth_min=4.62, stspd_min=1.11, plev_srcw=598.44 )
add_case( gweff=0.78, cfrac= 8.92, hdpth=0.32, hdpth_min=2.50, stspd_min=3.34, plev_srcw=781.25 )
add_case( gweff=0.81, cfrac= 6.77, hdpth=1.02, hdpth_min=3.38, stspd_min=0.15, plev_srcw=682.81 )
add_case( gweff=0.84, cfrac= 4.98, hdpth=0.95, hdpth_min=1.75, stspd_min=0.42, plev_srcw=753.12 )
add_case( gweff=0.89, cfrac= 7.28, hdpth=0.66, hdpth_min=4.12, stspd_min=1.65, plev_srcw=654.69 )

#-------------------------------------------------------------------------------
# new L72 ensemble

### Ensemble values from => https://acme-climate.atlassian.net/wiki/spaces/QIE/pages/4791500859/2024-11-21+Initial+sample

# add_case( nlev=72, gweff=0.35, cfrac=10, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # v3 defaults

# add_case( nlev=72, gweff=0.18, cfrac=10.95, hdpth=0.48, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.13, cfrac=18.87, hdpth=0.55, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.09, cfrac=20.33, hdpth=0.99, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# # add_case( nlev=72, gweff=0.07, cfrac=28.99, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# # add_case( nlev=72, gweff=0.14, cfrac=36.95, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.28, cfrac= 5.86, hdpth=0.71, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.32, cfrac=15.00, hdpth=0.83, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.34, cfrac=25.64, hdpth=1.04, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# # add_case( nlev=72, gweff=0.21, cfrac=28.28, hdpth=1.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.25, cfrac=33.11, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.50, cfrac= 8.76, hdpth=0.92, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.36, cfrac=14.13, hdpth=1.13, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=21.60, hdpth=1.26, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=32.59, hdpth=0.31, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.40, cfrac=37.86, hdpth=0.66, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80
# add_case( nlev=72, gweff=0.57, cfrac= 7.70, hdpth=1.24, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.62, cfrac=16.32, hdpth=1.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.55, cfrac=22.14, hdpth=0.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.52, cfrac=26.04, hdpth=0.57, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# # add_case( nlev=72, gweff=0.60, cfrac=39.84, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.69, cfrac=10.53, hdpth=1.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.71, cfrac=12.36, hdpth=0.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.78, cfrac=24.44, hdpth=0.62, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.68, cfrac=31.00, hdpth=0.85, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac=35.69, hdpth=1.08, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# add_case( nlev=72, gweff=0.21, cfrac=19.51, hdpth=0.36, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.10, cfrac=18.23, hdpth=1.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac= 9.11, hdpth=0.60, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.59, cfrac=15.62, hdpth=0.67, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.66, cfrac=13.34, hdpth=1.10, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.26, cfrac= 7.22, hdpth=1.06, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac=17.73, hdpth=1.32, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=11.74, hdpth=0.42, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.52, cfrac= 5.58, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case=None,nyr=None, gweff=None,cfrac=None,hdpth=None, 
         hdpth_min=None,stspd_min=None,plev_srcw=None):
   if case is None: exit(' one or more arguments not provided?')

   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   if clear_zppy_status:
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         os.remove(file_name)
   #------------------------------------------------------------------------------------------------
   if check_zppy_status:
      status_path = f'{case_root}/post/scripts'
      print(' '*4+clr.END+status_path+clr.END)
      status_files = glob.glob(f'{status_path}/*status')
      max_len = 0
      for file_path in status_files:
         file_name = file_path.replace(f'{status_path}/','')
         max_len = max(len(file_name),max_len)
      for file_path in status_files:
         file_name = file_path.replace(f'{status_path}/','')
         cmd = f'tail {file_path} '
         proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
         (msg, err) = proc.communicate()
         msg = msg.strip()
         msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
         msg = msg.replace('WAITING',f'{clr.YELLOW}WAITING{clr.END}')
         msg = msg.replace('RUNNING',f'{clr.YELLOW}RUNNING{clr.END}')
         msg = msg.replace('OK',f'{clr.GREEN}OK{clr.END}')
         print(' '*6+f'{clr.CYAN}{file_name:{max_len}}{clr.END} : {msg}')
   #------------------------------------------------------------------------------------------------
   if run_zppy:
      # Clear status files that don't indicate "OK"
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         file_ptr = open(file_name)
         contents = file_ptr.read().split()
         if contents[0]!='OK': os.remove(file_name)

      # dynamically create the zppy config file
      zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
      file = open(zppy_file_name,'w')
      file.write(get_zppy_config(case,case_root,nyr))
      file.close()

      print(f'  zppy cfg => {zppy_file_name}')

      # submit the zppy job
      run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
   #------------------------------------------------------------------------------------------------
   if calc_hovmoller:
      lat1,lat2 = -5,5
      remap_lev = np.array([ 1., 2., 3., 5., 7., 10., 20., 30., 50., 70., 100., 125., 150.])
      dst_file  = f'{case_root}/{case}.hovmoller.nc'
      print(); print(f'  dst_file: {clr.CYAN}{dst_file}{clr.END}')
      #-------------------------------------------------------------------------
      # file_path = f'{case_root}/archive/atm/hist/*.eam.h0.*'
      file_path = f'{case_root}/post/atm/90x180/ts/monthly/{nyr}yr/U_199501*'
      file_list = sorted(glob.glob(file_path))
      if file_list==[]: 
         print(f'\nfile_path: {file_path}'); raise ValueError('calc_hovmoller: no files found!')
      #-------------------------------------------------------------------------
      # print()
      # for f in file_list: print(f)
      # print()
      # exit()
      #-------------------------------------------------------------------------
      ds = xr.open_mfdataset(file_list)
      data = QBO_methods.interpolate_to_pressure(ds,'U',remap_lev,'PS',interp_type=2,extrap_flag=False)
      area = ds['area']
      data = data.sel(lat=slice(lat1,lat2))
      area = area.sel(lat=slice(lat1,lat2))
      data = (data*area).sum(dim=('lon','lat')) / area.sum(dim=('lon','lat'))
      #-------------------------------------------------------------------------
      ds_out = xr.Dataset()
      ds_out['U']            = data
      ds_out['lat1']         = lat1
      ds_out['lat2']         = lat2
      ds_out['gweff']        = gweff
      ds_out['cfrac']        = cfrac
      ds_out['hdpth']        = hdpth
      ds_out['hdpth_min']    = hdpth_min
      ds_out['stspd_min']    = stspd_min
      ds_out['plev_srcw']    = plev_srcw
      ds_out.to_netcdf(path=dst_file,mode='w')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss=E3SM/2024-SciDAC/{case} . 2>&1 | tee {zstash_log_root}/zstash_{case}_create_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_check:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss=E3SM/2024-SciDAC/{case} 2>&1 | tee {zstash_log_root}/zstash_{case}_check_{timestamp}.log ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss=E3SM/2024-SciDAC/{case}  2>&1 | tee {zstash_log_root}/zstash_{case}_update_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if cp_post_to_cfs:
      # os.umask(511)
      dst_root = '/global/cfs/cdirs/m4310/whannah/E3SM/2024-SciDAC-L80'
      src_dir = f'{case_root}/post/atm/90x180/ts/monthly/{nyr}yr'
      dst_dir = f'{dst_root}/{case}'
      if not os.path.exists(dst_root): os.mkdir(dst_root)
      if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
      run_cmd(f'cp {src_dir}/U_* {dst_dir}/')
      run_cmd(f'cp {case_root}/{case}.hovmoller.nc {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   # if delete_data:
   #    file_list = []
   #    file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
   #    file_list += glob.glob(f'{case_root}/run/*.nc')
   #    # if len(file_list)>10:
   #    #    print()
   #    #    for f in file_list: print(f)
   #    #    print()
   #    #    exit()
   #    if len(file_list)>0: 
   #       print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
   #       for f in file_list:
   #          os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def get_zppy_config(case_name,case_root,nyr):
   short_name = case_name
   grid,map_file = '90x180','/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_aave.nc'
   # grid,map_file = '180x360','/global/homes/w/whannah/maps/map_ne30pg2_to_180x360_aave.nc'
   # grid,map_file = '180x360','/global/homes/z/zender/data/maps/map_ne30pg2_to_cmip6_180x360_aave.20200201.nc'
   yr1,yr2,ts_nyr = 1995,1995+nyr-1,nyr
   return f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = /global/cfs/cdirs/e3sm/www/whannah/2024-SciDAC
machine = "pm-cpu"
partition = batch
environment_commands = "source {unified_env}"

[climo]
active = True
walltime = "1:00:00"
years = "{yr1}:{yr2}:{nyr}",

  [[ atm_monthly_{grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"

[ts]
active = True
walltime = "0:30:00"
years = "{yr1}:{yr2}:{ts_nyr}",

  [[ atm_monthly_{grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

  [[ atm_monthly_glb ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = "glb"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

  [[ land_monthly ]]
  input_subdir = "archive/lnd/hist"
  input_files = "elm.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"
  vars = "FSH,RH2M"
  extra_vars = "landfrac"
'''
# [e3sm_diags]
# active = True
# years = "{yr1}:{yr2}:{nyr}",
# ts_num_years = {ts_nyr}
# ref_start_yr = 1979
# ref_final_yr = 2016
# walltime = "24:00:00"

#   [[ atm_monthly_{grid}_aave ]]
#   short_name = '{short_name}'
#   grid = '{grid}'
#   sets = 'lat_lon','zonal_mean_xy','zonal_mean_2d','polar','cosp_histogram','meridional_mean_2d','enso_diags','qbo','annual_cycle_zonal_mean','zonal_mean_2d_stratosphere'
#   vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
#   reference_data_path = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/climatology'
#   obs_ts = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series'
#   dc_obs_climo = '/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags/climatology/'
#   output_format_subplot = "pdf",

# [global_time_series]
# active = True
# atmosphere_only = True
# years = "{yr1}-{yr2}", 
# ts_num_years = {ts_nyr}
# figstr = "{short_name}"
# experiment_name = "{case_name}"
# ts_years = "{yr1}-{yr2}",
# climo_years = "{yr1}-{yr2}",

# '''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   # run_cmd(f'source {unified_env}')

   for n in range(len(case_list)):
      # print_line()
      main( case=case_list[n], nyr=nyr_list[n], 
            gweff=gweff_list[n], 
            cfrac=cfrac_list[n], 
            hdpth=hdpth_list[n], 
            hdpth_min=hdpth_min_list[n], 
            stspd_min=stspd_min_list[n], 
            plev_srcw=plev_srcw_list[n], 
          )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
