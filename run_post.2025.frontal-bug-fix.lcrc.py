#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd):  print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd);  return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
st_archive = False
run_zppy,clear_zppy_status,check_zppy_status= False,False,False
lt_archive_create,lt_archive_update,lt_archive_check = False,False,False

acct = 'e3sm'

# st_archive           = True
# clear_zppy_status    = True
# check_zppy_status    = True
run_zppy             = True
# run_zppy_mvm           = True
# lt_archive_create    = True
# lt_archive_update    = True
# lt_archive_check     = True

zstash_log_root = os.getenv('HOME')+'/E3SM/zstash_logs'

#-------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#-------------------------------------------------------------------------------
# NERSC
# mach,part = 'pm-cpu','batch'
# scratch_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
# scratch_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'
# diags_data_obs_root = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm'
# diags_data_test_root = '/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags/climatology/'
# www_path = '/global/cfs/cdirs/e3sm/www/whannah/2024-SciDAC' # NERSC
# unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'

# LCRC
mach,part = 'chrysalis','compute'
scratch_root = '/lcrc/group/e3sm/ac.whannah/scratch/chrys'
diags_data_obs_root = '/lcrc/group/e3sm/diagnostics/observations/Atm/'
diags_data_test_root = '/lcrc/soft/climate/e3sm_diags_data/test_model_data_for_acme_diags/'
www_path = '/lcrc/group/e3sm/public_html/diagnostic_output/whannah'
unified_env = '/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh'


nyr = 5

# add_case(prefix='2025-frnt-gw',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=0)
add_case(prefix='2025-frnt-gw',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=1)
hpss_root = 'E3SM/2025-frnt-gw-bug-fix'

# map_file = '/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_traave.nc'
grid,map_file = '90x180',os.getenv('HOME')+'/maps/map_ne30pg2_to_90x180_aave.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['grid']:
         case_list.append(val.split('_')[0])
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
         # continue
      elif key in ['debug']:
         case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   #----------------------------------------------------------------------------
   case = get_case_name(opts)

   case_root = f'{scratch_root}/{case}'

   #------------------------------------------------------------------------------------------------
   # print(case); return
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_check:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss={hpss_root}/{case} 2>&1 | tee {zstash_log_root}/zstash_check_{case}_{timestamp}.log ')
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
   if 'run_zppy_mvm' not in locals(): run_zppy_mvm = False
   if run_zppy_mvm: # model-vs-model
      base_name = 'E3SM.2025-frnt-gw.ne30pg2.F20TR.NN_32.bugfix_0'
      # Clear status files that don't indicate "OK"
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         file_ptr = open(file_name)
         contents = file_ptr.read().split()
         if contents[0]!='OK': os.remove(file_name)

      # dynamically create the zppy config file
      zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
      file = open(zppy_file_name,'w')
      file.write(get_zppy_config_mvm(case,case_root,nyr,base_name))
      file.close()

      print(f'  zppy cfg => {zppy_file_name}')

      # submit the zppy job
      run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_zppy_config(case_name,case_root,nyr):
   short_name = case_name
   # grid,map_file = '90x180','/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_aave.nc'
   # grid,map_file = '180x360','/global/homes/w/whannah/maps/map_ne30pg2_to_180x360_aave.nc'
   # grid,map_file = '180x360','/global/homes/z/zender/data/maps/map_ne30pg2_to_cmip6_180x360_aave.20200201.nc'
   yr1,yr2,ts_nyr = 1985,1985+nyr-1,nyr
   config_txt = f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = {www_path}
machine = "{mach}"
partition = {part}
environment_commands = "source {unified_env}"
'''
#   config_txt +=  f'''
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
# '''
#   config_txt +=  f'''
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
# '''
   config_txt +=  f'''
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
  reference_data_path = '{diags_data_obs_root}/climatology'
  obs_ts = '{diags_data_obs_root}/time-series'
  dc_obs_climo = '{diags_data_test_root}'
  output_format_subplot = "pdf",

'''
   return config_txt

# [[ land_monthly ]]
# input_subdir = "archive/lnd/hist"
# input_files = "elm.h0"
# mapping_file = {map_file}
# grid = "{grid}"
# frequency = "monthly"
# vars = "FSH,RH2M"
# extra_vars = "landfrac"

# [global_time_series]
# active = True
# atmosphere_only = True
# years = "{yr1}-{yr2}", 
# ts_num_years = {ts_nyr}
# figstr = "{short_name}"
# experiment_name = "{case_name}"
# ts_years = "{yr1}-{yr2}",
# climo_years = "{yr1}-{yr2}",

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_zppy_config_mvm(case_name,case_root,nyr,base_name):
   short_name = case_name
   yr1,yr2,ts_nyr = 1985,1985+nyr-1,nyr
   scratch = '/lcrc/group/e3sm/ac.whannah/scratch/chrys'
   return f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = {www_path}
machine = "{mach}"
partition = {part}
environment_commands = "source {unified_env}"

[e3sm_diags]
run_type = 'model_vs_model'
tag = 'model_vs_model'
ref_name = '{base_name}'
short_ref_name = 'control'
diff_title = 'Test Model - Ref Model'
active = True
years = "{yr1}:{yr2}:{nyr}",
ref_start_yr = {yr1}
ref_final_yr = {yr2}
walltime = "24:00:00"

  [[ atm_monthly_{grid}_aave ]]
  short_name = '{short_name}'
  grid = '{grid}'
  sets = 'lat_lon','zonal_mean_xy','zonal_mean_2d','polar','cosp_histogram','annual_cycle_zonal_mean','zonal_mean_2d_stratosphere'
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
  reference_data_path = '{scratch}/{base_name}/post/atm/90x180/clim'
  output_format_subplot = "pdf",

'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(opt_list)):
      print_line()
      main( opt_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
