#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
# src_dir  = top_dir+'E3SM_SRC1/' # whannah/mmf/2022-coupled-historical-rebase

clean        = True
# newcase      = True
# config       = True
build        = True
# submit       = True
# continue_run = True

debug_mode = False

# queue = 'regular'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'


### common settings
ne,npg    = 4,0; grid = f'ne{ne}_ne{ne}'; num_nodes = 1
# compset   = 'FSCM-ARM97-MMF1-SAM'
compset   = 'FSCM-ARM97-MMF1-PAM'
# ne,npg    = 4,2; grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'; num_nodes = 1
# ne,npg    = 30,2; grid = f'ne{ne}pg{npg}_oECv3'; num_nodes = 64
# compset   = 'F2010-MMF1'
arch      = 'INTEL'
# arch      = 'GNU'


case_list = ['E3SM','PAM-DEV-CORI-00',arch,compset,grid]; src_dir = top_dir+'/E3SM_SRC4' # 


if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

atm_nthrds = 1
if 'FSCM' in compset:
   atm_ntasks = 1
else:   
   atm_ntasks = 64*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNU':   cmd += f' -mach cori-knl -compiler gnu  '
   if arch=='INTEL': cmd += f' -mach cori-knl -compiler intel  '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   # nfile = 'user_nl_eam'
   # file = open(nfile,'w')
   # file.write(" fincl1    = 'Z3','CLDLIQ','CLDICE','MMF_DU'") 
   # file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'land_init_file' in locals() or 'land_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
