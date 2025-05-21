#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
home = os.getenv('HOME')
case_dir = f'{home}/E3SM/Cases/'

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'ndays',183,0,'3:00'

### common settings
ne,npg    = 30,2
grid      = f'ne{ne}pg{npg}_oECv3'
compset   = 'F2010-MMF1'
arch      = 'GNUGPU'
num_nodes = 64

# case_list = ['E3SM','2022-REDUCED-GPT',f'ne{ne}pg{npg}',compset,'CTL']; src_dir=f'{home}/E3SM/E3SM_SRC0/' # master as of Sept 22
case_list = ['E3SM','2022-REDUCED-GPT',f'ne{ne}pg{npg}',compset,'EXP']; src_dir=f'{home}/E3SM/E3SM_SRC5/' # master + brhillman/eam/use-reduced-rrtmgp-gpoints

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files
land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
# land_data_file = 'surfdata_0.5x0.5_simyr2000_c200624.nc'
land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: 
      run_cmd('./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cppdefs \' -DYAKL_DEBUG \'  \" ')
      run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
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
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
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
