#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return

#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
home = os.getenv('HOME')

acct = 'm3312'    # m3312 / m3305 / m1517 / e3sm_g
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'0:30:00'
#-------------------------------------------------------------------------------
compset,arch,ne,npg,num_nodes = 'F2010',    'GNUCPU', 4,2, 1

# compset,arch,ne,npg,num_nodes = 'F2010',    'GNUCPU', 30,2, 32
# compset,arch,ne,npg,num_nodes = 'F2010',    'GNUCPU', 30,2, 64

# compset,arch,ne,npg,num_nodes = 'F2010-MMF1','GNUGPU', 30,2, 32
# compset,arch,ne,npg,num_nodes = 'F2010-MMF1','GNUGPU', 30,2, 64

# compset,arch,ne,npg,num_nodes = 'F2010-MMF1','GNUGPU', 4,2, 1
#-------------------------------------------------------------------------------

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_oECv3'
if ne==4: grid = f'ne4pg2_oQU480'

# case_list =['E3SM','TIMING-2022-scidac-00',arch,grid,compset,f'NODES_{num_nodes}']

### test the impact of converting thread private variables to allocatables
src_dir=f'{home}/E3SM/E3SM_SRC1/';case_list=['E3SM','TIMING-2023-00',arch,grid,compset] # baseline
# src_dir=f'{home}/E3SM/E3SM_SRC0/';case_list=['E3SM','TIMING-2023-01',arch,grid,compset] # whannah/atm/remove-threadprivate-variables

if debug_mode: case_list.append('debug')
case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += f' -compset {compset} -res {grid} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   os.chdir(f'{case_dir}/{case}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   script_path = os.getenv('HOME')+'/E3SM/'+os.path.realpath(__file__).split('/')[-1]
   run_cmd(f'cp {script_path} {case_dir}/{case}/run_script.{timestamp}.py')
else:
   os.chdir(case_dir+case+'/')
#---------------------------------------------------------------------------------------------------
if config :
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
