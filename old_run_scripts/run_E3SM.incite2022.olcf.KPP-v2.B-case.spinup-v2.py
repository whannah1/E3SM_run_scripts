#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime, shutil
import xml.etree.ElementTree as ET
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

input_data_root = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/' # branch => whannah/mmf/KPP

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'batch' # batch / debug

stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'
# stop_opt,stop_n,resub,walltime = 'nstep',10,0,'0:30'

ne,npg = 120,2; grid = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'

diff_ocn_nodes = True

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
compset,arch,num_nodes = 'WCYCL1950-MMF1','GNUGPU',1024
# compset,arch,num_nodes = 'WCYCL1950-MMF1','GNUGPU',512
# compset,arch,num_nodes = 'WCYCL1950-MMF1','GNUCPU',256
# compset,arch,num_nodes = 'WCYCL1950',     'GNUCPU', 512   # non-MMF companion case

### specify tasks instead of nodes
# compset,arch,num_tasks = 'WCYCL1950-MMF1','GNUGPU', 1024
# compset,arch,num_tasks = 'WCYCL1950-MMF1','GNUCPU', 1024
# compset,arch,num_tasks = 'WCYCL1950',     'GNUCPU', 512   # non-MMF companion case

use_L60 = False
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

case_list = ['E3SM','2022-KPP-B-v2-SPINUP',arch.replace('GNU',''),f'ne{ne}pg{npg}',compset]

if 'num_tasks' in locals(): case_list.append(f'NT_{num_tasks}')
if 'num_nodes' in locals(): case_list.append(f'NN_{num_nodes}')

if 'MMF' not in compset and use_L60: case_list.append(f'L60')

case_list.append('20221121') # add a time stamp
# case_list.append('20221104') # add a time stamp

# case_list.append('20221104a') # add a time stamp
# case_list.append('20221104b') # add a time stamp

case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# land initial condition and surface data files
if 'r0125' in grid:
   lnd_data_path = f'{input_data_root}/lnd/clm2/surfdata_map'
   lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
   if '20221104a' in case: lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
   if '20221104b' in case: lnd_data_file = 'surfdata_0.125x0.125_simyr2000_c190730.nc'
   # lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   # lnd_init_file = ''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

if 'num_nodes' in locals():
   task_per_node = max_mpi_per_node
   atm_ntasks = task_per_node*num_nodes

   if arch=='GNUGPU':
      # if num_nodes> 512:ocn_ntasks,ice_ntasks = 1024,1024; rootpe_ice,rootpe_lnd=0,ice_ntasks
      if num_nodes> 512:ocn_ntasks,ice_ntasks = 4096,4096; rootpe_ice,rootpe_lnd=0,ice_ntasks
      if num_nodes==512:ocn_ntasks,ice_ntasks = 1024,1024; rootpe_ice,rootpe_lnd=0,ice_ntasks
      if num_nodes==256:ocn_ntasks,ice_ntasks = 1024,1024; rootpe_ice,rootpe_lnd=0,ice_ntasks
      if num_nodes==128:ocn_ntasks,ice_ntasks =  512, 640; rootpe_ice,rootpe_lnd=0,ice_ntasks
   if arch=='GNUCPU':
      if num_nodes==512:ocn_ntasks,ice_ntasks = 4096,8192
      if num_nodes==256:ocn_ntasks,ice_ntasks = 4096,4096; lnd_ntasks=4096; rootpe_ice=0
      if num_nodes==128:ocn_ntasks,ice_ntasks = 2048,4096

   if 'cpl_ntasks' not in locals(): cpl_ntasks = atm_ntasks
   if 'rof_ntasks' not in locals(): rof_ntasks = atm_ntasks

   if 'lnd_ntasks' not in locals(): lnd_ntasks = atm_ntasks-ice_ntasks
   if lnd_ntasks<=0: lnd_ntasks = atm_ntasks

   # always default to ice on different root PE so it runs in parallel with land
   if 'rootpe_ice' not in locals(): rootpe_ice = lnd_ntasks

if 'num_tasks' in locals():
   task_per_node = max_mpi_per_node
   atm_ntasks, lnd_ntasks = num_tasks, num_tasks
   ocn_ntasks, ice_ntasks = num_tasks, num_tasks
   cpl_ntasks, rof_ntasks = num_tasks, num_tasks
   rootpe_ice = 0

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if use_L60: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 60 \" ')
   #-------------------------------------------------------
   # Set tasks
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL={cpl_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_LND={lnd_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_OCN={ocn_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ICE={ice_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ROF={rof_ntasks}')

   if diff_ocn_nodes: rootpe_ocn = atm_ntasks
   if 'rootpe_ocn' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_OCN={rootpe_ocn}')
   if 'rootpe_ice' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_ICE={rootpe_ice}')
   if 'rootpe_lnd' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_LND={rootpe_lnd}')
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
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
   if use_L60: 
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      file.write(f' ncdata = \'{input_data_root}/atm/cam/inic/homme/eam_i_mam3_Linoz_ne120np4_L60_c20210917.nc\' \n') 
      file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'lnd_init_file' in locals() or 'lnd_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'lnd_data_file' in locals(): file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      if 'lnd_init_file' in locals(): file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   file = open('user_nl_mpassi','w')
   file.write(f'config_reuse_halo_exch = true\n')
   file.write(f'config_am_regionalstatistics_enable = false\n')
   file.write(f'config_am_timeseriesstatsdaily_enable = false\n')
   file.close()
   #-------------------------------------------------------
   file = open('user_nl_mpaso','w')
   file.write(f'config_am_timeseriesstatsdaily_write_on_startup = .true.\n')
   file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
