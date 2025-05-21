#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
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
queue = 'regular'  # regular / debug 

compset,ne,npg = 'F-MMF1',30,2


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
else:
   # stop_opt,stop_n,resub,walltime = 'ndays',6,6-1,'4:00:00'
   stop_opt,stop_n,resub,walltime = 'ndays',6,1,'4:00:00'
   

### hi-res output for visualization
# case='.'.join(['E3SM','HR-OUTPUT',grid,compset,'CRMNX_256','CRMDX_500','RADNX_8','BVT','00'])
case='.'.join(['E3SM','HR-OUTPUT',grid,compset,'CRMNX_256','CRMDX_500','RADNX_8','BVT','01'])  # summer


# case = case+'.debug-on'
# case = case+'.checks-on'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)
# if ne==120: dtime = 5*60

if 'dtime' in locals(): ncpl = 86400/dtime

if 'atm_ntasks' not in locals():
   if ne==30: atm_ntasks = 5400
   if ne==4:  atm_ntasks = 64

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

   if os.path.isdir(f'{case_dir}/{case}'):
      exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid}'
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
   # if changing vertical levels make sure to update ncdata here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   if '.RRTMGP.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
   if '.RRTMGPXX.' in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp -rrtmgpxx \"')
   if 'L60_test' in case and 'MMF' not in compset and '.L60.' in case: 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 60 \" ')
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''

   # CRM variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   if 'debug-on' in case and 'MMFXX' in compset : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads
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
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-6 \n')
   file.write(' mfilt     = 1,4 \n')
      
   file.write('\n')
   file.write(" fincl2    = 'PS:I','PSL:I','TS:I'")
   file.write(             ",'PRECT:I','TMQ:I'")
   file.write(             ",'LHFLX:I','SHFLX:I'")
   file.write(             ",'FSNT:I','FLNT:I'")
   file.write(             ",'FLNS:I','FSNS:I'")
   file.write(             ",'TGCLDLWP:I','TGCLDIWP:I'")    
   file.write(             ",'TAUX:I','TAUY:I'")

   # file.write(             ",'T:I','Q:I' ")
   # file.write(             ",'U:I','V:I','OMEGA:I'")
   # file.write(             ",'CLDLIQ:I','CLDICE:I'")

   file.write(             ",'CRM_T:I','CRM_QV:I'")
   file.write(             ",'CRM_U:I','CRM_W:I'")
   file.write(             ",'CRM_QC:I','CRM_QPC:I'")
   file.write(             ",'CRM_QI:I','CRM_QPI:I'")
   file.write('\n')
   
   #------------------------------
   # Other namelist stuff
   #------------------------------
   if 'atm_ntasks' in locals(): 
      if num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   # file.write(" inithist = \'ENDOFRUN\' \n")

   if '.FVT_' in case: 
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='FVT':
            file.write(f' MMF_VT_wn_max = {int(p[1])} \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   # close atm namelist file
   file.close()

   
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   #-------------------------------------------------------
   if '.01' in case: iyr,imn,idy = 1,7,1 

   if 'iyr' in locals(): 
      init_date = f'{iyr}-{imn:02d}-{idy:02d}'
      os.system(f'./xmlchange -file env_run.xml  RUN_STARTDATE={init_date}')
   
   # os.system(f'./xmlchange -file env_run.xml  SSTICE_DATA_FILENAME={init_file_dir}{init_file_sst}')
   # os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_ALIGN={iyr}')
   # os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_START={iyr}')
   # os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_END={iyr+1}')
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
