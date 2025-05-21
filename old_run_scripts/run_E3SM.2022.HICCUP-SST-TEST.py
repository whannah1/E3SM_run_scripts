#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
# script for creating initial condition:
# ~/HICCUP/custom_scripts/2022-RCE-RRM.create_initial_condition.model_to_model.horizontal_only.py
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312' # m3312 / m3305 / m1517 / e3sm_g

case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # whannah/mmf/rce-rrm

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

stop_opt,stop_n,resub,walltime,queue = 'ndays',20,1,'0:30:00','debug' 

compset        = 'F2010'
arch           = 'CORI-INTEL'
num_nodes      = 32
grid = 'ne30pg2_oECv3'

case_list = ['E3SM','2022-HICCUP-SST-TEST-00',compset,grid] # control
# case_list = ['E3SM','2022-HICCUP-SST-TEST-01',compset,grid] # 

case='.'.join(case_list)

iyr,imn,idy = 2005,6,1
init_date = f'{iyr}-{imn:02d}-{idy:02d}'
init_file_atm = '/global/homes/w/whannah/HICCUP/data_scratch/HICCUP.atm_era5.2005-06-01.ne30np4.L72.nc'

if 'TEST-00' in case:init_file_sst='/global/homes/w/whannah/HICCUP/data_scratch/HICCUP.sst_noaa.2005-06-01.match_atmos.nc'
if 'TEST-01' in case:init_file_sst='/global/homes/w/whannah/HICCUP/data_scratch/HICCUP.sst_noaa.2005-06-01.use_all.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

max_mpi_per_node,atm_nthrds  = 64,1
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
task_per_node = max_mpi_per_node
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU': cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU': cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if 'CORI' in arch: cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
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
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   file.write(' nhtfrq = 0,-1,-24 \n')
   file.write(' mfilt  = 1,24,1 \n')
   file.write(" fincl2 = 'PS','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TAUX','TAUY'")               # surface stress
   file.write(          ",'UBOT','VBOT'")
   file.write(          ",'TBOT','QBOT'")
   file.write(          ",'U200','U850'")
   file.write(          ",'V200','V850'")
   file.write(          ",'Z100','Z500','Z700'")
   file.write(          ",'T500','T850','Q850'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')
   file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE / YEARLY
   file.close()
   #-------------------------------------------------------
   # SST
   os.system(f'./xmlchange --file env_run.xml  RUN_STARTDATE={init_date}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={init_file_sst}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={iyr}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={iyr}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={iyr+1}')
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------

