#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
# case_dir = os.getenv('HOME')+'/E3SM/Cases/'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # branch => whannah/mmf/pam-updates
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => jgfouca/scream_downstream_2024_10_09

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = True

queue = 'regular'  # regular / debug 
arch = 'GNUCPU' # GNUCPU / GNUGPU 

stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:20:00'
# stop_opt,stop_n,resub,walltime = 'ndays',15,6-1,'4:00:00'

compset='F2010-MMF2'

# ne,npg,grid = 30,2,'ne30pg2_oECv3'; num_nodes = 64
ne,npg,grid = 4,2,'ne4pg2_oQU480'; num_nodes = 1
if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';   num_nodes = 1
   
case_list = ['E3SM','2024-PAM-CHK-00',arch,grid,compset]

if debug_mode: case_list.append('debug')
case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# case_root = f'{case_dir}/{case}'
if 'CPU' in arch: case_root = os.getenv('SCRATCH')+f'/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = os.getenv('SCRATCH')+f'/e3sm_scratch/pm-gpu/{case}'
#---------------------------------------------------------------------------------------------------
if 'FSCM' in compset: 
   max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
else:
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node =  32
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase:
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case_root}'
   cmd += f' --compset {compset}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   # cmd += f' --walltime {walltime} '
   cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config:
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   # Run case setup
   if clean: run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build: 
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
   file.write(' nhtfrq    = 0,-1,-24 \n')
   file.write(' mfilt     = 1,24,1 \n')
   ### add some monthly variables to the default
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   ### hourly 2D variables
   file.write(" fincl2    = 'PS','TS','PSL'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'PRECC','PRECSC'")
   file.write(             ",'PRECL','PRECSL'")
   file.write(             ",'LHFLX','SHFLX'")                    # surface fluxes
   file.write(             ",'FSNT','FLNT'")                      # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                      # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")                    # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")                      # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")              # cloud water path
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT'")
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   file.write('\n')
   ### daily 3D variables
   # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
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
