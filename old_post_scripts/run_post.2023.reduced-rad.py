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

acct = 'm3312'

# st_archive        = True
# fix_st_archive    = True
# lt_archive_create = True
# lt_archive_update = True

hpss_root = 'E3SM/2023-RAD-SENS'

# Build list of properties that define each case
crm_nx_list,crm_dx_list,rad_nx_list,mcica_flag_list  = [],[],[],[]
def add_case(crm_nx_in,crm_dx_in,rad_nx_in,mcica_flag_in):
   crm_nx_list.append(crm_nx_in)
   crm_dx_list.append(crm_dx_in)
   rad_nx_list.append(rad_nx_in)
   mcica_flag_list.append(mcica_flag_in)

# 2023-12-07 login31 screen sesh for lt_archive_create 
# 2024-02-07 login21 screen sesh for lt_archive_update 

# add_case( 128, 1000, 128, True )
# add_case( 128, 1000,  64, True )
# add_case( 128, 1000,  32, True )
# add_case( 128, 1000,  16, True )
# add_case( 128, 1000,   8, True )
# add_case( 128, 1000,   4, True )
# add_case( 128, 1000,   2, True )
# add_case( 128, 1000,   1, True )

# add_case( 128, 1000, 128, False )
# add_case( 128, 1000,  64, False )
# add_case( 128, 1000,  32, False )
# add_case( 128, 1000,  16, False )
# add_case( 128, 1000,   8, False )
# add_case( 128, 1000,   4, False )
# add_case( 128, 1000,   2, False )
# add_case( 128, 1000,   1, False ) 

# add_case(  64, 2000,  64, True )
# add_case(  64, 2000,  32, True )
# add_case(  64, 2000,  16, True )
# add_case(  64, 2000,   8, True )
# add_case(  64, 2000,   4, True )
# add_case(  64, 2000,   2, True )
# add_case(  64, 2000,   1, True )

# add_case(  64, 2000,  64, False )
# add_case(  64, 2000,  32, False )
# add_case(  64, 2000,  16, False )
# add_case(  64, 2000,   8, False )
# add_case(  64, 2000,   4, False )
# add_case(  64, 2000,   2, False )
# add_case(  64, 2000,   1, False )

# extended runs
add_case(  64, 2000,  64, True )
add_case(  64, 2000,   8, True )
add_case(  64, 2000,   1, True )
add_case(  64, 2000,  64, False )
add_case(  64, 2000,   8, False )
add_case(  64, 2000,   1, False )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(crm_nx=None,crm_dx=None,rad_nx=None,mcica_flag=None):
   if rad_nx is None: exit('rad_nx argument not provided?')

   ne,npg = 30,2
   crm_ny = 1
   compset = 'F2010-MMF1'
   grid = f'ne30pg2_oECv3'
   arch = 'GNUGPU'

   mcica_str = 'MCICA_ON' if mcica_flag else 'MCICA_OFF'

   case='.'.join(['E3SM','2023-RAD-SENS-00',arch,grid,compset,f'NXY_{crm_nx}x{crm_ny}',f'RNX_{rad_nx}',f'{mcica_str}'])

   case_root = os.getenv('PSCRATCH')+f'/e3sm_scratch/pm-gpu/{case}'

   print(case); return

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
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(rad_nx_list)):
      print('-'*80)
      main(crm_nx=crm_nx_list[n],crm_dx=crm_dx_list[n],rad_nx=rad_nx_list[n],mcica_flag=mcica_flag_list[n])
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
