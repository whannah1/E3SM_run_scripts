#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC1/'

# clean        = True
newcase      = True
config       = True
build        = True
# submit       = True
# continue_run = True
queue = 'debug'  # regular / debug 

ne,npg = 4,2
compset = 'F-MMFXX'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'   # f'{res}_r05_oECv3' / f'{res}_{res}'
grid = f'{res}_{res}'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'nstep',5,0,'0:30:00'
   # stop_opt,stop_n,resub,walltime = 'ndays',1,2,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'


arch,num_nodes = 'GNUCPU',1
# arch,num_nodes = 'GNUGPU',1


case = '.'.join(['E3SM','CORI-GPU-TEST',arch,grid,compset,'CRMNX_32','CRMDX_2000','RADNX_1'])


# case = case+'.debug-on'
# case = case+'.checks-on'


land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
if grid=='ne30pg2_r05_oECv3': land_init_file = f'{land_init_path}/CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01.clm2.r.2010-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)

if 'dtime' in locals(): ncpl = 86400/dtime

if arch=='GNUCPU' : task_per_node = 36
if arch=='GNUGPU' : task_per_node = 8

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
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   # Check if directory already exists
   # if not print_commands_only:
   if os.path.isdir(case_dir+case): 
      exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + ' -compset '+compset+' -res '+grid
   cmd = cmd + ' -mach cori-gpu '
   if arch=='GNUCPU' : cmd = cmd + ' -compiler gnu    -pecount '+str(num_nodes*task_per_node)+'x1 '
   if arch=='GNUGPU' : cmd = cmd + ' -compiler gnugpu -pecount '+str(num_nodes*task_per_node)+'x1 '
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
   if arch=='GNUGPU': 
      pcols = np.ceil( (ne**2*6*npg**2) / (num_nodes*task_per_node) )
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -pcols {int(pcols)} \" ' )
   #-------------------------------------------------------
   # if changing vertical levels make sure to update ncdata here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
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
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if '.CRM_SFC_FLX.' in case: cpp_opt += ' -DMMF_CRM_SFC_FLUX'

   # convective variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   if '.FVT' in case: 
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='FVT': cpp_opt += f' -DMMF_VT_KMAX={p[1]} '

   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads - disable threading for MMF

   if 'atm_ntasks' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')

   if 'MMF' in compset:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')

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
                                     stdout=sp.PIPE, shell=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if stop_opt=='nstep':
      file.write(' nhtfrq    = 0,1 \n')
      file.write(' mfilt     = 1,72 \n')
      # file.write(f' mfilt    = 1,{stop_n} \n')
   else:
      file.write(' nhtfrq    = 0,-1,-24 \n')
      file.write(' mfilt     = 1,24,1 \n')

   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   # file.write(             ",'OMEGA850','OMEGA500'")
   # file.write(             ",'T500','T850','Q850'")
   # file.write(             ",'U200','U850'")
   # file.write(             ",'V200','V850'")
   #------------------------------
   # Other namelist stuff
   #------------------------------
   if 'atm_ntasks' in locals(): 
      if num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')   

   if 'dtime' in locals():
         if dtime == 20*60 :
            if ne==4 :
               file.write(f'dt_tracer_factor = 2 \n')
               file.write(f'dt_remap_factor = 2 \n')
               file.write(f'se_tstep = 600 \n')
            if ne==30 :
               file.write(f'dt_tracer_factor = 4 \n')
               file.write(f'dt_remap_factor = 4 \n')
               file.write(f'se_tstep = 300 \n')

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
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
