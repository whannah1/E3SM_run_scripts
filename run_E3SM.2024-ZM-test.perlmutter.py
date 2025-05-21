#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => master @ Dec 9

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True


# queue = 'debug';   stop_opt,stop_n,resub,walltime = 'ndays', 1,0,'0:20:00'
# queue = 'regular'; stop_opt,stop_n,resub,walltime = 'ndays', 32,0,'0:30:00'
# queue = 'regular'; stop_opt,stop_n,resub,walltime = 'ndays', 92,0,'1:00:00'
queue = 'regular'; stop_opt,stop_n,resub,walltime = 'ndays',365,0,'2:00:00'

compset='F2010'
grid = f'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 22


# case = '.'.join(['E3SM','2024-ZM-test-00',compset]) # control
case = '.'.join(['E3SM','2024-ZM-test-01',compset]) # disable gathering - all columns active - non-BFB

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
max_mpi_per_node,atm_nthrds  = 128,1
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --mach pm-cpu --compiler intel --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --case {case} --handle-preexisting-dirs u '
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --compset {compset} --res {grid} '
   cmd += f' --project {acct} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   #----------------------------------------------------------------------------
   cpp_opt = ''
   if 'ZM-test-01' in case: cpp_opt += f' -DZM_NO_GATHER'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #----------------------------------------------------------------------------
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build :
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
hst_fld  =  "'PS','TS','PSL'"
hst_fld += ",'PRECT','TMQ'"
hst_fld += ",'PRECC','PRECL','PRECZ'"
hst_fld += ",'LHFLX','SHFLX'"             # surface fluxes
hst_fld += ",'FSNT','FLNT','FLUT'"        # Net TOM heating rates
hst_fld += ",'FLNS','FSNS'"               # Surface rad for total column heating
hst_fld += ",'FSNTC','FLNTC'"             # clear sky heating rates for CRE
hst_fld += ",'TGCLDLWP','TGCLDIWP'"       # liq & ice water path
hst_fld += ",'CAPE_ZM','FREQZM'"

# # 3D ZM output
# 'ZMDT','ZMDQ'
# 'ZMMU','ZMMD'
# 'ZMMTT','ZMMTU','ZMMTV'
# 'CMFMCDZM','EVAPTZM'
#---------------------------------------------------------------------------------------------------
if submit :
   #----------------------------------------------------------------------------
   # # Namelist options
   # nfile = 'user_nl_eam'
   # file = open(nfile,'w') 
   # # Specify history output frequency and variables
   # file.write(' nhtfrq    = 0,-3 \n')
   # file.write(' mfilt     = 1,8 \n')
   # file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','HDEPTH','MAXQ0','UTGWSPEC','BUTGWSPEC'\n")
   # file.write(f" fincl2 = {hst_fld} \n")
   # file.write(f" fincl3 = {hst_fld} \n")
   # file.close()
   #----------------------------------------------------------------------------
   # Set some run-time stuff
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   #----------------------------------------------------------------------------
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
