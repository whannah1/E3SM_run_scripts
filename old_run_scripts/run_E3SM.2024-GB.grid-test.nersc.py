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
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/Gordon-Bell-2024

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # regular / debug 
arch = 'GNUCPU' # GNUCPU / GNUGPU

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:10:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
#if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10:00'

compset='F2010'
# compset='F2010-MMF1'

ne,npg,grid = 30,2,'ne30pg2_oECv3'; num_nodes = 8

# ne,npg,grid = 16,2,'ne16pg2_oECv3'; num_nodes = 16
# ne,npg,grid = 24,2,'ne24pg2_oECv3'; num_nodes = 8
# ne,npg,grid = 60,2,'ne60pg2_oECv3'; num_nodes = 32
# ne,npg,grid = 70,2,'ne70pg2_oECv3'; num_nodes = 32

# case = '.'.join(['E3SM','2024-GB.grid-test',arch,grid,compset])
# case = '.'.join(['E3SM','2024-GB.grid-test-01',arch,grid,compset]) # use MPASSI
case = '.'.join(['E3SM','2024-GB.grid-test-02',arch,grid,compset]) # test new domain file tool

if debug_mode: case += '.debug'

#--------------------------------------------------------------------------------------------------
# Set input data paths
#---------------------------------------------------------------------------------------------------
# init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'
# if ne==16: init_file_atm = f'{init_scratch}/????'
# if ne==24: init_file_atm = f'{init_scratch}/????'
# if ne==70: init_file_atm = f'{init_scratch}/????'

# init_path_lnd = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
# init_case_lnd = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.2010-01-01'
# init_file_lnd = f'{init_path_lnd}/{init_case_lnd}.elm.r.2010-01-01-00000.nc'
# data_path_lnd = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
# data_file_lnd = f'{data_path_lnd}/surfdata_ne30pg2_simyr2010_c210402.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 
atm_ntasks = max_mpi_per_node*num_nodes

if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'


# dtime = 4*60
# ncpl  = 86400/dtime

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   if arch=='GNUCPU' : cmd += f' --mach pm-cpu --compiler gnu    --pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' --mach pm-gpu --compiler gnugpu --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')

   if compset=='F2010':
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 60 \" ')
   #-------------------------------------------------------
   # # if specifying ncdata, do it here to avoid an error message
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_atm}\' \n')
   #    file.close()
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
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
   file.write('\n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECL'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # variables for tracking stuff like hurricanes
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
   # file.write(f' cosp_lite = .true. \n')
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write(" inithist = \'ENDOFRUN\' \n")
   file.close()
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   # if 'init_file_lnd' in locals() or 'data_file_lnd' in locals():
   #    nfile = 'user_nl_elm'
   #    file = open(nfile,'w')
   #    if 'init_file_lnd' in locals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
   #    if 'data_file_lnd' in locals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
   #    # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
   #    file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in globals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
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

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------