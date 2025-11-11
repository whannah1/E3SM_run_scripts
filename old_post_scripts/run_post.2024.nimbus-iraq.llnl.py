#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
# unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
run_zppy,clear_zppy_status,check_zppy_status,st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False,False,False,False

acct = 'nhclilab'

st_archive        = True
lt_archive_create = True
# lt_archive_update = True

case_list = []
root_list = []
def add_case(case,root):
   case_list.append(case)
   root_list.append(root)

scratch_root1 = '/p/lustre1/hannah6/e3sm_scratch'
scratch_root2 = '/p/lustre2/hannah6/e3sm_scratch'

add_case('ELM_spinup.ICRUELM.ne0np4-2024-nimbus-iraq-32x3-pg2.20-yr.2015-10-01',scratch_root2)
add_case('ELM_spinup.ICRUELM.ne0np4-2024-nimbus-iraq-64x3-pg2.20-yr.2015-10-01',scratch_root2)
add_case('ELM_spinup.ICRUELM.ne0np4-2024-nimbus-iraq-128x3-pg2.20-yr.2015-10-01',scratch_root2)

hpss_root = 'E3SM/2024-nimbus-iraq'

'''
Make sure to manually activate unified env
conda activate e3sm-unified
'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
'''
From Yan Feng:
Dst_a1 and _a3 in E3SMv3 correspond to the accumulation and coarse size modes. 
I’d lump the first two arrays:
   dust_aerosol_0.03-0.55um_mixing_ratio
   dust_aerosol_0.55-0.9um_mixing_ratio
from CAMS to dst_a1, and assign
   dust_aerosol_0.9-20um_mixing_ratio
To dst_a3
'''
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
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'zstash create --hpss={hpss_root}/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'zstash update --hpss={hpss_root}/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(case_list)):
      print('-'*80)
      main( case=case_list[n],
            root=root_list[n],
          )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
