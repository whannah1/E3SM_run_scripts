#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
Below are commands to create grid and map files. 
copying and pasting all this into the terminal should work if
 - the directories ~/grids and ~/maps exist
 - NCO is installed in your path or conda environment

NE=30
SRC_GRID=ne${NE}pg2
DST_NY=90
DST_NX=180
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
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
run_zppy,clear_zppy_status,check_zppy_status,st_archive,fix_st_archive,lt_archive_create,lt_archive_update = False,False,False,False,False,False,False
lt_archive_extract = False

acct = 'm3312'

# st_archive        = True
# fix_st_archive    = True
# lt_archive_create = True
# lt_archive_update = True
lt_archive_extract = True

hpss_root = 'E3SM/2023-MMF-THROTTLING'


# Build list of properties that define each case
compset_list,nx_list,ny_list = [],[],[]
def add_case(compset_in,nx_in,ny_in):
   compset_list.append(compset_in)
   nx_list.append(nx_in)
   ny_list.append(ny_in)

# add_case('F2010-MMF1',  8, 1)
# add_case('F2010-MMF1', 16, 1)
add_case('F2010-MMF1', 32, 1)
# add_case('F2010-MMF1', 64, 1)
# add_case('F2010-MMF1',128, 1)
# add_case('F2010-MMF1',256, 1)
# add_case('F2010-MMF1',512, 1)
# add_case('F2010-MMF1',  8, 4)
# add_case('F2010-MMF1', 16, 4)
add_case('F2010-MMF1', 32, 4)
# add_case('F2010-MMF1', 64, 4)
# add_case('F2010-MMF1',128, 4)
# add_case('F2010-MMF1',256, 4)
# add_case('F2010-MMF1',512, 4)
# add_case('F2010-MMF1',  8, 8)
# add_case('F2010-MMF1', 16, 8)
add_case('F2010-MMF1', 32, 8)
# add_case('F2010-MMF1', 64, 8)
# add_case('F2010-MMF1',128, 8)
# add_case('F2010-MMF1',256, 8)
# add_case('F2010-MMF1',512, 8)

add_case('F2010-MMF1', 32, 32)

# add_case('FAQP-MMF1',   8, 1)
# add_case('FAQP-MMF1',  16, 1)
# add_case('FAQP-MMF1',  32, 1)
# add_case('FAQP-MMF1',  64, 1)
# add_case('FAQP-MMF1', 128, 1)
# add_case('FAQP-MMF1', 256, 1)
# add_case('FAQP-MMF1', 512, 1)
# add_case('FAQP-MMF1',   8, 4)
# add_case('FAQP-MMF1',  16, 4)
# add_case('FAQP-MMF1',  32, 4)
# add_case('FAQP-MMF1',  64, 4)
# add_case('FAQP-MMF1', 128, 4)
add_case('FAQP-MMF1', 256, 4)
# add_case('FAQP-MMF1', 512, 4)
# add_case('FAQP-MMF1',   8, 8)
# add_case('FAQP-MMF1',  16, 8)
# add_case('FAQP-MMF1',  32, 8)
# add_case('FAQP-MMF1',  64, 8)
add_case('FAQP-MMF1', 128, 8)
# add_case('FAQP-MMF1', 256, 8)
# add_case('FAQP-MMF1', 512, 8)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset=None,nx=None,ny=None):

   arch = 'GNUGPU'
   grid = 'ne4pg2_oQU480'
   ens_num = '02' # new runs to overcome issue from perlmutter maintenance - also switch to ne4

   case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

   case_root = os.getenv('PSCRATCH')+f'/e3sm_scratch/pm-gpu/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      ### this doesn't work for some reason...? 
      ### (it also screws up the alt approach below to move stuff afterwards)
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      # run_cmd(f'./xmlquery DOUT_S_ROOT ')

      run_cmd('./case.st_archive')

      
   if fix_st_archive:
      # use this when if you forgot to change DOUT_S_ROOT above
      run_cmd(f'mv {case_root}/archive/{case}/* {case_root}/archive/ ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      log_file = f'zstash_create_{case}_{timestamp}.log'
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {log_file}')
      print(f'\nlog file: {case_root}/{log_file}')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      log_file = f'zstash_update_{case}_{timestamp}.log'
      # Update the HPSS archive
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {log_file}')
      print(f'\nlog file: {case_root}/{log_file}')
   #------------------------------------------------------------------------------------------------
   if lt_archive_extract:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      log_file = f'zstash_extract_{case}_{timestamp}.log'
      run_cmd(f'source {unified_env}; zstash extract --hpss={hpss_root}/{case} "archive/atm/hist/*.eam.h0.*"   2>&1 | tee {log_file}')
      print(f'\nlog file: {case_root}/{log_file}')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for c in range(len(compset_list)):
      print('-'*80)
      main( compset=compset_list[c], nx=nx_list[c], ny=ny_list[c] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
