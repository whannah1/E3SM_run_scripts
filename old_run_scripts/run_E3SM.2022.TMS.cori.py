#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Note: initialization data was transferred from LCRC:
# /lcrc/group/e3sm/ac.forsyth2/E3SMv2/v2.LR.amip_0101/init
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC3/' # branch => maint-2.0

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

queue = 'regular'  # regular / debug 

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73*2,5*10/2-1,'3:00:00' # 10 years
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73*2,5*1/2-1,'3:00:00' # 1 year
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73,0,'2:00:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',365,4,'6:00:00'

compset = 'F20TR'
ne,npg = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2'


case='.'.join(['E3SM','TMS-00',compset,grid,'tms-on']) # initial version - 2022/03/09
# case='.'.join(['E3SM','TMS-00',compset,grid,'tms-off']) # parallel test without TMS - 2022/05/25

### debugging options
# case += '.debug-on'

ic_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/v2.LR.amip_0101/init'
scratch = '/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/'

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
   cmd += f' -compset {compset} -res {grid} --pecount 1920x1'
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   # Build with COSP
   run_cmd("./xmlchange --id CAM_CONFIG_OPTS --append --val='-cosp' ")
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
   #-------------------------------------------------------
   # Set up a hybrid run
   run_cmd('./xmlchange RUN_TYPE=hybrid')
   run_cmd('./xmlchange GET_REFCASE=FALSE')
   run_cmd(f'./xmlchange RUN_STARTDATE=1870-01-01,START_TOD=0')
   run_cmd('./xmlchange BUDGETS=TRUE') # Coupler budgets (always on)
   
   run_cmd('./xmlchange RUN_REFCASE=\'v2.LR.historical_0101\'')
   run_cmd('./xmlchange RUN_REFDATE=1870-01-01')
   #-------------------------------------------------------
   # copy the initialization data files
   run_cmd(f'cp {ic_path}/* {scratch}/{case}/run/')
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
   file.write(' nhtfrq = 0,-24,-6,-6,-3,-24,0 \n')
   file.write(' mfilt  = 1,30,120,120,240,30,1\n')
   file.write(" avgflag_pertape = 'A','A','I','A','A','A','I' \n")
   file.write(" fexcl1 = 'CFAD_SR532_CAL', 'LINOZ_DO3', 'LINOZ_DO3_PSC', 'LINOZ_O3CLIM', 'LINOZ_O3COL', 'LINOZ_SSO3', 'hstobie_linoz' \n")
   file.write(" fincl1 = 'extinct_sw_inp','extinct_lw_bnd7','extinct_lw_inp','CLD_CAL', 'TREFMNAV', 'TREFMXAV' \n")
   file.write(" fincl2 = 'FLUT','PRECT','U200','V200','U850','V850','Z500','OMEGA500','UBOT','VBOT','TREFHT','TREFHTMN:M','TREFHTMX:X','QREFHT','TS','PS','TMQ','TUQ','TVQ','TOZ', 'FLDS', 'FLNS', 'FSDS', 'FSNS', 'SHFLX', 'LHFLX', 'TGCLDCWP', 'TGCLDIWP', 'TGCLDLWP', 'CLDTOT', 'T250', 'T200', 'T150', 'T100', 'T050', 'T025', 'T010', 'T005', 'T002', 'T001', 'TTOP', 'U250', 'U150', 'U100', 'U050', 'U025', 'U010', 'U005', 'U002', 'U001', 'UTOP', 'FSNT', 'FLNT' \n")
   file.write(" fincl3 = 'PSL','T200','T500','U850','V850','UBOT','VBOT','TREFHT', 'Z700', 'TBOT:M' \n")
   file.write(" fincl4 = 'FLUT','U200','U850','PRECT','OMEGA500' \n")
   file.write(" fincl5 = 'PRECT','PRECC','TUQ','TVQ','QFLX','SHFLX','U90M','V90M' \n")
   file.write(" fincl6 = 'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANTAU_ISCCP','MEANPTOP_ISCCP','MEANTB_ISCCP','CLDTOT_CAL','CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN','CLDHGH_CAL','CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN','CLDMED_CAL','CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN','CLDLOW_CAL','CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN' \n")
   file.write(" fincl7 = 'O3', 'PS', 'TROP_P' \n")

   # Enable turbulent mountain stress
   if 'tms-off' in case: file.write(' do_tms = .false. \n')
   if 'tms-on'  in case: file.write(' do_tms = .true. \n')

   file.close()

   #-------------------------------------------------------
   # Land namelist
   #-------------------------------------------------------
   nfile = 'user_nl_elm'
   file = open(nfile,'w') 
   file.write(" hist_dov2xy = .true.,.true. \n")
   file.write(" hist_fincl2 = 'H2OSNO', 'FSNO', 'QRUNOFF', 'QSNOMELT', 'FSNO_EFF', 'SNORDSL', 'SNOW', 'FSDS', 'FSR', 'FLDS', 'FIRE', 'FIRA' \n")
   file.write(" hist_mfilt = 1,365 \n")
   file.write(" hist_nhtfrq = 0,-24 \n")
   file.write(" hist_avgflag_pertape = 'A','A' \n")
   file.write(" check_finidat_fsurdat_consistency = .false. \n")
   file.close()
   #-------------------------------------------------------
   # River namelist
   #-------------------------------------------------------
   nfile = 'user_nl_mosart'
   file = open(nfile,'w') 
   file.write(" rtmhist_fincl2 = 'RIVER_DISCHARGE_OVER_LAND_LIQ' \n")
   file.write(" rtmhist_mfilt = 1,365 \n")
   file.write(" rtmhist_ndens = 2 \n")
   file.write(" rtmhist_nhtfrq = 0,-24 \n")
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   
   # Coupler history
   run_cmd(f'./xmlchange HIST_OPTION=nyears,HIST_N=5')

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
