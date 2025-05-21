#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
ne,npg = 0,0
newcase,config,build,submit,copy_p3_data = False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

newcase      = True
config       = True
build        = True
submit       = True

queue = 'batch'  # batch / debug 

### Compset
# compset='F2010-MMF1'
compset='F2010-MMF2'
# compset='F2010-MMF2-AWFL'

src_dir=top_dir+'/E3SM_SRC0'
arch = 'GNUGPU' # GNUGPU / GNUCPU
ne   = 30

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'

### set grid
if ne==30: npg = 2; grid=f'ne{ne}pg{npg}_oECv3';         num_nodes=32
if ne== 4: npg = 2; grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}'; num_nodes=1

# case_list=['E3SM','PAM-TIMING-2023-00',arch,grid,compset,f'NODES_{num_nodes}']
case_list=['E3SM','PAM-TIMING-2023-00',arch,grid,compset,f'NODES_{num_nodes}i','TPN_12']

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 6,1
# if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 12,1
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config : 
   if ne==4 and npg==2: run_cmd(f'./xmlchange NTASKS_OCN=16,NTASKS_ICE=16')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   # nfile = 'user_nl_eam'
   # file = open(nfile,'w')
   # file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   ### Disable restart file write for timing
   run_cmd('./xmlchange --file env_run.xml --id REST_OPTION --val never')
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
