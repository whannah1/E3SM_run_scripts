#!/usr/bin/env python
# spin-up notes
# 00 - for initial spin up use vertically regridded version of L72 file - run for at least 1 year
# Using a horizontally regridded version of the L60 spinup from ne30pg2 was 
# very problematic with lots of gravity waves in the ne45 and ne120 cases
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
queue = 'regular'  # regular / debug 

# compset = 'F2010'
# compset = 'F-EAM-AQP1'
compset = 'F-EAM-RCEMIP'


# ne,npg =   4,2
# ne,npg =  30,2
# ne,npg =  45,2
ne,npg = 120,2


if 'AQP' in compset or 'RCE' in compset:
   grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'
else:
   grid = f'ne{ne}pg{npg}_r05_oQU480' if ne==4 else f'ne{ne}pg{npg}_r05_oECv3'


### switch to np4 for sanity check
# ne,npg =  30,0; grid = f'ne{ne}_r05_oECv3'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
else:   
   # stop_opt,stop_n,resub,walltime = 'ndays',9,0,'2:00:00'
   if 'AQP' in compset or 'RCE' in compset:
      if ne==  4: stop_opt,stop_n,resub,walltime = 'ndays',30,0,'1:00:00'
      if ne== 30: stop_opt,stop_n,resub,walltime = 'ndays',30,0,'2:00:00'
      if ne== 45: stop_opt,stop_n,resub,walltime = 'ndays',30,0,'3:00:00'
      if ne==120: stop_opt,stop_n,resub,walltime = 'ndays',30,0,'6:00:00'
   else:
      if ne==  4: stop_opt,stop_n,resub,walltime = 'ndays',365,0,'5:00:00'
      if ne== 30: stop_opt,stop_n,resub,walltime = 'ndays',365,0,'4:00:00'
      # if ne== 45: stop_opt,stop_n,resub,walltime = 'ndays',29,12,'2:00:00'
      # if ne==120: stop_opt,stop_n,resub,walltime = 'ndays',29,12,'6:00:00'
      if ne== 45: stop_opt,stop_n,resub,walltime = 'ndays', 7,0,'1:00:00' # final run for getting back to Jan 1
      if ne==120: stop_opt,stop_n,resub,walltime = 'ndays',17,0,'3:00:00' # final run for getting back to Jan 1



case = '.'.join(['E3SM','L60-spinup',grid,compset,'00'])
# case = '.'.join(['E3SM','L60-spinup',grid,compset,'01']) # new spin up starting with 5-year spun up non-MMF run (short time step?)
# case = '.'.join(['E3SM','L60-spinup',grid,compset,'02']) # just test ne30 for sanity


hiccup_path = '/global/cscratch1/sd/whannah/HICCUP/data'
# init_file_atm = f'{hiccup_path}/cami_mam3_Linoz_ne{ne}np4_L60_c20210817.nc'

ic_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/L60_initial_conditions/'
if '.00' in case: init_file_atm = f'{ic_path}/eam_i_mam3_Linoz_ne{ne}np4_L60_c20210823.nc'
if 'AQP' in compset: init_file_atm = f'{hiccup_path}/cami_aqua_ne{ne}np4_L60_c20210817.nc'
if 'RCE' in compset: init_file_atm = f'{hiccup_path}/cami_rcemip_ne{ne}np4_L60_c20210817.nc'

# case = case+'.debug-on'
# case = case+'.checks-on'


if 'AQP' not in compset and 'RCE' not in compset:
   land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
   land_init_file = f'{land_init_path}/ELM_spinup.ICRUELM.{grid}.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# if ne==120: dtime = 5*60
# if ne==45 : dtime = 20*60

if 'dtime' in locals(): ncpl = 86400/dtime

if ne==  4: atm_ntasks = 96
if ne== 30: atm_ntasks = 5400
if ne== 45: atm_ntasks = 5400
if ne==120: atm_ntasks = 10800

# if 'sanity-check' in case: del init_file_atm

#-------------------------------------------------------------------------------
# Define run and query commands
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
def query(qvar):
   (value, error) = sp.Popen(f'./xmlquery {qvar} -value', \
                             stdout=sp.PIPE, shell=True, \
                             universal_newlines=True).communicate()
   return value
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'):
      exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   run_cmd(f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}')

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}')

if config : 
   #-------------------------------------------------------
   # if using non-default ncdata update the namelist here to avoid an error
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------  
   # use variance transport for smoother solution
   if 'MMF' in compset:
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   # if 'sanity-check' in case:
   #    run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx 1000 -crm_dt 5 -nlev 72 -crm_nz 58 \" ')

   run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 60 \" ')
   #-------------------------------------------------------
   # Set the tasks and threads
   if 'MMF' in case:
      run_cmd(f'./xmlchange NTHRDS_ATM=1,NTASKS_ATM={atm_ntasks} ')
   else:
      run_cmd(f'./xmlchange NTHRDS_ATM=4,NTASKS_ATM={atm_ntasks} ')

   if ne==120:
      cmd = './xmlchange -file env_mach_pes.xml NTASKS_LND=1350,NTASKS_CPL=1350,NTASKS_OCN=1200,NTASKS_ICE=1200'
      run_cmd(cmd)
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
   # First query some stuff about the case
   #-------------------------------------------------------
   # din_loc_root = query('DIN_LOC_ROOT')
   # config_opts  = query('CAM_CONFIG_OPTS')
   # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 


   # file.write(' nhtfrq    = 0,1 \n')
   # file.write(f' mfilt     = 1,1 \n')
   # file.write(" fincl2    = 'PS','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")   
   # file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   # file.write(             ",'OMEGA850','OMEGA500'")
   # file.write(             ",'T500','T850','Q850'")
   # file.write(             ",'U200','U850'")
   # file.write(             ",'V200','V850'")
   # file.write('\n')
   
   if 'init_file_atm' in locals(): 
      file.write(f' ncdata = \'{init_file_atm}\' \n')

   file.write(" inithist = \'ENDOFRUN\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   if 'dtime' in locals():
      # if dtime == 20*60 :
      #    # file.write(f'dt_tracer_factor = 4 \n')
      #    # file.write(f'dt_remap_factor = 4 \n')
      #    # file.write(f'se_tstep = 300 \n')
      # if dtime == 15*60 :
      #    file.write(f'dt_tracer_factor = 1 \n')
      #    file.write(f'dt_remap_factor = 1 \n')
      #    file.write(f'se_tstep = 300 \n')
      # if dtime == 10*60 :
      #    file.write(f'dt_tracer_factor = 1 \n')
      #    file.write(f'dt_remap_factor = 1 \n')
      #    file.write(f'se_tstep = 300 \n')
      if dtime == 5*60 :
         file.write(f'dt_tracer_factor = 4 \n')
         file.write(f'dt_remap_factor = 2 \n')
         file.write(f'se_tstep = 75 \n')
      if dtime == 1*60 :
         file.write(f'dt_tracer_factor = 1 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')

   # close atm namelist file
   file.close()

   
   # if ne==120 and npg==2 : 
   #    file = open('user_nl_cpl','w') 
   #    file.write(' eps_agrid = 1e-11 \n')
   #    file.close()
   # if ne==120 and npg==2 : run_cmd('./xmlchange -file env_run.xml      EPS_AGRID=1e-11' )

   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
      file.write(f' fsurdat = \'/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2000_c200624.nc \' \n ')
      file.close()

   # 64_data format is needed for ne120 output
   os.system('./xmlchange ATM_PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE')
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
