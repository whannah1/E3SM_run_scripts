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

acct = 'cli115'

case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # whannah/mmf/rce-rrm => updated 2023-02-22

# clean        = True
#newcase      = True
#config       = True
#build        = True
submit       = True
continue_run = True

debug_mode = False
 
# stop_opt,stop_n,resub,walltime,queue = 'nstep',60,0,'0:30:00','debug' 
# stop_opt,stop_n,resub,walltime,queue = 'nday',1,0,'4:00:00','regular' 

compset = 'FRCE-MMF1' ; arch = 'GNUGPU'
# compset = 'FRCE'      ; arch = 'GNUCPU'

# ne,npg =   8,2 ; num_nodes =  2
# ne,npg =  16,2 ; num_nodes =  4
# ne,npg =  32,2 ; num_nodes =  8
# ne,npg =  64,2 ; num_nodes = 16
ne,npg = 128,2 ; num_nodes = 32
# ne,npg = 256,2 ; num_nodes = 64

grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}' 


hiccup_scratch = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'

# case_list = ['E3SM','RCE-GRID-SENS-SPINUP-00',compset,f'ne{ne}pg{npg}']
# case_list = ['E3SM','RCE-GRID-SENS-SPINUP-01',compset,f'ne{ne}pg{npg}']
case_list = ['E3SM','RCE-GRID-SENS-SPINUP-01a',compset,f'ne{ne}pg{npg}']
# case_list = ['E3SM','RCE-GRID-SENS-SPINUP-02',compset,f'ne{ne}pg{npg}']


case='.'.join(case_list)

if 'MMF' in compset:
   run_scratch = '/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch'
   if 'SPINUP-00' in case: dtime,crm_dt=60,10; init_file_atm = f'{hiccup_scratch}/eam_i_rce_ne{ne}_L60_c20230223.nc'
   if 'SPINUP-01' in case: dtime = 5*60; init_time='0001-01-10-00000'; init_case='E3SM.RCE-GRID-SENS-SPINUP-00.FRCE-MMF1.ne128pg2'; 
   if 'SPINUP-01a'in case: dtime = 1*60; init_time='0001-01-06-00000'; init_case='E3SM.RCE-GRID-SENS-SPINUP-01.FRCE-MMF1.ne128pg2'
   if 'SPINUP-02' in case: dtime = 5*60; init_file_atm = f'{hiccup_scratch}/eam_i_rce_ne{ne}_L60_c20230309.nc' # new IC based on ne128 01 spinup
   if 'SPINUP-02' in case and ne==128: dtime=5*60; init_time='0001-01-02-00000'; init_case='E3SM.RCE-GRID-SENS-SPINUP-01a.FRCE-MMF1.ne128pg2'

   if 'SPINUP-00' in case: stop_opt,stop_n,resub,walltime,queue = 'nstep',12*60*60/dtime,4-1,'2:00','batch' 
   if 'SPINUP-01' in case: stop_opt,stop_n,resub,walltime,queue = 'nday',1,5-1,'1:00','batch' 
   if 'SPINUP-01a'in case: stop_opt,stop_n,resub,walltime,queue = 'nstep',60*60/dtime,24-1,'1:00','batch' 
   if 'SPINUP-02' in case: stop_opt,stop_n,resub,walltime,queue = 'nday',2,30-1,'1:00','batch' 
else:
   run_scratch = '/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch'
   if 'SPINUP-00' in case: dtime=12; init_file_atm = f'{hiccup_scratch}/eam_i_rce_ne{ne}_L72_c20230223.nc'
   if 'SPINUP-01' in case: dtime=60; init_time='0001-01-02-00000'; init_case='E3SM.RCE-GRID-SENS-SPINUP-00.FRCE.ne128pg2';
   if 'SPINUP-00' in case: stop_opt,stop_n,resub,walltime,queue = 'nstep',60*60/dtime,24-1,'1:00','batch' 
   if 'SPINUP-01' in case: stop_opt,stop_n,resub,walltime,queue = 'nstep',60*60/dtime,24-1,'1:00','batch' 


if 'init_case' in locals() and 'init_time' in locals():
   init_file_atm = f'{run_scratch}/{init_case}/run/{init_case}.eam.i.{init_time}.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')


max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach summit -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach summit -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   if 'crm_dt' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
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

   # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles

   file.write('\n')

   # file.write(" fincl3 =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(          ",'TOT_DU','TOT_DV'")          # total momentum tendencies
   # file.write(          ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
   # file.write(          ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
   # file.write(          ",'DUV','DVV'")                # 3D PBL tendencies
   # file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------

   # dtime_minute = dtime/60
   if 'dtime' in locals(): 
      if dtime==5*60:
         file.write(f'se_tstep            = {dtime/5} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 5 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')
      if dtime==5*60 and ne==128:
         file.write(f'se_tstep            = {dtime/10} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 5 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')
      if dtime==5*60 and ne==256:
         file.write(f'se_tstep            = {dtime/20} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 10 \n')
         file.write(f'hypervis_subcycle_q = 10 \n')

      if dtime==1*60:
         file.write(f'se_tstep            = {dtime/6} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 6 \n')
         file.write(f'hypervis_subcycle_q = 6 \n')
      else:
         file.write(f'se_tstep            = {dtime/4} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 4 \n')
         file.write(f'hypervis_subcycle_q = 4 \n')

   # file.write(f'use_crm_accel = .false. \n')
   # file.write(f'crm_accel_factor = 2 \n')

   if 'init_file_atm' in locals():
      file.write(f' ncdata = \'{init_file_atm}\'\n')

   file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE / YEARLY

   file.close()

   #-------------------------------------------------------
   # increase tolerance for domain grid check
   run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   #-------------------------------------------------------
   # Set the time step parameters
   if 'dtime' in locals(): 
      ncpl  = 86400 / dtime  # comment to disable setting time step
      run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   # other run-time stuff
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')

   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
