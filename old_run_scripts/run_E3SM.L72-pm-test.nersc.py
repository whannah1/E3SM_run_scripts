#!/usr/bin/env python
# This is for testing the vertical hybrid coordinate transition 
# between terrain follwing and pure pressure
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC3/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug 

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'

compset,ne,npg,grid = 'F2010',30,2,'ne30pg2_EC30to60E2r2'

# pm = 400; pgrad_correction = True    # fail
# pm = 300; pgrad_correction = True    # done
# pm = 200; pgrad_correction = True    # done
# pm = 100; pgrad_correction = True    # done
pm =  50; pgrad_correction = True    # 
# pm = 400; pgrad_correction = False   # fail
# pm = 300; pgrad_correction = False   # done
# pm = 200; pgrad_correction = False   # done
# pm = 100; pgrad_correction = False   # done
# pm =  50; pgrad_correction = False   # 

case='.'.join(['E3SM','HY-PM-TEST',compset,grid,f'L72_pm{pm}',f'pgrad_{int(pgrad_correction)}'])

case += '.00' # initial version - 2022/03/09

### debugging options
# case += '.debug-on'

init_scratch = '/global/cscratch1/sd/whannah/HICCUP/data'
init_file_atm = f'{init_scratch}/cami_mam3_Linoz_ne30np4_L72_pm{pm}_c20220309.nc'

init_path_lnd = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/PI_control_v2/archive/rest/0501-01-01-00000'
init_file_lnd = f'{init_path_lnd}/v2.LR.piControl.elm.r.0501-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

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
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,8 \n')
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
   file.write(          ",'DYN_OMEGA','DYN_PS'")
   file.write('\n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECL'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
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
   file.write(          ",'DYN_OMEGA:I','DYN_PS:I'")
   file.write('\n')
   
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   # file.write(" inithist = \'ENDOFRUN\' \n")

   if pgrad_correction:
      file.write(f' pgrad_correction=1 \n')
      # file.write(f' hv_ref_profiles=2 \n')
      # file.write(f' hv_theta_correction=1 \n')
      # file.write(f' theta_hydrostatic_mode=.false. \n')
      # file.write(f' tstep_type=9 \n')
      # file.write(f' hypervis_scalings=3.0 \n')
      # file.write(f' nu=3.4e-8 \n')

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{init_file_lnd}\' \n')
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
