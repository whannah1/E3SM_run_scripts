#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = top_dir+'/Cases/'
src_dir  = top_dir+'/E3SM_SRC2/' # master as of Oct 13, 2022

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'nsteps',10, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32, 0,'1:00:00'

# ne,npg = 4,2; num_nodes = 2 ; grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'

ne,npg = 30,2; num_nodes = 32 ; grid = f'ne{ne}pg{npg}_EC30to60E2r2' # match v2 PI control
# ne,npg = 30,2; num_nodes = 64 ; grid = f'ne{ne}pg{npg}_EC30to60E2r2' # match v2 PI control


compset = 'F2010-MMF1'
# compset = 'F2010-MMF1'
# compset = 'FAQP-MMF1'
# compset = 'F2010'
# compset = 'WCYCL1850'

arch = 'CORI-GNU'

case_list = ['E3SM','PIO-DEBUG-00',arch,compset,grid,f'NN_{num_nodes}'] # initial version to reproduce error

# case_list = ['E3SM','PIO-DEBUG-22',arch,compset,grid,f'NN_{num_nodes}'] # add MPICH_COLL_SYNC=1
# case_list = ['E3SM','PIO-DEBUG-23',arch,compset,grid,f'NN_{num_nodes}'] # add MPICH_COLL_OPT_OFF=1 & MPICH_SHARED_MEM_COLL_OPT=0
# case_list = ['E3SM','PIO-DEBUG-24',arch,compset,grid,f'NN_{num_nodes}'] # redo "old" fix with scorpio classic to compare throughput
# case_list = ['E3SM','PIO-DEBUG-25',arch,compset,grid,f'NN_{num_nodes}'] # Noel's suggested fix

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

max_mpi_per_node,atm_nthrds  = 64,1
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='CORI-GNU': cmd += f' -mach cori-knl -compiler gnu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if debug_mode: run_cmd('./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DPIO_ENABLE_LOGGING=OFF \'  \"')
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if 'PIO-DEBUG-24' in case: run_cmd('./xmlchange PIO_VERSION=1 ')
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
