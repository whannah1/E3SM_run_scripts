#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm2637'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = f'{top_dir}/Cases/'
src_dir  = f'{top_dir}/E3SM_SRC1/'

# clean        = True   # clean a previous build
newcase      = True   # create a new case
config       = True   # configure the case
build        = True   # build the model
submit       = True   # submit a job
# continue_run = True   # continue from a previous run

debug_mode = False

queue = 'debug'  # regular / debug 

walltime = '1:00:00' # wall clock limit for each submission
stop_opt = 'ndays'   # ndays / nsteps
stop_n   = 10        # number of days/steps to run
resub    = 0         # how many times to resubmit

compset = 'F2010'
grid    = 'ne4pg2_oQU480'

case='.'.join(['E3SM','TEST-00',grid,compset])

if debug_mode: case += '.debug'

#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid}'
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
os.chdir(case_dir+case+'/')
if config : run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
if submit : 
   #-------------------------------------------------------
   # atmos namelist options and history output
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,8 \n')
   # add some monthly variables to the default
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   # 3-hourly 2D variables
   file.write(" fincl2    = 'PS','TS','PSL'")                      # sfc temperature and pressure
   file.write(             ",'PRECT','TMQ'")                       # precip and column water vapor
   file.write(             ",'LHFLX','SHFLX'")                     # surface fluxes
   file.write(             ",'FSNT','FLNT'")                       # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                       # Surface rad for total column heating
   file.write(             ",'TGCLDLWP','TGCLDIWP'")               # cloud water path
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")                   # geopotential height
   file.write(             ",'OMEGA850:I','OMEGA500:I'")           # vertical velocity
   file.write('\n')
   file.close() # close atm namelist file
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
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
