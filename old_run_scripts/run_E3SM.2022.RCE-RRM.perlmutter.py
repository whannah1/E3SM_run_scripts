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
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # master as of Dec 8, 2022
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # whannah/mmf/test-scaled-dx

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False
 
ne,npg = 0,2
rad_nx = 4

crm_nx,crm_ny = 64,1; num_nodes,stop_opt,stop_n,resub,walltime,queue = 64,'nday',1,0,'1:00:00','regular' 

grid,grid_name = 'ne0_cubeface_grad_ne30x3pg2','ne30x3pg2'

compset = 'FRCE-MMF1' ; arch = 'GNUGPU'
# compset = 'FRCE'      ; arch = 'GNUCPU'


use_dx_scaling, dx_scale, crm_dx, crm_dt = False,     0,2000,5
# use_dx_scaling, dx_scale, crm_dx, crm_dt = False,     0, 200, 2
# use_dx_scaling, dx_scale, crm_dx, crm_dt = True,'12e-3', 200, 2

# crm_dx,crm_dt = 2e3,10; case='.'.join(['E3SM','RCE-RRM-TEST',compset,f'CRMDX_{crm_dx}','00']) # control
# crm_dx,crm_dt = 2e2,2;  case='.'.join(['E3SM','RCE-RRM-TEST',compset,f'CRMDX_{crm_dx}','00']) # control
# crm_dx,crm_dt = 2e2,2;  case='.'.join(['E3SM','RCE-RRM-TEST',compset,f'DXSCL_{crm_dx}','00']) # scale crm_dx by DXSCL

case_list = ['E3SM','RCE-RRM-TEST',compset]
# case_list = ['E3SM','RCE-RRM-TEST',compset,grid_name,f'GCMDT_{gcm_dt}']

if 'MMF' in compset:
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   if use_dx_scaling: 
      case_list.append(f'DXSCL_{dx_scale}')
   else:
      case_list.append(f'CRMDX_{crm_dx}')   
      

case_list.append('00') # initial tests

case='.'.join(case_list)

### specify atmos initial condition file
# hiccup_scratch = '/global/cfs/projectdirs/m3312/whannah/HICCUP'
# if compset=='FRCE-MMF1': init_file_atm = f'{hiccup_scratch}/eam_i_rce_RRM-cubeface-grad-ne30x3_L60_c20221208.nc'
# if compset=='FRCE'     : init_file_atm = f'{hiccup_scratch}/eam_i_rce_RRM-cubeface-grad-ne30x3_L72_c20221208.nc'
if compset=='FRCE-MMF1': init_file_atm = f'/global/cfs/projectdirs/m3312/whannah/HICCUP/eam_i_rce_RRM-cubeface-grad-ne30x3_L60_c20221208.nc'
if compset=='FRCE'     : init_file_atm = f'/global/cfs/projectdirs/m3312/whannah/HICCUP/eam_i_rce_RRM-cubeface-grad-ne30x3_L72_c20221208.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# dtime = gcm_dt*60
dtime = 5*60

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
task_per_node = max_mpi_per_node
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
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      if 'rad_nx' in locals():
         rad_ny = rad_nx if crm_ny>1 else 1
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')

      if use_dx_scaling: 
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx_scale {dx_scale} \" ')
   #-------------------------------------------------------
   # 64_data format is needed for large numbers of columns (GCM or CRM)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
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

   # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

   if 'dtime' in locals():
      if dtime == 5*60:
         file.write(f'se_tstep            = 60 \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 5 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')
      if dtime == 1*60:
         file.write(f'se_tstep            = 10 \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'dt_tracer_factor    = 6 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'hypervis_subcycle_q = 6 \n')


   if 'init_file_atm' in locals():
      file.write(f' ncdata = \'{init_file_atm}\'\n')

   file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')

   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   # if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
   # if 'CPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
