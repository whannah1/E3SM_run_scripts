#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd):  print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd);  return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime

acct = 'e3sm'

# st_archive           = True
# st_archive_hist      = True
lt_archive_create    = True
# lt_archive_update    = True
# lt_archive_check  = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'

#-------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#-------------------------------------------------------------------------------

# scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
# scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'
scream_scratch = '/pscratch/sd/w/whannah/scream_scratch/pm-gpu'

hpss_root = 'E3SM/2026-impflx'

add_case(case='E3SM.2026-impflx-00.GPU.F2010-SCREAMv1.ne256pg2_ne256pg2.NN_128.iflx_0.gust_0',root=scream_scratch)
add_case(case='E3SM.2026-impflx-00.GPU.F2010-SCREAMv1.ne256pg2_ne256pg2.NN_128.iflx_1.gust_1',root=scream_scratch)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   root = opts['root']
   case = opts['case']
   case_root = f'{root}/{case}'
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END}')
   print(f'  root : {clr.BOLD}{root}{clr.END}');print()
   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   st_archive_loc = False if 'st_archive' not in globals() else st_archive
   if st_archive_loc:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   st_archive_hist_loc = False if 'st_archive_hist' not in globals() else st_archive_hist
   if st_archive_hist_loc:
      os.chdir(f'{case_root}/run')
      run_cmd(f'mv output*.nc ../archive/atm/hist')
   #------------------------------------------------------------------------------------------------
   lt_archive_create_loc = False if 'lt_archive_create' not in globals() else lt_archive_create
   if lt_archive_create_loc:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   lt_archive_update_loc = False if 'lt_archive_update' not in globals() else lt_archive_update
   if lt_archive_update_loc:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   lt_archive_check_loc = False if 'lt_archive_check' not in globals() else lt_archive_check
   if lt_archive_check_loc:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss={hpss_root}/{case} 2>&1 | tee {zstash_log_root}/zstash_check_{case}_{timestamp}.log ')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      print_line()
      main( opt_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
