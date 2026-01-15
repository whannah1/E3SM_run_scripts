#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'atm146'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/atm/add-som-rce

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue = 'debug'  # regular / debug 
arch = 'GNUGPU' # GNUCPU / GNUGPU

stop_opt,stop_n,resub,walltime = 'ndays',73,11*5-1,'2:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,11-1,'2:00'

# compset='ERCE'; arch = 'GNUCPU'
compset='ERCE-MMF1'

# grid = 'ne30pg2_ne30pg2'; num_nodes = 64
grid = 'ne4pg2_ne4pg2'; num_nodes = 1

# crm_nx,crm_ny,rad_nx,rad_ny = 32,1,1,1
crm_nx,crm_ny,rad_nx,rad_ny = 32,1,32,1
# crm_nx,crm_ny,rad_nx,rad_ny = 64,1,1,1
# crm_nx,crm_ny,rad_nx,rad_ny = 64,1,64,1

# case_list = ['E3SM','2024-SOM-rad-00',arch,grid,compset] # Q-flux = 50
# case_list = ['E3SM','2024-SOM-rad-01',arch,grid,compset] # Q-flux = 0
# case_list = ['E3SM','2024-SOM-rad-02',arch,grid,compset] # Q-flux = 0 + fixed_total_solar_irradiance = 340
case_list = ['E3SM','2024-SOM-rad-03',arch,grid,compset] # Q-flux = 0 + fixed_total_solar_irradiance = 450
if 'MMF' in compset: 
   case_list.append(f'CNXY_{crm_nx}x{crm_ny}')
   case_list.append(f'RNXY_{rad_nx}x{rad_ny}')
case = '.'.join(case_list)

if debug_mode: case += '.debug'

# som_file = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/SOM-RCE_20240501.nc'
# if grid=='ne30pg2_oECv3': som_file = 'SOM/SOM-RCE_20240501.nc'
# if grid=='ne4pg2_oQU480': som_file = 'SOM/SOM-RCE_20240501.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')


if 'CPU' in arch: max_mpi_per_node,atm_nthrds  =  42,1 #; max_task_per_node = 42
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   6,7 #; max_task_per_node = 6
atm_ntasks = max_mpi_per_node*num_nodes

case_root = f'{case_dir}/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   if arch=='GNUCPU' : cmd += f' --compiler gnu    --pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' --compiler gnugpu --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --case {case_root}'
   # cmd += f' --case {case}'
   # cmd += f' --output-root {case_root} '
   # cmd += f' --script-root {case_root}/case_scripts '
   # cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# os.chdir(f'{case_root}/case_scripts')
os.chdir(f'{case_root}')
#---------------------------------------------------------------------------------------------------
if config :
   # run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   # run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   if 'MMF' in compset:
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
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
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-24 \n')
   file.write(' mfilt     = 1,1 \n')
   file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE'") # this is for easier use of height axis on profile plots
   file.write('\n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECL'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'FSNTOA'")
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I'")
   file.write(          ",'OMEGA850:I','OMEGA500:I'")
   file.write(          ",'U200:I','V200:I'")
   # # 3D variables
   # file.write(          ",'T','Q','Z3'")                       # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
   # file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
   # file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write('fixed_total_solar_irradiance = 340')
   file.write('fixed_total_solar_irradiance = 450')
   file.close()
   #-------------------------------------------------------
   # run_cmd(f'./xmlchange DOCN_SOM_FILENAME={som_file}')   
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'queue'    in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'stop_opt' in locals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in locals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------