#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
ne,npg = 0,0
newcase,config,build,clean,submit,continue_run,copy_p3_data = False,False,False,False,False,False, False

acct = 'm3312'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'/E3SM_SRC0' # branch => ECPP_development (liranpeng)

clean        = True
# newcase      = True
# config       = True
build        = True
# submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # batch / debug 

stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'

compset='F2010-MMF2-ECPP'
arch = 'GNUCPU' # GNUGPU / GNUCPU

# ne=30; grid=f'ne30pg2_oECv3';  num_nodes=64
ne= 4; grid='ne4pg2_oQU480';  num_nodes=1

crm_nx = 16

case_list=['E3SM','2024-ECPP-DEV',arch,grid,compset,f'NX_{crm_nx}']

if debug_mode: case_list.append('debug')
case='.'.join(case_list)

# print(case); exit()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_nx_rad 1 \" ')
   #-------------------------------------------------------
   # cpp_opt = ''
   # cpp_opt += f' -D??'
   # if cpp_opt != '' :
   #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
   #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
   #    run_cmd(cmd)
   #-------------------------------------------------------
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # ATM namelist
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-1,-1 \n')
   file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECSC'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TBOT','QBOT'")
   # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write('\n')

   file.close()
   #-------------------------------------------------------
   # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
