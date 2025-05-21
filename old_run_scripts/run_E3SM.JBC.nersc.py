#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

# src_dir  = top_dir+'E3SM_SRC2/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

queue = 'regular'  # regular / debug 

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73*2,5*10/2-1,'5:00:00'


# case='.'.join(['E3SM','PI-CPL','v1','ne30'])
case='.'.join(['E3SM','PI-CPL','v2','ne30'])


# case += '.00' # initial version - 2021/11/22
case += '.01' # switch to hybrid run to fix start date/time - 2021/11/28

#---------------------------------
# v1 setup
if '.v1.' in case:
   src_dir=top_dir+'E3SM_SRC0/' 
   compset,ne,npg,grid = 'A_WCYCL1850S_CMIP6',30,0,'ne30_oECv3_ICG'
   ic_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/PI_control_v1/archive/rest/0500-01-01-00000'
#---------------------------------
# v2 setup
if '.v2.' in case:
   src_dir = top_dir+'E3SM_SRC3/' 
   compset,ne,npg,grid = 'WCYCL1850',30,2,'ne30pg2_EC30to60E2r2'
   ic_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/PI_control_v2/archive/rest/0501-01-01-00000'
#---------------------------------


### debugging options
# case += '.debug-on'
# case += '.checks-on'

scratch = '/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

#-------------------------------------------------------------------------------
# Define run command
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
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(tcolor.RED+"\nThis case already exists!\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid} '
   # cmd += ' --pecount 5400x1'
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
   #-------------------------------------------------------
   # # Set up a branch run
   # run_cmd('./xmlchange RUN_TYPE=branch')
   # run_cmd('./xmlchange GET_REFCASE=FALSE')
   # run_cmd('./xmlchange RUN_STARTDATE=0001-01-01')
   # if '.v1.' in case:
   #    run_cmd('./xmlchange RUN_REFCASE=\'20180129.DECKv1b_piControl.ne30_oEC.edison\'')
   #    run_cmd('./xmlchange RUN_REFDATE=0500-01-01')
   # if '.v2.' in case:
   #    run_cmd('./xmlchange RUN_REFCASE=\'v2.LR.piControl\'')
   #    run_cmd('./xmlchange RUN_REFDATE=0501-01-01')
   #-------------------------------------------------------
   # Set up a hybrid run
   run_cmd('./xmlchange RUN_TYPE=hybrid')
   run_cmd('./xmlchange GET_REFCASE=FALSE')
   run_cmd('./xmlchange RUN_STARTDATE=0001-01-01,START_TOD=0')
   if '.v1.' in case:
      run_cmd('./xmlchange RUN_REFCASE=\'20180129.DECKv1b_piControl.ne30_oEC.edison\'')
      run_cmd('./xmlchange RUN_REFDATE=0500-01-01')
      # run_cmd('./xmlchange RUN_STARTDATE=0500-01-01,START_TOD=0')
   if '.v2.' in case:
      run_cmd('./xmlchange RUN_REFCASE=\'v2.LR.piControl\'')
      run_cmd('./xmlchange RUN_REFDATE=0501-01-01')
      # run_cmd('./xmlchange RUN_STARTDATE=0501-01-01,START_TOD=0')
   #-------------------------------------------------------
   # copy the initialization data files
   run_cmd(f'cp {ic_path}/* {scratch}/{case}/run/')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   #-------------------------------------------------------
   # Build the case
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
   # (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
   #                                   stdout=sp.PIPE, shell=True).communicate()
   # (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
   #                                   stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   if '.v1.' in case: nfile = 'user_nl_cam'
   if '.v2.' in case: nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-1,-6 \n')
   file.write(' mfilt     = 1,24,4 \n')
   file.write(" fincl2    = 'PS','TS','PSL'")
   file.write(             ",'PRECC','PRECL'")
   file.write(             ",'FLNS','FLNT','FLUT'")
   file.write(             ",'FSNS','FSNT'")
   file.write(             ",'LHFLX','SHFLX'")
   file.write(             ",'LWCF','SWCF'")
   file.write(             ",'TAUX','TAUY'")
   file.write(             ",'TGCLDLWP','TGCLDIWP','TMQ'")    
   file.write(             ",'TREFHT','QREFHT','RHREFHT'")
   file.write(             ",'U10','OMEGA500'")
   file.write(             ",'U200','U850','UBOT'")
   file.write(             ",'V200','V850','VBOT'")
   file.write('\n')
   file.write(" fincl3    =  'PS','T','Q','Z3'")   
   file.write(             ",'U','V','OMEGA'")          
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
   file.write(             ",'QRS','QRL'")
   file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   # file.write(" inithist = \'MONTHLY\' \n")
   # file.write(" inithist = \'ENDOFRUN\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   # OCN namelist
   #-------------------------------------------------------
   file = open('user_nl_mpaso','w')
   # nminutes = int(dtime/60); file.write(f' config_dt = \'00:{nminutes}:00\' \n')
   file.write(f' config_AM_mixedLayerDepths_Tgradient = .true. \n')
   file.write(f' config_AM_mixedLayerDepths_Dgradient = .true. \n')
   file.close()

   if not continue_run:
      ### request daily mixed layer depth output
      file = open(f'{scratch}/{case}/run/streams.ocean','r')
      contents = file.read()
      file.close()
      if 'diag_daily' not in contents:
         file = open(f'{scratch}/{case}/run/streams.ocean','a')
         file.write('\n')
         file.write('<stream name="diag_daily"\n')
         file.write('        type="output"\n')
         file.write('        io_type="pnetcdf"\n')
         file.write('        filename_template="mpaso.hist.diagnostic_daily.$Y-$M-$D.nc"\n')
         file.write('        filename_interval="00-01-00_00:00:00"\n')
         file.write('        output_interval="00-00-01_00:00:00"\n')
         file.write('        clobber_mode="truncate">\n')
         file.write('\n')
         file.write('    <var name="xtime"/>\n')
         file.write('    <var name="tThreshMLD"/>\n')
         file.write('    <var name="dThreshMLD"/>\n')
         file.write('    <var name="dGradMLD"/>\n')
         file.write('    <var name="tGradMLD"/>\n')
         file.write('    <var name="ssh"/>\n')
         file.write('    <var name="pressureAdjustedSSH"/>\n')
         file.write('    <var name="boundaryLayerDepth"/>\n')
         file.write('    <var_array name="activeTracersAtSurface"/>\n')
         file.write('    <var_array name="surfaceVelocity"/>\n')
         file.write('\n')
         file.write('</stream>\n')
         file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
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
