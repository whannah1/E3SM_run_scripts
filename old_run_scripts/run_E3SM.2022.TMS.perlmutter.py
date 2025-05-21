#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC1/' # whannah/mmf/2022-coupled-historical-rebase

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue = 'regular'  # regular / debug 

# stop_opt,stop_n,resub,walltime = 'nsteps',4, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,10-1,'5:00:00'


### common settings
ne,npg    = 30,2
grid      = f'ne{ne}pg{npg}_oECv3'
compset   = 'F2010-MMF1'
arch      = 'GNUGPU'
num_nodes = 64

# case_list = ['E3SM','TMS-00',compset,grid,'tms-off'] # initial version - 2022/11/8
case_list = ['E3SM','TMS-00',compset,grid,'tms-on' ] # initial version - 2022/11/8

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
# if grid=='ne30pg2_r05_oECv3':land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
if grid=='ne30pg2_oECv3':
   land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   land_data_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   # land_data_file = 'surfdata_ne30pg2_simyr2010_c201210.nc'
   land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
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
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   # Enable turbulent mountain stress
   if 'tms-off' in case: file.write(' do_tms = .false. \n')
   if 'tms-on'  in case: file.write(' do_tms = .true. \n')
   file.close()
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
   if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
   if 'CPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
