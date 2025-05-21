#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
# import xarray as xr
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC3/'

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug 

compset,ne,npg,grid = 'F2010',30,2,'ne30pg2_EC30to60E2r2'
# compset,ne,npg,grid = 'F-MMFXX',30,2,'ne30pg2_EC30to60E2r2' ; src_dir=top_dir+'E3SM_SRC0/'

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'nstep',3, 0,'0:05:00'
# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73*5,9,'5:00:00'

if queue=='regular' and 'MMF' in compset: stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00:00'


case='.'.join(['E3SM','L72-NEW-TEST-ZM',compset,grid,f'L72-v0','00']) # quick test to print max MSE level in ZM


# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v0','00']) # control
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v1','00']) # initial version - 2022/03/15
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v2','00']) # initial version - 2022/03/15
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v3','00']) # initial version - 2022/03/15

# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v1-R2','00'])  # sensitivity test - 2022/07/25
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v1-R5','00'])  # sensitivity test - 2022/07/25
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v1-R10','00']) # sensitivity test - 2022/07/25

### hi-freq output
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v0','HF-OUTPUT','00']) # control
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v1','HF-OUTPUT','00']) # initial version - 2022/03/15
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v2','HF-OUTPUT','00']) # initial version - 2022/03/15
# case='.'.join(['E3SM','L72-NEW-TEST',compset,grid,f'L72-v3','HF-OUTPUT','00']) # initial version - 2022/03/15

### debugging options
# case += '.debug-on'

cfs_inputdata = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme'
init_scratch = '/global/cscratch1/sd/whannah/HICCUP/data'
if 'L72-v0' in case: init_file_atm = f'{cfs_inputdata}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.nc'
# if 'L72-v0' in case: init_file_atm = f'{init_scratch}/cami_mam3_Linoz_ne30np4_L72_c160214.nc'
# if 'L72-v1' in case: init_file_atm = f'{init_scratch}/cami_mam3_Linoz_ne30np4_L72_new_v1_c20220311.nc'

if 'L72-v1.' in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v1_c20220315.nc'
if 'L72-v2.' in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v2_c20220315.nc'
if 'L72-v3.' in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v3_c20220315.nc'

if 'L72-v1-R2.'  in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v1_R2_c20220315.nc'
if 'L72-v1-R5.'  in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v1_R5_c20220315.nc'
if 'L72-v1-R10.' in case: init_file_atm = f'{init_scratch}/20180716.DECKv1b_A3.ne30_oEC.edison.cam.i.2010-01-01-00000.L72v1_R10_c20220315.nc'

# init_path_lnd = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/PI_control_v2/archive/rest/0501-01-01-00000'
# init_file_lnd = f'{init_path_lnd}/v2.LR.piControl.elm.r.0501-01-01-00000.nc'

# init_path_lnd = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/v2.LR.amip_0101/init'
# init_file_lnd = f'{init_path_lnd}/v2.LR.historical_0101.elm.r.1870-01-01-00000.nc'

init_path_lnd = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/'
init_case_lnd = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.2010-01-01'
init_file_lnd = f'{init_path_lnd}/{init_case_lnd}.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(tcolor.RED+"\nThis case already exists!\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid} '
   # cmd += ' --pecount 5400x1'
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # if 'MMF' in case:
   #    run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 72 -crm_nz 58 \" ')
   #-------------------------------------------------------
   # make sure nuber of levels is correct
   # ds_init = xr.open_dataset(init_file_atm)
   # nlev = len(ds_init['lev'].values)
   # if nlev!=72:
   #    run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {nlev} \" ')

   if 'L72-v1-R10.' in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 74 \" ')

   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   #-------------------------------------------------------
   # Build the case
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if 'HF-OUTPUT' in case:
      file.write(' nhtfrq    = 0,1 \n')
      file.write(' mfilt     = 1,48 \n')
      file.write('\n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'PRECC','PRECL'")
      file.write(          ",'LHFLX','SHFLX','QFLX'")      # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
      file.write(          ",'U10'")
      file.write(          ",'TBOT','QBOT','UBOT','VBOT'")
      file.write(          ",'T900','Q900','U900','V900'")
      file.write(          ",'T850','Q850','U850','V850'")
      file.write(          ",'TREFHT','QREFHT','RHREFHT'")
      file.write(          ",'ASDIR','ASDIF','ALDIR','ALDIF'") # albedos
      file.write(          ",'PBLH'")
      file.write(          ",'UTGWORO','VTGWORO','TTGWORO'")
      file.write(          ",'TAUGWX','TAUGWY','SGH','TTGW'")
      file.write(          ",'FRONTGF','FRONTGFA'")
      # file.write(          ",'','','',''")
      # 3D fields
      file.write(          ",'T','Q','Z3','RELHUM'")
      file.write(          ",'U','V','OMEGA'")
      file.write(          ",'CLOUD','CLDLIQ','CLDICE'")
      file.write(          ",'QRL','QRS'")
      file.write(          ",'PTTEND','PTEQ'")
      file.write(          ",'DTENDTQ','DTENDTH'")
      file.write('\n')
   else:
      file.write(' nhtfrq    = 0,-3 \n')
      file.write(' mfilt     = 1,8 \n')
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
      file.write(          ",'DYN_OMEGA','DYN_PS'")
      file.write('\n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'PRECC','PRECL'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'TAUX','TAUY'")               # surface stress
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
      file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
      # variables for tracking stuff like hurricanes
      file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(          ",'Z300:I','Z500:I'")
      file.write(          ",'OMEGA850:I','OMEGA500:I'")
      file.write(          ",'U200:I','V200:I'")
      # dynamics grid output for assessing topography noise
      # file.write(          ",'DYN_OMEGA:I','DYN_PS:I'")
      file.write('\n')
   
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   # file.write(" inithist = \'ENDOFRUN\' \n")

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'init_file_lnd' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{init_file_lnd}\' \n')
      # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      file.write(f' fsurdat = \'/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2000_c210402.nc\' \n')
   # file.write(f' fsurdat = \'/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2010_c210402.nc\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
