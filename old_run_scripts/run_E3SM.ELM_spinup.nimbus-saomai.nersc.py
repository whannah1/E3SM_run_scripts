#!/usr/bin/env python

# commands for creating ROF map files
'''
ATM_GRID_NAME=saomai-128x8
ROF_GRID_NAME=r05
ATM_GRID=/global/cfs/cdirs/m2637/jsgoodni/Saomai_2006_ne128x8_lon130E_lat25Npg2.scrip.nc
ROF_GRID=/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc
MAP_FILE1=/global/cfs/cdirs/m2637/jsgoodni/map_${ATM_GRID_NAME}_to_${ROF_GRID_NAME}_mono.20240108.nc
MAP_FILE2=/global/cfs/cdirs/m2637/jsgoodni/map_${ROF_GRID_NAME}_to_${ATM_GRID_NAME}_mono.20240108.nc
echo $MAP_FILE1
echo $MAP_FILE2
ncremap -a tempest --src_grd=${ATM_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE1} --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
ncremap -a tempest --src_grd=${ROF_GRID} --dst_grd=${ATM_GRID} --map_file=${MAP_FILE2} --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm2637'

src_dir = os.getenv('HOME')+'/E3SM-maint-2.1' # branch => whannah/2024-nimbus-saomai-m2.1

#clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True 


queue = 'regular'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'nyears',5, 4-1,'4:00:00' # 20 years
if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:10:00'

compset   = 'ICRUELM' 

# rest_opt,rest_n = 'nyears',1

grid = f'ne0np4-saomai-128x8_EC30to60E2r2'

num_years = 20 # overall years for spin-up
stop_date = datetime.datetime(2010, 1, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

case = f'ELM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

clm_opt = ' -bgc sp -clm_start_type arb_ic'

fsurdat_path = '/global/cfs/cdirs/m2637/jsgoodni/surfdata_Saomai2006ne128x8pg2_simyr2006_c240105.nc'

#---------------------------------------------------------------------------------------------------
def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         run_cmd('./xmlchange --file '+file_name+' '+var_name+'='+str(value) )
#---------------------------------------------------------------------------------------------------
def write_namelist_elm():
   nfile = ''
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   file.write(f' fsurdat = \'{fsurdat_path}\' \n')
   # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
   file.close()
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   case_root = f'/pscratch/sd/w/jsgoodni/e3sm_scratch/pm-cpu/{case}'
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '

   map_file_lnd2rof = f'/global/cfs/cdirs/m2637/jsgoodni/map_saomai-128x8_to_r05_mono.20240108.nc'
   map_file_rof2lnd = f'/global/cfs/cdirs/m2637/jsgoodni/map_r05_to_saomai-128x8_mono.20240108.nc'

   run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
   run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
   
   write_namelist_elm()

#---------------------------------------------------------------------------------------------------
# Configure
os.chdir(f'{case_root}/case_scripts')
if config : 
   #----------------------------------------------------------------------------   
   #run_cmd('./xmlchange --file env_build.xml --id MOSART_MODE --val NULL')
   run_cmd('./xmlchange --append --file env_run.xml --id ELM_BLDNML_OPTS  --val  \"'+clm_opt+'\"' )

   if '_r05_' in grid: 
      run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_LND --val 1350 ')
   if 'ne16pg2' in grid:         run_cmd(f'./xmlchange NTASKS_LND=384 ')
   if grid=='ne256pg2_ne256pg2': run_cmd(f'./xmlchange NTASKS_LND=3200 ')
   
   # if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

#---------------------------------------------------------------------------------------------------
# Build
if build : 
   # run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')   # enable debug mode
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
if submit : 
   write_namelist_elm()
   #-------------------------------------------------------
   # run_cmd('./xmlchange --file env_run.xml      ATM_NCPL='          +str(ncpl)   )

   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency
   if 'rest_opt' in locals(): run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   if 'rest_n'   in locals(): run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')

   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange --file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2

   if continue_run :
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
