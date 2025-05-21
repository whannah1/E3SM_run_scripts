#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli145' # cli115 / cli145

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases/'
src_dir  = f'{top_dir}/E3SM_SRC1/' # branch = whannah/mmf/fix-m2005+ECPP

print_commands_only = False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# compset = 'F-MMFXX-AQP1'
compset = 'F-MMFXX'

stop_opt,stop_n,resub = 'ndays',2,0

# ne,npg = 4,2
# ne,npg = 30,2
ne,npg = 45,2

res = f'ne{ne}pg{npg}'
# grid = f'{res}_{res}'
grid = f'{res}_r05_oECv3'



# arch,num_nodes = 'GNUGPU',  16
# arch,num_nodes = 'GNUGPU',  32
# arch,num_nodes = 'GNUGPU',  64
# arch,num_nodes = 'GNUGPU', 128
# arch,num_nodes = 'GNUGPU', 256
# arch,num_nodes = 'GNUGPU', 512
# arch,num_nodes = 'GNUGPU',1024

# arch,num_nodes = 'GNUCPU',  16
arch,num_nodes = 'GNUCPU',  32
# arch,num_nodes = 'GNUCPU',  64
# arch,num_nodes = 'GNUCPU', 128
# arch,num_nodes = 'GNUCPU', 256
# arch,num_nodes = 'GNUCPU', 512
# arch,num_nodes = 'GNUCPU',1024

crm_nx,crm_ny,rad_nx = 64, 1,4
# crm_nx,crm_ny,rad_nx = 32,32,4

# case = f'E3SM.TIMING-2022.{arch}.{grid}.{compset}.NODES_{num_nodes}.00'

case_list = ['E3SM','TIMING-2022',arch,grid,compset,f'NODES_{num_nodes}'] 

if 'MMF' in compset:
   if crm_ny>1: 
      case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   elif crm_nx!=64:
      case_list.append(f'NXY_{crm_nx}x{crm_ny}')


case_list.append('00')

case='.'.join(case_list)

# case = case+'.debug-on'


# walltime =  '0:10'
# walltime =  '2:00'
### Impose wall limits for Summits
if num_nodes>=  1: walltime =  '2:00'
if num_nodes>= 46: walltime =  '6:00'
# if num_nodes>= 92: walltime = '12:00'
# if num_nodes>=922: walltime = '24:00'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

if 'NTHRDS' in case:
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='NTHRDS': atm_nthrds = p[1]

task_per_node = max_mpi_per_node

atm_ntasks = task_per_node*num_nodes

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   if print_commands_only: 
      print(f'{msg}')
   else:
      print(f'\n{msg}')
      if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   #-------------------------------------------------------
   # Check if directory already exists
   if not print_commands_only:
      if os.path.isdir(f'{case_dir}/{case}'): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)
   #-------------------------------------------------------
   # create new case
   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid} -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   # set tasks per node
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)

#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config :

   #-------------------------------------------------------
   # set the CRM and radiation columns
   params = [p.split('_') for p in case.split('.')]
   for p in params: 
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')

   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')

   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''

   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   # cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -cppdefs \'{cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks
   # cmd = './xmlchange -file env_mach_pes.xml '
   # if 'GPU' in arch and ne==30 and num_nodes== 64: alt_ntask = 256
   # if 'GPU' in arch and ne==30 and num_nodes== 96: alt_ntask = 576
   # if 'GPU' in arch and ne==30 and num_nodes==128: alt_ntask = 720
   # if 'CPU' in arch and ne==30 and num_nodes== 64: alt_ntask = 1200
   # if 'CPU' in arch and ne==30 and num_nodes==128: alt_ntask = 1200
   # cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   # alt_ntask = task_per_node
   # cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   # cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   # run_cmd(cmd)

   #-------------------------------------------------------
   # Set threads
   # cmd = './xmlchange -file env_mach_pes.xml '
   # if 'GPU' in arch: alt_nthrds = 7
   # if 'CPU' in arch: alt_nthrds = 1
   # cmd += f'NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   # cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   # cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTHRDS_GLC=1,NTHRDS_ESP=1,NTHRDS_IAC=1'
   # run_cmd(cmd)

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
   ### Change inputdata from default due to permissions issue
   run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
   # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')

   #-------------------------------------------------------
   ### Namelist options
   if num_nodes>128:
      dyn_npes = 128*max_mpi_per_node
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      file.write(f' dyn_npes = {dyn_npes} \n')   # limit dynamics tasks
      file.close()

   #-------------------------------------------------------
   ### Disable restart file write for timing
   run_cmd('./xmlchange -file env_run.xml -id REST_OPTION -val never')

   #-------------------------------------------------------
   ### Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   ### Submit the run
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
