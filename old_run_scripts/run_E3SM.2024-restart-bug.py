#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
acct = 'e3sm'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => mahf708/eam/output-aer-rad-props

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = True

queue = 'debug'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'nsteps',5,1,'0:30:00'

compset='F2010'

# ne,npg,grid = 30,2,'ne30pg2_oECv3';   num_nodes = 32
ne,npg,grid = 4,2,'ne4pg2_oQU480';  num_nodes = 1
if 'FSCM' in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';   num_nodes = 1

case_list = ['E3SM','2024-RESTART-BUG-00',grid,compset]
if debug_mode: case_list.append('debug')
case='.'.join(case_list)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

case_root = f'{case_dir}/{case}'
#---------------------------------------------------------------------------------------------------
if 'FSCM' in compset: 
   max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
else:
   max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case_root}'
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' -mach pm-cpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
os.chdir(f'{case_root}')
if config : 
   #-------------------------------------------------------
   # Run case setup
   if clean: run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit
if submit : 
   #-------------------------------------------------------
   # atmos namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #-------------------------------------------------------
   # atmos history output
   file.write(' nhtfrq    = 0,-6 \n')
   file.write(' mfilt     = 1,4 \n')
   file.write(" fincl1 = 'MODAL_AER_TAU_SW'") 
   # file.write(" fincl1 = 'P3_input','MODAL_AER_TAU_SW'") 
   # file.write(" fincl1 = 'P3_input'") 
   file.write('\n')
   ### hourly 2D variables
   # file.write(" fincl2    = 'PS','TS','PSL'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'PRECC','PRECSC'")
   # file.write(             ",'PRECL','PRECSL'")
   # file.write(             ",'LHFLX','SHFLX'")                    # surface fluxes
   # file.write(             ",'FSNT','FLNT'")                      # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")                      # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")                    # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")                      # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")              # cloud water path
   # ### daily 3D variables
   # # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'MODAL_AER_TAU_SW' ")
   # file.write('\n')
   file.close() # close atm namelist file
   #-------------------------------------------------------
   # Set some run-time stuff
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
