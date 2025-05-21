#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = f'{top_dir}/Cases/'
src_dir  = f'{top_dir}/E3SM_SRC1/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'

compset = 'F2010-MMF1'

ne,npg = 4,2 ; grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'

# MMF options
use_vt        = True # variance transport (disabled by default)
use_mf        = True # 2D scalar momentum transport (disabled by default)
crm_nx,crm_ny = 64,1
crm_dx        = 2000
rad_nx        = 4 

case_list = ['E3SM','TEST-00',grid,compset]

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)
# if ne==120: dtime = 5*60
# if 'dtime' in locals(): ncpl = 86400/dtime

#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid}'
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   
   if 'MMF' in compset:
      if use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Run case setup
   if clean: run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # atmos namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #-------------------------------------------------------
   # atmos history output
   #-------------------------------------------------------
   file.write(' nhtfrq    = 0,-1,-24 \n')
   file.write(' mfilt     = 1,24,1 \n')
   ### add some monthly variables to the default
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   ### hourly 2D variables
   file.write(" fincl2    = 'PS','TS','PSL'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'PRECC','PRECSC'")
   file.write(             ",'PRECL','PRECSL'")
   file.write(             ",'LHFLX','SHFLX'")                    # surface fluxes
   file.write(             ",'FSNT','FLNT'")                      # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                      # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")                    # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")                      # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")              # cloud water path
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT'")
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   file.write('\n')
   ### daily 3D variables
   file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write('\n')

   file.close() # close atm namelist file

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
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
