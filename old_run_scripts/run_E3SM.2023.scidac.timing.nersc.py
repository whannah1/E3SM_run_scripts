#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit = False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True

debug_mode = False

stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'

grid = 'ne30pg2_EC30to60E2r2'
#-----------------------------------------------
# set case sepcific changes

compset,nlev,num_nodes = 'F20TR',72,22
# compset,nlev,num_nodes = 'F20TR',72,32
# compset,nlev,num_nodes = 'F20TR',72,44
# compset,nlev,num_nodes = 'F20TR',72,64

# compset,nlev,num_nodes = 'F20TR',80,22
# compset,nlev,num_nodes = 'F20TR',80,32
# compset,nlev,num_nodes = 'F20TR',80,44
# compset,nlev,num_nodes = 'F20TR',80,64
#-----------------------------------------------

case = '.'.join(['E3SM','TIMING-2023-scidac-00',grid,compset,f'NODES_{num_nodes}'])

case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'

init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'
# din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.nc'
if nlev==80: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')
atm_ntasks,atm_nthrds = num_nodes*128,1
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   # Check if directory already exists   
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --machine pm-cpu '
   cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   # when specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals(): 
      file=open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
   #-------------------------------------------------------
   # PE layout mods from Noel
   cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build :
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write('empty_htapes = .true. \n')
   file.close()
   #-------------------------------------------------------
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   file.write(f'hist_nhtfrq = -999999999 \n')
   file.write(f'hist_mfilt = 1 \n')
   file.write(f'hist_empty_htapes = .true. \n')
   file.close()
   #-------------------------------------------------------
   # Disable restart file write for timing
   run_cmd('./xmlchange --file env_run.xml --id REST_OPTION --val never')
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
