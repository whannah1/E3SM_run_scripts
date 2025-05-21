#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit = False,False,False,False,False

acct = 'cli145' # cli115 / cli145

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

print_commands_only = False

# clean        = True
newcase      = True
# config       = True
# build        = True
# submit       = True



stop_opt,stop_n,walltime = 'nsteps',5,'0:10'

# src_dir  = top_dir+'E3SM_SRC1/'; compset = 'F2010'
src_dir  = top_dir+'E3SM_SRC2/'; compset = 'F2010'

# src_dir  = top_dir+'E3SM_SRC1/'; compset = 'F-EAM-AQP1'
# src_dir  = top_dir+'E3SM_SRC2/'; compset = 'FAQP'

# src_dir  = top_dir+'E3SM_SRC1/'; compset = 'F-MMF1-AQP1'
# src_dir  = top_dir+'E3SM_SRC2/'; compset = 'FAQP-MMF1'


src = src_dir.replace(top_dir,'').replace('/','').replace('/','')

case = '.'.join(['E3SM','TEST_COMPSET',src,compset,'00']) # baseline

grid = 'ne4pg2_ne4pg2'
num_nodes = 1

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')


max_task_per_node = 42
max_mpi_per_node,atm_nthrds  = 42,1
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=True,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   if print_commands_only: 
      print(f'{msg}')
   else:
      print(f'\n{msg}')
      if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   # # Check if directory already exists
   # if not print_commands_only:
   #    if os.path.isdir(f'{case_dir}/{case}'): 
   #       exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid} -mach summit '
   cmd += f' -compiler gnu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
else:
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)

print()
run_cmd('./xmlquery CAM_CONFIG_OPTS',suppress_output=False)
print()

#---------------------------------------------------------------------------------------------------
# Configure
if config :
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Submit
if submit : 
   # Set some run-time stuff
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   # Submit the run
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
