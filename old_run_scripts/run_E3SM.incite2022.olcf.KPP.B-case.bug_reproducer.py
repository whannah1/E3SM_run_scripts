#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime, shutil
import xml.etree.ElementTree as ET
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/' # branch => whannah/mmf/KPP-dev

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'nstep',2,0,'0:30'

### common settings
ne,npg = 30,2; grid = f'ne{ne}pg{npg}_oECv3'

compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUGPU',16, True # for debugging

diff_ocn_nodes = True

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# specify case name based on configuration
case_list = ['E3SM','2022-KPP-B-BUG',arch,f'ne{ne}pg{npg}',compset]
case_list.append(f'NN_{num_nodes}')

if diff_ocn_nodes: case_list.append(f'DIFF_OCN_NODES')

NTHRDS_OCN,NTHRDS_ICE = 1,1
# NTHRDS_OCN,NTHRDS_ICE = 1,3
# NTHRDS_OCN,NTHRDS_ICE = 1,5

case_list.append(f'NTHRDS_OCN_{NTHRDS_OCN}')
case_list.append(f'NTHRDS_ICE_{NTHRDS_ICE}')

if debug_mode: case_list.append('debug')

case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')


max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

rof_ntasks = int(atm_ntasks/2)

ocn_ntasks,ice_ntasks = 48,48
cpl_ntasks,rof_ntasks = atm_ntasks,atm_ntasks

lnd_ntasks = atm_ntasks-ice_ntasks

total_ntasks, total_nthrds = atm_ntasks, atm_nthrds
if diff_ocn_nodes: total_ntasks = total_ntasks + ocn_ntasks

#---------------------------------------------------------------------------------------------------
if newcase :
   #-------------------------------------------------------
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
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
   #-------------------------------------------------------
   # Set tasks for each component
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL={cpl_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_LND={lnd_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_OCN={ocn_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ICE={ice_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ROF={rof_ntasks}')

   # always put ice on different root PE so it runs in parallel with land
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_ICE={lnd_ntasks}')

   run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ICE={NTHRDS_ICE}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_OCN={NTHRDS_ICE}')

   #-------------------------------------------------------
   # set root PE for putting ocean/ice on separate nodes
   if diff_ocn_nodes:
      run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_OCN={atm_ntasks}')
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   #-------------------------------------------------------
   # check if debug mode is already set before setting 
   # to avoid error when rebuilding a debug case
   if debug_mode: 
      (debug_flag, err) = sp.Popen('./xmlquery DEBUG    --value', \
                                   stdout=sp.PIPE, shell=True, \
                                   universal_newlines=True).communicate()
      if debug_flag=='FALSE': 
         run_cmd('./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DYAKL_DEBUG \'  \" ')
         run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   dtime = 20*60; ncpl = int( 86400 / dtime )
   run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   file = open('user_nl_mpaso','w')
   nminutes = int(dtime/60)
   file.write(f' config_dt = \'00:{nminutes}:00\' \n')
   file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
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
