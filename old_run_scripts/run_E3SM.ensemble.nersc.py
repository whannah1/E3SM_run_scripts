#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
import numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

# src_dir  = top_dir+'E3SM_BASE/'
src_dir  = top_dir+'E3SM_SRC4/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug 

ninst = 5

ne,npg,compset = 4,2,'FC5AV1C-L'   # FC5AV1C-L / F2010SC5-CMIP6 / F-EAMv1-AQP1 / F-MMF1

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = res+'_'+res

if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',20,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',20,0,'12:00:00'

# if 'E3SM_BASE' in src_dir: case = '.'.join(['E3SM',f'ENS_{ninst}','PREQX',grid,compset,'base'])
# if 'E3SM_SRC'  in src_dir: case = '.'.join(['E3SM',f'ENS_{ninst}','PREQX',grid,compset,'test'])

pertlim_max = 1e-1
case = '.'.join(['E3SM',f'ENS_{ninst}','PREQX',grid,compset,f'pertlim-max_{pertlim_max}'])
# case = '.'.join(['E3SM','ENS','THETA-L',grid,compset,'00'])

# case = case+'.debug-on'
# case = case+'.checks-on'

# pertlim_max = 1e-13
pert_val = np.linspace(pertlim_max/1e1,pertlim_max,ninst)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'')
print('  Perturbation values:')
for i in range(ninst): print(f'    {pert_val[i]}')
print()

# dtime = 20*60
if 'dtime' in locals(): ncpl = 86400/dtime
atm_ntasks = 96*ninst
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
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
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}'
   run_cmd(cmd)
   #-------------------------------------------------------
   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # Set up multi-instance
   run_cmd(f'./xmlchange -file env_mach_pes.xml NINST_ATM={ninst}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NINST_LND={ninst}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NINST_ICE={ninst}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NINST_OCN={ninst}')
   #-------------------------------------------------------
   # Adjust ATM tasks
   if 'atm_ntasks' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_ATM={atm_ntasks}')
   #-------------------------------------------------------
   # Switch the dycore
   if '.THETA-L.' in case: run_cmd('./xmlchange CAM_TARGET=theta-l ' )
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
   # Namelist options
   for i in range(ninst):
      nfile = f'user_nl_cam_{(i+1):04}'
      file = open(nfile,'w') 
      # pert_val = float(i+1)/float(ninst)*10
      # file.write(f' pertlim   = {pert_val}e-14 \n')
      file.write(f' pertlim   = {pert_val[i]} \n')
      file.write(' nhtfrq    = 0,-3 \n')
      file.write(' mfilt     = 1,8 \n')
      file.write(" fincl2    = 'PS','TS','PRECT','TMQ','LHFLX','SHFLX'")
      file.write(             ",'FSNT','FLNT','FLNS','FSNS','FSNTC','FLNTC'")
      file.write(             ",'TGCLDLWP','TGCLDIWP'")    
      file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
      file.write(             ",'OMEGA850','OMEGA500'")
      file.write(             ",'Z100','Z500','Z700'")
      file.write(             ",'T500','T850','Q850'")
      file.write(             ",'U200','U850','V200','V850'")
      file.write('\n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
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
   run_cmd('./case.submit')

# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
