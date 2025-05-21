#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115' # cli115 / cli145

case_dir = os.getenv('HOME')+'/E3SM/Cases/'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # not sure which branch, maybe => whannah/incite2021/momentum-transport-updated
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # v2.0.0 tag
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4/' # FOR HR TESTING ONLY - branch => whannah/mmf/2022-cess

print_commands_only = False

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

disable_bfb = True

debug_mode = False

queue = 'debug' # batch / debug

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10'
# stop_opt,stop_n,resub,walltime = 'ndays',73,0,'3:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5*2-1,'4:00'


compset,num_nodes,arch = 'F2010-MMF1',256,'GNUGPU'
# compset,num_nodes,arch = 'F-MMFXX',1000,'GNUGPU'
# compset,num_nodes,arch = 'F2010-CICE',512,'GNUCPU'

ne,npg,grid = 120,2,'ne120pg2_r0125_oRRS18to6v3'

# case_list = ['E3SM','INCITE2021-HR',arch,grid,compset]
case_list = ['E3SM','INCITE2021-HR-TEST',arch,grid,compset]

use_vt    = True
if 'MMF' in compset:
   if use_vt   : case_list.append('BVT')

### batch/version number
case_list.append('00') # initial HR runs

if debug_mode: case_list.append('debug')

case='.'.join(case_list)


### specify land initial condition file
# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# if ne==45: land_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
# Impose wall limits for Summit
#---------------------------------------------------------------------------------------------------
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

dtime = 15*60
if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step


max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 6,4#7

if 'atm_nthrds' not in locals(): atm_nthrds = tmp_atm_nthrds

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

   # Check if directory already exists
   if not print_commands_only:
      if os.path.isdir(case_dir+case): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + ' -compset '+compset+' -res '+grid
   cmd = cmd + ' -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='IBMGPU' : cmd += f' -compiler ibmgpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      if use_vt: 
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   # if ne==30: alt_ntask = 1200
   # alt_ntask = atm_ntasks
   alt_ntask = 1200
   cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   alt_ntask = 1350
   cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   alt_ntask = max_mpi_per_node
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   ### don't use threads
   # nthrds = 2
   # cmd = f'./xmlchange -file env_mach_pes.xml '
   # cmd += f'NTHRDS_CPL={nthrds},NTHRDS_CPL={nthrds},'
   # cmd += f'NTHRDS_OCN={nthrds},NTHRDS_ICE={nthrds}'
   # run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large numbers of columns (GCM or CRM)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
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
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      # Change inputdata from default due to permissions issue
      # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
      run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
      
      #-------------------------------------------------------
      # First query some stuff about the case
      #-------------------------------------------------------
      (ncpl        ,err) = sp.Popen('./xmlquery ATM_NCPL        -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (din_loc_root,err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (config_opts ,err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      file.write(' nhtfrq = 0,-1,-3 \n')
      file.write(' mfilt  = 1, 24,8 \n')
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
      file.write(          ",'TAUX','TAUY'")               # surface stress
      file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
      # variables for hurricane tracking 
      file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(          ",'Z300:I','Z500:I'")
      file.write(          ",'OMEGA850:I','OMEGA500:I'")
      file.write('\n')
      file.write(" fincl3 =  'PS','PSL'")
      file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
      file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
      file.write('\n')

      #------------------------------
      # Other namelist stuff
      #------------------------------

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      if 'init_file_atm' in locals():
         file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

      file.close()

   #-------------------------------------------------------
   # CLM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      if 'land_init_file' in locals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
         file.close()
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   if disable_bfb :
      run_cmd('./xmlchange BFBFLAG=FALSE')
   else :
      run_cmd('./xmlchange BFBFLAG=TRUE')
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
