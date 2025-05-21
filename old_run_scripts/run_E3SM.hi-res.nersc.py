#!/usr/bin/env python
print_commands_only = False
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): 
   print(f'\n{clr.GREEN}{cmd}{clr.END}') ; 
   if not print_commands_only: os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => ????

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular' # regular / batch / debug

# stop_opt,stop_n,resub,walltime = 'nstep',10,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'2:00:00'

ne,npg = 120,2
grid   = f'ne{ne}pg{npg}_r0125_oRRS18to6v3' # f'ne{ne}pg{npg}_oECv3'

# compset,arch,num_nodes = 'F2010-MMF1','GNUGPU',256
compset = 'F2010-MMF1'

# case_list = ['E3SM','HR-TEST',f'ne{ne}pg{npg}',compset]
case_list = ['E3SM','HR-TEST',f'ne{ne}pg{npg}',compset,'DT_15m']
# case_list = ['E3SM','HR-TEST',f'ne{ne}pg{npg}',compset,'DT_10m']
# case_list = ['E3SM','HR-TEST',f'ne{ne}pg{npg}',compset,'DT_05m']

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

if ne==120: dtime = 15*60   # GCM physics time step

if 'DT_15m' in case: dtime = 15*60
if 'DT_10m' in case: dtime = 10*60
if 'DT_05m' in case: dtime =  5*60

if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

# max_task_per_node = 42
# if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
# if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
# task_per_node = max_mpi_per_node
# atm_ntasks = task_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f'  -compset {compset} -res {grid}'
   # if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   # if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: os.chdir(f'{case_dir}/{case}/')
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   # Set tasks for all components
   # cmd = './xmlchange -file env_mach_pes.xml '
   # if num_nodes>200:
   #    alt_ntask = 1024; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   #    alt_ntask = 1024; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # if num_nodes<200:
   #    alt_ntask = 768; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   #    alt_ntask = 768; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # alt_ntask = max_mpi_per_node
   # cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   # cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   # run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
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
   # Change inputdata from default due to permissions issue
   # init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
   # init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   # run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------   
   # file.write(' nhtfrq    = 0,-1 \n') 
   # file.write(' mfilt     = 1, 24 \n') # 1-day files
   # file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   # file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   # file.write('\n')
   # file.write(" fincl2    = 'PS','PSL','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'FLUT','FSNTOA'")
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'TUQ','TVQ'")                         # vapor transport
   # file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   # file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(             ",'Z300:I','Z500:I'")
   # file.write(             ",'OMEGA850:I','OMEGA500:I'")
   # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
   # file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # if 'DT_15m' in case:
   #    file.write(f'dt_tracer_factor = 5 \n')
   #    file.write(f'dt_remap_factor = 1 \n')
   #    file.write(f'se_tstep = 60 \n')
   if 'DT_10m' in case:
      file.write(f'dt_tracer_factor = 5 \n')
      file.write(f'dt_remap_factor = 1 \n')
      file.write(f'se_tstep = 60 \n')
   if 'DT_05m' in case:
      file.write(f'dt_tracer_factor = 5 \n')
      file.write(f'dt_remap_factor = 1 \n')
      file.write(f'se_tstep = 60 \n')
   # query the atmos tasks for setting dyn_npes
   # ntasks_atm = None
   # (ntasks_atm, err) = sp.Popen('./xmlquery NTASKS_ATM -value', stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   # ntasks_atm = float(ntasks_atm)
   # if num_dyn<(ntasks_atm*atm_nthrds): file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')
   file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
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
