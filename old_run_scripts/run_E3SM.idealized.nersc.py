#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC1/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug 

ne,npg = 4,2

compset = 'FADIAB'
# compset = 'FIDEAL'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'   # f'{res}_r05_oECv3' / f'{res}_{res}'
grid = f'{res}_{res}'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',16,1,'6:00:00'

### dev runs for idealized physics
case = '.'.join(['E3SM','DEV',grid,compset])


# case = case+'.debug-on'
# case = case+'.checks-on'


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)

if 'dtime' in locals(): ncpl = 86400/dtime

# atm_ntasks = 5400
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
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   if '.gnu.' in case : cmd = cmd + ' --compiler gnu '
   if '.pgi.' in case : cmd = cmd + ' --compiler pgi '
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
   # if changing vertical levels make sure to update ncdata here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''

   if 'debug-on' in case and 'MMFXX' in compset : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads
   if 'atm_ntasks' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   # if stop_opt=='nstep':
   #    file.write(' nhtfrq    = 0,1 \n')
   #    file.write(' mfilt     = 1,72 \n')
   # else:
   file.write(' nhtfrq    = 0,-6 \n')
   file.write(' mfilt     = 1,4 \n')

   file.write('\n')
   file.write(" fincl2    = 'PS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT'")
   # file.write(             ",'TBOT','QBOT'")
   # file.write(             ",'OMEGA850','OMEGA500'")
   # file.write(             ",'T500','T850','Q850'")
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRS','QRL'")
   file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')   

   # close atm namelist file
   file.close()

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
