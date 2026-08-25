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

SRC_GRID=~/HICCUP/data_scratch/files_grid/scrip_ERA5_721x1440.nc
DST_GRID=~/grids/90x180_scrip.nc
MAP_FILE=~/HICCUP/data_scratch/files_map/map_721x1440_to_90x180_traave.nc
# ncremap -6 --alg_typ=traave --grd_src=$SRC_GRID --grd_dst=$DST_GRID --map=$MAP_FILE

ERA_VAR=ta
SRC_DATA=/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series/ERA5/${ERA_VAR}_197901_201912.nc
DST_DATA=/global/cfs/cdirs/m4310/whannah/E3SM/2025-SciDAC-MF-pilot/ERA5_90x180_${ERA_VAR}_197901_201912.nc
ncremap -m $MAP_FILE -i $SRC_DATA -o $DST_DATA
'''
#---------------------------------------------------------------------------------------------------
'''
nohup python -u run_post.2025.scidac.MF-ensemble-pilot.py > run_post.2025.scidac.MF-ensemble-pilot.py.out &
nohup python -u run_post.2025.scidac.MF-ensemble-pilot.py > run_post.2025.scidac.MF-ensemble-pilot.py.lt_archive_check.out &

nohup python -u run_post.2025.scidac.MF-ensemble-pilot.py > run_post.2025.scidac.MF-ensemble-pilot.py.calc_QOIout &
'''
#---------------------------------------------------------------------------------------------------
''' for long-term archiving
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=10 whannah@dtn01.nersc.gov
nohup python -u run_post.2025.scidac.MF-ensemble-pilot.py > run_post.2025.scidac.MF-ensemble-pilot.lt_archive.out &
2025-11-18 => login40
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime, sys
#---------------------------------------------------------------------------------------------------
# import signal
# def signal_handler(sig, frame):
#    # This function runs when a SIGINT signal (Ctrl+C) is received.
#    print('\nKeyboardInterrupt received. Performing cleanup and exiting gracefully.')
#    sys.exit(0) # Exit the program cleanly
# signal.signal(signal.SIGINT, signal_handler)
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n  '+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
chk_files,st_archive,calc_hovmoller,calc_climatology = False,False,False,False
run_zppy,clear_zppy_status,check_zppy_status= False,False,False
lt_archive_create,lt_archive_check,lt_archive_ls,lt_archive_update = False,False,False,False
cp_post_to_cfs = False

acct = 'm4310'

# chk_files         = True
# st_archive        = True
# clear_zppy_status = True
# check_zppy_status = True
# run_zppy          = True
cp_post_to_cfs    = True
calc_hovmoller    = True
calc_climatology  = True
# lt_archive_create = True
# lt_archive_check  = True
# lt_archive_ls     = True; zstash_ls_str = 'archive/atm/hist/*eam.h0.2004-12.nc'
# lt_archive_update = True
# delete_data       = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'
scratch_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
cfs_root = '/global/cfs/cdirs/m4310/whannah/E3SM/2025-SciDAC-MF-pilot'
hpss_root = '/home/w/whannah/E3SM/2025-SciDAC-MF-pilot'

#-------------------------------------------------------------------------------
if calc_hovmoller or calc_climatology:
   sys.path.append('/global/homes/w/whannah/Research/E3SM/code_QBO')
   import xarray as xr, numpy as np, QBO_diagnostic_methods as QBO_methods
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------

# nyr = 5 # starting 1995
nyr = 10 # starting 1995

# add_case(case='ERA5')

# add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults

add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)

add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

#---------------------------------------------------------------------------------------------------
# def get_grid(opts):
#    grid_short = opts['g']
#    grid = None
#    if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
#    if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
#    if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
#    if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
#    return grid
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   if 'case' in opts:
      return opts['case']
   else:
      case_list = []
      for key,val in opts.items(): 
         if key in ['prefix']:
            case_list.append(val)
         # elif key in ['num_nodes']:
         #    case_list.append(f'NN_{val}')
         elif key in ['g']:
            case_list.append(val)
         elif key in ['debug']:
            case_list.append('debug')
         else:
            if isinstance(val, str):
               case_list.append(f'{key}_{val}')
            else:
               fmt = 'g'
               if key in ['EF','CF','HD','HM','PS','FT','FE','OB','OE']: fmt = '0.3f'
               if key=='CF':fmt='05.2f'
               if key=='PS':fmt='05.1f'
               if key=='FT':fmt='07.4f'
               if key=='OB':fmt='0.6f'
               case_list.append(f'{key}_{val:{fmt}}')
      #----------------------------------------------------------------------------
      case = '.'.join(case_list)
      # clean up the exponential numbers in the case name
      for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
      #----------------------------------------------------------------------------
      return case

#---------------------------------------------------------------------------------------------------
def get_case_root(opts):
   case = get_case_name(opts)
   root = f'{scratch_root}/{case}'
   return root
#---------------------------------------------------------------------------------------------------
def get_cfs_case_root(opts):
   case = get_case_name(opts)
   root = f'{cfs_root}/{case}'
   return root
#---------------------------------------------------------------------------------------------------
def main(opts):
   #------------------------------------------------------------------------------------------------
   if 'g' in opts:
      grid_short = opts['g']
      if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
      if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
      if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
      if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
   #----------------------------------------------------------------------------
   case = get_case_name(opts)
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END}')
   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   case_root = get_case_root(opts)
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
      file.write(get_zppy_config(case,case_root,grid_short,nyr))
      file.close()

      print(f'  zppy cfg => {zppy_file_name}')

      # submit the zppy job
      run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_{case}_create_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_check:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss={hpss_root}/{case} 2>&1 | tee {zstash_log_root}/zstash_{case}_check_{timestamp}.log ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_ls:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash ls --hpss={hpss_root}/{case} "{zstash_ls_str}" ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_{case}_update_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if cp_post_to_cfs:
      if nyr not in [5,10]: raise ValueError(f'nyr={nyr} is not valid for cp_post_to_cfs')
      # os.umask(511)
      dst_dir = get_cfs_case_root(opts)
      if not os.path.exists(cfs_root): os.mkdir(cfs_root)
      if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
      src_dir = f'{case_root}/post/atm/90x180/ts/monthly/{nyr}yr'
      run_cmd(f'cp {src_dir}/U_* {dst_dir}/')
      src_dir = f'{case_root}/post/atm/90x180/clim/{nyr}yr/'
      if nyr== 5: run_cmd(f'cp {src_dir}/{case}_ANN_199501_199912_climo.nc {dst_dir}/')
      if nyr==10: run_cmd(f'cp {src_dir}/{case}_ANN_199501_200412_climo.nc {dst_dir}/')
      # run_cmd(f'cp {case_root}/{case}.hovmoller.nc {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   if calc_hovmoller:
      lat1,lat2 = -5,5
      remap_lev = np.array([ 1., 2., 3., 5., 7., 10., 20., 30., 50., 70., 100., 125., 150.])
      dst_root = get_cfs_case_root(opts)
      dst_file  = f'{dst_root}/QOI_{nyr}yr_hovmoller.nc'
      #-------------------------------------------------------------------------
      print()
      print(f'  Calculating QBO hovmoller')
      print(f'  dst_file: {clr.CYAN}{dst_file}{clr.END}')
      #-------------------------------------------------------------------------
      if case=='ERA5':
         # obs_root,obs_file_prefix = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series/ERA5',''
         # ERA_grid_file = '/global/cfs/projectdirs/m4842/whannah/HICCUP/files_grid/scrip_ERA5_721x1440.nc'
         obs_root,obs_file_prefix = '/global/cfs/cdirs/m4310/whannah/E3SM/2025-SciDAC-MF-pilot','ERA5_90x180_'
         ERA_grid_file = '/global/homes/w/whannah/grids/90x180_scrip.nc'
         file_list = [f'{obs_root}/{obs_file_prefix}ua_197901_201912.nc']
      else:
         # file_path = f'{case_root}/archive/atm/hist/*.eam.h0.*'
         file_path = f'{case_root}/post/atm/90x180/ts/monthly/{nyr}yr/U_199501*'
         file_list = sorted(glob.glob(file_path))
         if file_list==[]: 
            print(f'\nfile_path: {file_path}'); raise ValueError('calc_hovmoller: no files found!')
      #-------------------------------------------------------------------------
      # print(); print(f for f in file_list); print(); exit()
      #-------------------------------------------------------------------------
      ds = xr.open_mfdataset(file_list)
      #----------------------------------------------------------------------
      if case=='ERA5': ds = ds.sel(time=slice('1995',f'{(1995+nyr-1)}'))
      #-------------------------------------------------------------------------
      # print(); print(ds); print(); exit()
      #-------------------------------------------------------------------------
      if case=='ERA5':
         ds['plev'] = ds['plev']/1e2
         ds = ds.rename({'plev':'lev'})
         data = ds['ua'].sel(lev=remap_lev)
         data = data.transpose('time','lev','lat','lon')
         # ds_grid =xr.open_dataset(ERA_grid_file)
         # area = ds_grid['grid_area'].rename({'grid_size':'ncol'})
         # area.assign_coords(lat=data['lat'].values)
      else:
         data = QBO_methods.interpolate_to_pressure(ds,'U',remap_lev,'PS',interp_type=2,extrap_flag=False)
      #-------------------------------------------------------------------------
      area = ds['area']
      data = data.sel(lat=slice(lat1,lat2))
      area = area.sel(lat=slice(lat1,lat2))
      data = (data*area).sum(dim=('lon','lat')) / area.sum(dim=('lon','lat'))
      #-------------------------------------------------------------------------
      ds_out = xr.Dataset()
      ds_out['U']          = data
      ds_out['lat1']       = lat1
      ds_out['lat2']       = lat2
      for key,val in opts.items(): ds_out.attrs[key] = val
      ds_out.attrs['case'] = case
      ds_out.to_netcdf(path=dst_file,mode='w')
   #------------------------------------------------------------------------------------------------
   if calc_climatology:
      var_list = ['U','T']
      remap_lev = np.array([ 1., 2., 3., 5., 7., 10, 20, 30, 50, 70, 100, 125, 150, 175, \
                            200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, \
                            750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000])
      dst_root = get_cfs_case_root(opts)
      dst_file  = f'{dst_root}/QOI_{nyr}yr_climatology.nc'
      #-------------------------------------------------------------------------
      print()
      print(f'  Calculating zonal mean climatology')
      print(f'  dst_file: {clr.CYAN}{dst_file}{clr.END}')
      #-------------------------------------------------------------------------
      ds_out = xr.Dataset()
      for key,val in opts.items(): ds_out.attrs[key] = val
      ds_out.attrs['case'] = case
      #-------------------------------------------------------------------------
      for var in var_list:
         #----------------------------------------------------------------------
         if case=='ERA5':
            # obs_root,obs_file_prefix = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series/ERA5',''
            obs_root,obs_file_prefix = '/global/cfs/cdirs/m4310/whannah/E3SM/2025-SciDAC-MF-pilot','ERA5_90x180_'
            if var=='U': ivar='ua'; input_file = f'{obs_root}/{obs_file_prefix}ua_197901_201912.nc'
            if var=='T': ivar='ta'; input_file = f'{obs_root}/{obs_file_prefix}ta_197901_201912.nc'
         else:
            input_file = f'{case_root}/post/atm/90x180/clim/{nyr}yr/{case}_ANN_199501_{(1995+nyr-1)}12_climo.nc'
         #----------------------------------------------------------------------
         # print(); print(input_file); print(); exit()
         #----------------------------------------------------------------------
         ds = xr.open_mfdataset(input_file)
         #----------------------------------------------------------------------
         # print(); print(ds); print(); exit()
         #----------------------------------------------------------------------
         if case=='ERA5': ds = ds.sel(time=slice('1995',f'{(1995+nyr-1)}'))
         #----------------------------------------------------------------------
         if case=='ERA5':
            ds['plev'] = ds['plev']/1e2
            ds = ds.rename({'plev':'lev'})
            data = ds[ivar].sel(lev=remap_lev)
            data = data.transpose('time','lev','lat','lon')
         else:
            data = QBO_methods.interpolate_to_pressure(ds,var,remap_lev,'PS',interp_type=2,extrap_flag=True)
            data = data.mean(dim='time')
         area = ds['area']
         data = (data*area).sum(dim=('lon')) / area.sum(dim=('lon'))
         #----------------------------------------------------------------------
         # mask out antarctica
         data = data.where( (data['lat']>-65) | (data['lev']<600) )
         #----------------------------------------------------------------------
         # print(); print(data); print(); exit()
         #----------------------------------------------------------------------
         ds_out[var] = data
      #-------------------------------------------------------------------------
      # print(); print(ds_out); print(); exit()
      #-------------------------------------------------------------------------
      ds_out.to_netcdf(path=dst_file,mode='w')
   #------------------------------------------------------------------------------------------------
   # if delete_data:
   #    file_list = []
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/lnd/hist/*.nc')
   #    # file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
   #    # file_list += glob.glob(f'{case_root}/run/*.nc')
   #    #-------------------------------------------------------------------------
   #    # if len(file_list)>10:
   #    #    print()
   #    #    for f in file_list[:10]: print(f)
   #    #    print()
   #    #    exit()
   #    #-------------------------------------------------------------------------
   #    # if len(file_list)>0: 
   #    #    print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
   #    #    for f in file_list:
   #    #       os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def get_zppy_config(case_name,case_root,grid_short,nyr):
   short_name = case_name
   grid,map_file = '90x180',f'/global/homes/w/whannah/maps/map_{grid_short}pg2_to_90x180_traave.nc'
   yr1,yr2,ts_nyr = 1995,1995+nyr-1,nyr
   config_txt = f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = /global/cfs/cdirs/e3sm/www/whannah/2025-SciDAC
machine = "pm-cpu"
partition = batch
environment_commands = "source {unified_env}"
'''
   config_txt += f'''
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
'''
   config_txt += f'''
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
'''
#   [[ land_monthly ]]
#   input_subdir = "archive/lnd/hist"
#   input_files = "elm.h0"
#   mapping_file = {map_file}
#   grid = "{grid}"
#   frequency = "monthly"
#   vars = "FSH,RH2M"
#   extra_vars = "landfrac"
# '''
   config_txt += f'''
[e3sm_diags]
active = True
years = "{yr1}:{yr2}:{nyr}",
ts_num_years = {ts_nyr}
ref_start_yr = 1979
ref_final_yr = 2016
walltime = "24:00:00"

  [[ atm_monthly_{grid}_aave ]]
  short_name = '{short_name}'
  grid = '{grid}'
  sets = 'lat_lon','zonal_mean_xy','zonal_mean_2d','polar','cosp_histogram','meridional_mean_2d','enso_diags','qbo','annual_cycle_zonal_mean','zonal_mean_2d_stratosphere'
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
  reference_data_path = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/climatology'
  obs_ts = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series'
  dc_obs_climo = '/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags/climatology/'
  output_format_subplot = "pdf",

[global_time_series]
active = True
atmosphere_only = True
years = "{yr1}-{yr2}", 
ts_num_years = {ts_nyr}
figstr = "{short_name}"
experiment_name = "{case_name}"
ts_years = "{yr1}-{yr2}",
climo_years = "{yr1}-{yr2}",

'''
   return config_txt
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   
   if chk_files:
      for n in range(len(opt_list)):
         opts = opt_list[n]
         case_name = get_case_name(opts)
         case_root = get_case_root(opts)
         hist_file_list = sorted(glob.glob(f'{case_root}/run/*.eam.h0.*'))
         last_file = hist_file_list[-1].replace(f'{case_root}/run/','')
         num_files = len(hist_file_list)
         print(f'  {(n+1):3}  {case_name}  num_files: {num_files:5}  {clr.GREEN}{last_file}{clr.END}')
      exit()

   for n in range(len(opt_list)):
      main( opt_list[n] )

   # for n in range(len(case_list)):
   #    # print_line()
   #    main( case=case_list[n], nyr=nyr_list[n], 
   #          gweff=gweff_list[n], 
   #          cfrac=cfrac_list[n], 
   #          hdpth=hdpth_list[n], 
   #          hdpth_min=hdpth_min_list[n], 
   #          stspd_min=stspd_min_list[n], 
   #          plev_srcw=plev_srcw_list[n], 
   #        )
   print_line()
   
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
