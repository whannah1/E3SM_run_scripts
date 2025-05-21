#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
acct = 'm3312'    # m3312 / m3305

case_dir =  os.getenv('HOME')+'/E3SM/Cases'
src_dir  =  os.getenv('HOME')+'/E3SM/E3SM_SRC3' # 

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 

#-------------------------------------------------------------------------------
# compset = 'FSCM-RCE'
compset = 'FSCM-RCE-MMF1'
#-------------------------------------------------------------------------------
arch = 'GNUGPU' # GNUCPU / GNUGPU / CORI / CORIGNU

case = '.'.join(['E3SM','SCM-TEST-00',arch,compset])

if queue=='debug'  : stop_opt,stop_n,walltime = 'nstep',10,'0:30:00'
if queue=='regular': stop_opt,stop_n,walltime = 'ndays',100,'3:00:00'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

#---------------------------------------------------------------------------------------------------
if newcase :
   cmd  = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res ne4_ne4 -pecount 1x1 '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu '
   if arch=='CORI'   : cmd += f' -mach cori-knl '
   if arch=='CORIGNU': cmd += f' -mach cori-knl -compiler gnu '
   run_cmd(cmd)

   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}')
if config : 
   #-------------------------------------------------------
   # Modify some parameters for CICE to make it SCM compatible
   # run_cmd('./xmlchange CICE_AUTO_DECOMP=FALSE,CICE_DECOMPTYPE=blkrobin')
   # run_cmd('./xmlchange CICE_BLCKX=1,CICE_BLCKY=1,CICE_MXBLCKS=1')
   # run_cmd('./xmlchange CICE_CONFIG_OPTS=\"-nodecomp -maxblocks 1 -nx 1 -ny 1\"')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   (ncpl,err) = sp.Popen('./xmlquery ATM_NCPL --value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w')

   file.write(' iopfile = \'/global/cfs/projectdirs/m3312/whannah/init_files/RCE_iopfile.SST_300K.nc\' \n')

   file.write( ' nhtfrq    = 0,1 \n')
   file.write(f' mfilt     = 1,{int(ncpl)*stop_n} \n')
   
   # file.write(' nhtfrq    = 0,-1,-24 \n')
   # file.write(' mfilt     = 1,24,1 \n')

   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")           # 3D cloud fields
   file.write(             ",'QRS','QRL'")
   file.write('\n')
   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   # run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
