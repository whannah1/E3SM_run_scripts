#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'

# directory info
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/'

#clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True 

# stop_opt,stop_n,resub,walltime = 'nyears',5,3,'4:00'
# rest_opt,rest_n = 'nyears',1
stop_opt,stop_n,resub,walltime = 'nmonths',3,0,'2:00'
rest_opt,rest_n = 'nmonths',1

# ne,npg    = 30,2
# grid      = 'ne30pg2_ne30pg2'
grid      = 'ne45pg2_r05_oECv3'
# grid = 'ne16pg2_r05_oQU240'
compset   = 'ICRUELM'

num_years = 20
stop_date = datetime.datetime(2010, 10, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

case = f'CLM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

clm_opt = ' -bgc sp -clm_start_type arb_ic'

### land IC
start_date_str = '2005-10-01'
land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_init_file = 'CLM_spinup.ICRUCLM45.ne45pg2_r05_oECv3.20-yr.2010-10-01.clm2.r.2005-10-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# if ne==30 : dtime = 30*60
# if ne==120 : dtime = 5*60
# ncpl = 86400 / dtime

num_nodes = 8
task_per_node = 84

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
   cmd = f'{src_dir}/cime/scripts/create_newcase --case {case_dir}/{case}'
   cmd += f' --compset {compset} --res {grid}'
   cmd += ' --machine summit --compiler gnu  --pecount '+str(num_nodes*task_per_node)+'x1 '
   run_cmd(cmd)

   # Change run directory to be next to bld directory
   os.chdir(case_dir+case+'/')
   memberwork = os.getenv('MEMBERWORK')
   run_cmd(f'./xmlchange -file env_run.xml RUNDIR=\'{memberwork}/{acct}/e3sm_scratch/{case}/run\' ' )
   #run_cmd('./xmlchange -file env_run.xml   DATM_MODE=CLMCRUNCEPv7' )
   run_cmd(f'./xmlchange -file env_run.xml   RUN_STARTDATE={start_date_str}' )

   if grid == 'ne30pg2_ne30pg2':
      map_file_lnd2rof = 'cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc'
      map_file_rof2lnd = 'cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_mono.200220.nc'
      run_cmd(f'./xmlchange -file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
      run_cmd(f'./xmlchange -file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
   
  
   # Change inputdata from default due to permissions issue
   #run_cmd('./xmlchange -file env_run.xml  DIN_LOC_ROOT=/gpfs/alpine/scratch/jlee1046/cli115/inputdata ')
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = ''
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   
   # nfile = 'user_nl_clm'
   # file = open(nfile,'w') 
   # file.write(' hist_empty_htapes = .true. \n') 

#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #----------------------------------------------------------------------------
   #----------------------------------------------------------------------------   
   #run_cmd('./xmlchange -file env_build.xml -id MOSART_MODE -val NULL')
   run_cmd('./xmlchange --append -file env_run.xml -id CLM_BLDNML_OPTS  -val  \"'+clm_opt+'\"' )

   if '_r05_' in grid: 
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_LND -val 1350 ')
      # run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 1350 ')
      # run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 1350 ')
      # run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 1350 ')
      # run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 1350 ')
   
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   # run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')   # enable debug mode
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   
   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         run_cmd('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )

   #-------------------------------------------------------
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # run_cmd('./xmlchange -file env_run.xml      ATM_NCPL='          +str(ncpl)   )
   run_cmd('./xmlchange -file env_run.xml      STOP_OPTION='       +stop_opt    )
   run_cmd('./xmlchange -file env_run.xml      STOP_N='            +str(stop_n) )
   run_cmd('./xmlchange -file env_run.xml      RESUBMIT='          +str(resub)  )
   run_cmd('./xmlchange -file env_workflow.xml JOB_WALLCLOCK_TIME='+walltime    )

   # Restart Frequency
   run_cmd(f'./xmlchange -file env_run.xml  REST_OPTION={rest_opt}')
   run_cmd(f'./xmlchange -file env_run.xml  REST_N={rest_n}')

   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)

   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange -file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange -file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------