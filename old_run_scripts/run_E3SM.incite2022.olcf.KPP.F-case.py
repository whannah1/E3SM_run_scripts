#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime, shutil
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/' # branch => whannah/mmf/KPP-dev

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'2:00'
# stop_opt,stop_n,resub,walltime = 'nstep',3,0,'0:30'

### common settings
ne,npg = 120,2; grid = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'

### GCM physics time step
# dtime = 15*60

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
# compset,arch,num_nodes,disable_output = 'F1950-MMF1','GNUGPU',1000, False
# compset,arch,num_nodes,disable_output = 'F1950-MMF1','GNUGPU',1000, True
# compset,arch,num_nodes,disable_output = 'F1950-MMF1','GNUGPU',1200, True
compset,arch,num_nodes,disable_output = 'F1950-MMF1','GNUGPU',1800, True

# non-MMF companion case
# compset,arch,num_nodes,disable_output = 'F1950',     'GNUCPU', 256, False

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# specify case name based on configuration
case_list = ['E3SM','2022-KPP-F',arch,f'ne{ne}pg{npg}',compset]
case_list.append(f'NN_{num_nodes}')

# case_list.append(f'alt_ntasks_01') # reduce CPL and make LND+ICE be concurrent
# case_list.append(f'alt_ntasks_02') # reduce NTASK for CPL, OCN, ROF
case_list.append(f'alt_ntasks_03') # 

if disable_output: case_list.append('NO-OUTPUT')
if debug_mode: case_list.append('debug')

case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# land initial condition and surface data files
if 'r0125' in grid:
   lnd_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   # lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
   lnd_data_file = 'surfdata_0.125x0.125_simyr2000_c190730.nc'
   # lnd_data_file = 'surfdata_0.125x0.125_simyr2010_c191025.nc'
   lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   lnd_init_file = 'ELM_spinup.ICRUELM.r0125_r0125_oRRS18to6v3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
if 'CPU' in arch and use_6x7_cpu : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

rundir = f'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/{case}/run'

if 'alt_ntasks_01' in case:
   ocn_ntasks = 1024
   ice_ntasks = 4096
   cpl_ntasks = int(atm_ntasks/4)
   rof_ntasks = int(atm_ntasks/2)
if 'alt_ntasks_02' in case:
   ocn_ntasks = 256
   ice_ntasks = 4096
   cpl_ntasks = int(atm_ntasks/10)
   rof_ntasks = int(atm_ntasks/10)
if 'alt_ntasks_03' in case:
   ocn_ntasks = 1024
   ice_ntasks = 4800
   cpl_ntasks = task_per_node*256
   rof_ntasks = task_per_node*128


if cpl_ntasks>atm_ntasks: cpl_ntasks = atm_ntasks
if ocn_ntasks>atm_ntasks: ocn_ntasks = atm_ntasks

lnd_ntasks = atm_ntasks-ice_ntasks

#---------------------------------------------------------------------------------------------------
if newcase :
   #-------------------------------------------------------
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   # Set tasks for each component
   run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_CPL={cpl_ntasks}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_LND={lnd_ntasks}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_OCN={ocn_ntasks}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_ICE={ice_ntasks}')
   run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_ROF={rof_ntasks}')

   # always put ice on different root PE so it runs in parallel with land
   run_cmd(f'./xmlchange -file env_mach_pes.xml ROOTPE_ICE={lnd_ntasks}')
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: 
      run_cmd('./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cppdefs \' -DYAKL_DEBUG \'  \" ')
      run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean: run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   if not disable_output:
      file.write(' nhtfrq    = 0,-1,-24 \n') 
      file.write(' mfilt     = 1, 24,1 \n') # 1-day files
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
      # file.write('\n')
      # file.write(" fincl3    = 'PS'")
      # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
      # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
      # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
      file.write('\n')
   #------------------------------
   # Other namelist stuff

   # file.write(f' crm_accel_factor = 3 \n')         # CRM mean-state acceleration factor (default is 2)
   # file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   # if 'dtime' in locals():
   #    if dtime == 5*60 :
   #       file.write(f'dt_tracer_factor = 5 \n')
   #       file.write(f'dt_remap_factor = 1 \n')
   #       file.write(f'se_tstep = 60 \n')
   #       file.write(f'hypervis_subcycle_q = 5 \n')
   #    if dtime == 10*60 :
   #       file.write(f'dt_tracer_factor = 5 \n')
   #       file.write(f'dt_remap_factor = 1 \n')
   #       file.write(f'se_tstep = 60 \n')
   #       file.write(f'hypervis_subcycle_q = 5 \n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'lnd_init_file' in locals() or 'lnd_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'lnd_data_file' in locals(): file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      if 'lnd_init_file' in locals(): file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange -file env_run.xml CONTINUE_RUN={continue_flag} ')   

   if disable_output:
      run_cmd(f'./xmlchange -file env_run.xml REST_OPTION=never')
   else:
      run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')

   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
