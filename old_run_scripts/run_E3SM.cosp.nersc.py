#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305
top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC4/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug 

compset,ne,npg = 'F-MMF1',30,2 

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_{res}'   # f'{res}_r05_oECv3' / f'{res}_{res}'

if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',5,0,'6:00:00'

case = '.'.join(['E3SM',grid,compset,'CRMNX_64','RADNX_4','HR-CRM-OUTPUT','00']) # 

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

dtime = 20*60
atm_ntasks = 5400

num_dyn = ne*ne*6
if 'dtime' in locals(): ncpl = 86400/dtime
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
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
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   # cmd += ' --pecount '+str(num_dyn)+'x1'
   if '_gnu_' in case : cmd = cmd + ' --compiler gnu '
   if '_pgi_' in case : cmd = cmd + ' --compiler pgi '
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')

#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
   #-------------------------------------------------------
   # Set tasks
   if 'atm_ntasks' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
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
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                            stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                            stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-1,-1 \n')
   file.write(' mfilt     = 1,24,24 \n')
   file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
   file.write('\n')
   file.write(" fincl2    = 'PS:I','PSL:I','TS:I'")
   file.write(             ",'PRECT:I','TMQ:I'")
   file.write(             ",'LHFLX:I','SHFLX:I'")          # surface fluxes
   file.write(             ",'FSNT:I','FLNT:I'")            # Net TOM heating rates
   file.write(             ",'FLNS:I','FSNS:I'")            # Surface rad for total column heating
   file.write(             ",'FSNTC:I','FLNTC:I'")          # clear sky heating rates for CRE
   file.write(             ",'TGCLDLWP:I','TGCLDIWP:I'")
   file.write(             ",'T:I','Q:I','Z3:I' ")          # 3D thermodynamic budget components
   file.write(             ",'U:I','V:I','OMEGA:I'")        # 3D velocity components
   file.write(             ",'CLDLIQ:I','CLDICE:I'")        # 3D cloud fields
   file.write(             ",'QRL:I','QRS:I'")              # 3D radiative heating profiles
   file.write(             ",'CRM_U:I','CRM_W:I'")
   file.write(             ",'CRM_T:I','CRM_QV:I'")
   file.write(             ",'CRM_QC:I','CRM_QI:I'")
   file.write(             ",'CRM_QPC:I','CRM_QPI:I'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   file.write(" inithist = \'MONTHLY\' \n")
   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')
   file.close()         
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
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
