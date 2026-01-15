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
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
run_zppy,clear_zppy_status,check_zppy_status,st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False,False,False,False
extract_h0 = False

acct = 'm4310'

# st_archive        = True
# clear_zppy_status = True
# check_zppy_status = True
# run_zppy          = True
# lt_archive_create = True
# lt_archive_update = True
extract_h0        = True

case_list = []
root_list = []
def add_case(case,root):
   case_list.append(case)
   root_list.append(root)

scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'

add_case('E3SM.2024-coriolis-00.GNUCPU.ne30pg2_oECv3.F2010.NHS-off.NCT-off',scratch_root_cpu)
add_case('E3SM.2024-coriolis-00.GNUCPU.ne30pg2_oECv3.F2010.NHS-on.NCT-off',scratch_root_cpu)
add_case('E3SM.2024-coriolis-00.GNUCPU.ne30pg2_oECv3.F2010.NHS-on.NCT-on',scratch_root_cpu)
# add_case('E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-off.NCT-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-on.NCT-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-on.NCT-on',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-05.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NHS-off.NCT-off.NXY_64_1.XU-off.XW-off.SU-off.SW-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-05.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NHS-on.NCT-off.NXY_64_1.XU-off.XW-off.SU-off.SW-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-05.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NHS-on.NCT-on.NXY_64_1.XU-off.XW-off.SU-off.SW-off',scratch_root_gpu)

# # new cases for QBO diagnosis
# add_case('E3SM.2024-coriolis-01.GNUGPU.ne30pg2_EC30to60E2r2.F2010-MMF1.NXY_64_1.NHS-off.NCT-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-01.GNUGPU.ne30pg2_EC30to60E2r2.F2010-MMF1.NXY_64_1.NHS-on.NCT-off',scratch_root_gpu)
# add_case('E3SM.2024-coriolis-01.GNUGPU.ne30pg2_EC30to60E2r2.F2010-MMF1.NXY_64_1.NHS-on.NCT-on',scratch_root_gpu)


hpss_root = 'E3SM/2024-coriolis'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case,root):
   if case is None: exit(' case argument not provided?')
   if root is None: exit(' root argument not provided?')

   case_root = f'{root}/{case}'

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
   # if clear_zppy_status:
   #    status_files = glob.glob(f'{case_root}/post/scripts/*status')
   #    for file_name in status_files:
   #       os.remove(file_name)
   #------------------------------------------------------------------------------------------------
   # if check_zppy_status:
   #    status_path = f'{case_root}/post/scripts'
   #    print(' '*4+clr.END+status_path+clr.END)
   #    status_files = glob.glob(f'{status_path}/*status')
   #    max_len = 0
   #    for file_path in status_files:
   #       file_name = file_path.replace(f'{status_path}/','')
   #       max_len = max(len(file_name),max_len)
   #    for file_path in status_files:
   #       file_name = file_path.replace(f'{status_path}/','')
   #       cmd = f'tail {file_path} '
   #       proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
   #       (msg, err) = proc.communicate()
   #       msg = msg.strip()
   #       msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
   #       msg = msg.replace('WAITING',f'{clr.YELLOW}WAITING{clr.END}')
   #       msg = msg.replace('RUNNING',f'{clr.YELLOW}RUNNING{clr.END}')
   #       msg = msg.replace('OK',f'{clr.GREEN}OK{clr.END}')
   #       print(' '*6+f'{clr.CYAN}{file_name:{max_len}}{clr.END} : {msg}')
   #------------------------------------------------------------------------------------------------
   # if run_zppy:
   #    # Clear status files that don't indicate "OK"
   #    status_files = glob.glob(f'{case_root}/post/scripts/*status')
   #    for file_name in status_files:
   #       file_ptr = open(file_name)
   #       contents = file_ptr.read().split()
   #       if contents[0]!='OK': os.remove(file_name)

   #    # dynamically create the zppy config file
   #    zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
   #    file = open(zppy_file_name,'w')
   #    file.write(get_zppy_config(case,case_root))
   #    file.close()

   #    print(f'  zppy cfg => {zppy_file_name}')

   #    # submit the zppy job
   #    run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if extract_h0:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash extract --hpss={hpss_root}/{case} "archive/atm/hist/*eam.h0*"  2>&1 | tee zstash_upextract_h0_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
# def get_zppy_config(case_name,case_root):
#    short_name = case_name
#    # grid,map_file = '90x180','/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_aave.nc'
#    grid,map_file = '180x360','/global/homes/w/whannah/maps/map_ne30pg2_to_180x360_aave.nc'
#    # grid,map_file = '180x360','/global/homes/z/zender/data/maps/map_ne30pg2_to_cmip6_180x360_aave.20200201.nc'
#    yr1,yr2,nyr,ts_nyr = 1984,1993,10,10
#    # yr1,yr2,nyr,ts_nyr = 1984,2003,20,20
#    return f'''
# [default]
# account = {acct}
# input = {case_root}
# output = {case_root}
# case = {case_name}
# www = /global/cfs/cdirs/e3sm/www/whannah/2023-SciDAC
# machine = "pm-cpu"
# partition = batch
# environment_commands = "source {unified_env}"

# [climo]
# active = True
# walltime = "1:00:00"
# years = "{yr1}:{yr2}:{nyr}",

#   [[ atm_monthly_{grid}_aave ]]
#   input_subdir = "archive/atm/hist"
#   input_files = "eam.h0"
#   mapping_file = {map_file}
#   grid = "{grid}"
#   frequency = "monthly"

# [ts]
# active = True
# walltime = "0:30:00"
# years = "{yr1}:{yr2}:{ts_nyr}",

#   [[ atm_monthly_{grid}_aave ]]
#   input_subdir = "archive/atm/hist"
#   input_files = "eam.h0"
#   mapping_file = {map_file}
#   grid = "{grid}"
#   frequency = "monthly"
#   vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

#   [[ atm_monthly_glb ]]
#   input_subdir = "archive/atm/hist"
#   input_files = "eam.h0"
#   mapping_file = "glb"
#   frequency = "monthly"
#   vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

#   [[ land_monthly ]]
#   input_subdir = "archive/lnd/hist"
#   input_files = "elm.h0"
#   mapping_file = {map_file}
#   grid = "{grid}"
#   frequency = "monthly"
#   vars = "FSH,RH2M"
#   extra_vars = "landfrac"

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

   for n in range(len(case_list)):
      print('-'*80)
      main( case=case_list[n], root=root_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
