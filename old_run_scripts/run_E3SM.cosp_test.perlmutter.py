#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => brhillman/atm/refactor-cosp-interface

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular' # regular / debug

### run duration
# stop_opt,stop_n,resub,walltime = 'nstep',10,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'nday',5,0,'2:00:00'

### common settings
ne,npg = 30,2; grid   = f'ne{ne}pg{npg}_oECv3'

### MMF options
crm_nx,crm_ny = 64,1
rad_nx        = 4 
use_vt        = True
use_mf        = True

use_cosp      = True

#-------------------------------------------------------------------------------
# specific case names and settings
#-------------------------------------------------------------------------------

# compset,arch,num_nodes = 'F2010','CORI', 64 ; #walltime = '4:00:00'
compset,arch,num_nodes = 'F2010-MMF1','CORI', 64 ; #walltime = '4:00:00'

# compset,arch,num_nodes = 'F2010-MMF1','GNUGPU', 64

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

### specify case name based on configuration
# case_list = ['E3SM','2022-COSP-TEST',arch,grid,compset]
case_list = ['E3SM','2022-COSP-TEST',arch,grid,compset,'CFT_1e-5']

# case_list = ['E3SM','2022-COSP-TEST-00',arch,f'NN_{num_nodes}',grid,compset]

if use_cosp: 
   case_list.append('COSP-ON')
else:
   case_list.append('COSP-OFF')
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

# dtime = 20*60   # GCM physics time step
if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
if arch=='CORI'  : max_mpi_per_node,atm_nthrds  = 64,1
atm_ntasks = max_mpi_per_node*num_nodes

#-------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CORI'   : cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   os.chdir(f'{case_dir}/{case}/')
   # # Change run directory to be next to bld directory
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   # update max task values
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#-------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   #    file.close()
   #-------------------------------------------------------
   # Set some non-default stuff
   if use_cosp: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cosp \" ')
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#-------------------------------------------------------------------------------
# Build
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#-------------------------------------------------------------------------------
# Write the namelist options and submit the run
if submit : 
   run_cmd('./xmlchange DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata ')
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output
   # file.write(' nhtfrq    = 0,1 \n') 
   # file.write(' mfilt     = 1,72 \n') # 1-day files
   file.write(' nhtfrq    = 0,-1,-24 \n') 
   file.write(' mfilt     = 1,24,1 \n') # 1-day files
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   file.write(" fincl2    = 'PS','PSL','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'FLUT','FSNTOA'")
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   ### COSP variables
   if use_cosp:
      file.write(          ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'")
      file.write(          ",'CLDTOT_ISCCP','FISCCP1_COSP'")
   ### 3D variables
   # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(             ",'MMF_QC','MMF_QI'")
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
   file.write(             ",'CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff

   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)

   # if num_dyn<(ntasks_atm*atm_nthrds): 
   #    file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')

   # file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   # if 'init_file_atm' in locals():
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   # if 'land_init_file' in locals():
   #    nfile = 'user_nl_elm'
   #    file = open(nfile,'w')
   #    file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
   #    file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
   #    file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # # Restart Frequency
   # if disable_output:
   #    run_cmd(f'./xmlchange -file env_run.xml REST_OPTION=NEVER')
   # else:
   #    run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#-------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#-------------------------------------------------------------------------------

