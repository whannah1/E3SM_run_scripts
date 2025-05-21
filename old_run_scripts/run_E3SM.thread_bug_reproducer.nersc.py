#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime, shutil
import xml.etree.ElementTree as ET
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
acct = 'm3312'    # m3312 / m3305
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # branch => whannah/atm/model_aero_bug_fix
#---------------------------------------------------------------------------------------------------
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
#---------------------------------------------------------------------------------------------------
debug_mode = True
queue = 'debug' # regular / debug
stop_opt,stop_n,resub,walltime = 'nstep',3,0,'00:30:00'
ne,npg = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2'
# compset,num_nodes = 'WCYCL1850',30
compset,num_nodes = 'WCYCL1850',18
#---------------------------------------------------------------------------------------------------
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 1,1,1
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 2,1,1
NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 3,1,1
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 3,3,3
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 4,1,1
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 4,2,2
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE,NTHRDS_LND = 5,1,1,1
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE,NTHRDS_LND = 5,2,2,1
# NTHRDS_ATM,NTHRDS_OCN,NTHRDS_ICE = 2,1,1; BUG_FIX_VER = 1
#---------------------------------------------------------------------------------------------------
case_list = ['E3SM','2022-THRD-BUG-00',f'ne{ne}pg{npg}',compset,f'NN_{num_nodes}',f'NT_{NTHRDS_ATM}_{NTHRDS_OCN}_{NTHRDS_ICE}']
if 'BUG_FIX_VER' in locals(): case_list.append(f'BFV_{BUG_FIX_VER}')
if debug_mode: case_list.append('debug')
case = '.'.join(case_list)
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
task_per_node = 64
atm_ntasks = task_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd = cmd + f' -mach cori-knl  -compset {compset} -res {grid}'
   cmd += f' -compiler gnu    -pecount {atm_ntasks}x{NTHRDS_ATM} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ICE={NTHRDS_ICE}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_OCN={NTHRDS_OCN}')
   if 'NTHRDS_LND' in locals():
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_LND={NTHRDS_LND}')
   #----------------------------------------------------------------------------
   cpp_opt = ''
   if 'BUG_FIX_VER' in locals():
      if BUG_FIX_VER==1: cpp_opt += ' -DBUGFIX_REALLOC'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      run_cmd(cmd+f' -val \" -cppdefs \' {cpp_opt} \'  \" ')
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build :
   if debug_mode:
      (debug_flag, err) = sp.Popen('./xmlquery DEBUG    --value', stdout=sp.PIPE, shell=True, \
                                   universal_newlines=True).communicate()
      if debug_flag=='FALSE':
         run_cmd('./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DYAKL_DEBUG \'  \" ')
         run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit :
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
