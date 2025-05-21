#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => master @ Oct 10

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

stop_opt,stop_n,resub,walltime = 'ndays',5,0,'6:00:00' # for ne120 w/ dt = 60 sec ~ 1 day per hour
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'6:00:00'

### compset='F2010'; grid='ne4pg2_ne4pg2';            num_nodes = 1 # doesn't work due to MPASSI
# compset='F2010';       grid='ne4pg2_oQU480';              num_nodes = 1
# compset='F2010';       grid='ne4_oQU240';                 num_nodes = 1
# compset='F2010';       grid='ne11_oQU240';                num_nodes = 4
# compset='WCYCL1850NS'; grid='ne11_oQU240';                num_nodes = 4
# compset='F2010';       grid='ne16_oQU240';                num_nodes = 8
# compset='F2010';       grid='ne30pg2_EC30to60E2r2';       num_nodes = 22
# compset='F2010';       grid='ne120pg2_r0125_oRRS18to6v3'; num_nodes = 64
# compset='F2010';       grid='conusx4v1_r05_oECv3';        num_nodes = 32
compset='F2010';       grid='conusx4v1pg2_r05_oECv3';     num_nodes = 32

# compset='FAQP'; grid='ne4pg2_oQU480';               num_nodes = 1
# compset='FAQP'; grid='ne30pg2_EC30to60E2r2';        num_nodes = 22
# compset='FRCE'; grid='ne4pg2_oQU480';               num_nodes = 1
# compset='FRCE'; grid='ne30pg2_EC30to60E2r2';        num_nodes = 22

case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset])

# custom time step for stabilizing ne11 WCYCL
# dtime = 10*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])
# dtime = 20*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])
# dtime = 30*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])

# custom time step for stabilizing ne120
# dtime =  1*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])
# dtime =  5*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])
# dtime = 15*60; case = '.'.join(['E3SM','2023-L80-SPINUP-00',grid,compset,f'DT_{dtime}'])


if debug_mode: case += '.debug'

#---------------------------------------------------------------------------------------------------
hiccup_data_path = '/lcrc/group/e3sm/ac.whannah/HICCUP/data/v3_L80_interpolated_files'
scratch_path = '/lcrc/group/e3sm/ac.whannah/scratch/chrys'
if compset=='F2010':
   if 'ne4'   in grid: init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne4np4_L80_c20231010.nc'
   if 'ne11'  in grid: 
      init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne11np4_L80_c20231010.nc'
      if dtime==20*60: 
         init_case='E3SM.2023-L80-SPINUP-00.ne11_oQU240.WCYCL1850NS.DT_600'
         init_file_atm = f'{scratch_path}/{init_case}/run/{init_case}.eam.i.0001-01-06-00000.nc'
      # if dtime==30*60: 
      #    init_case='E3SM.2023-L80-SPINUP-00.ne11_oQU240.WCYCL1850NS.DT_600'
      #    init_file_atm = f'{scratch_path}/{init_case}/run/{init_case}.eam.i.0001-01-06-00000.nc'
   if 'ne16'  in grid: init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne16np4_L80_c20231010.nc'
   if 'ne30'  in grid: init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne30np4_L80_c20231010.nc'
   if 'ne120' in grid: 
      if dtime==1*60: init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne120np4_L80_c20231010.nc'
      if dtime==5*60: 
         init_case='E3SM.2023-L80-SPINUP-00.ne120pg2_r0125_oRRS18to6v3.F2010.DT_60'
         init_file_atm = f'{scratch_path}/{init_case}/run/{init_case}.eam.i.0001-01-07-00000.nc'
      if dtime==15*60: 
         init_case='E3SM.2023-L80-SPINUP-00.ne120pg2_r0125_oRRS18to6v3.F2010.DT_300'
         init_file_atm = f'{scratch_path}/{init_case}/run/{init_case}.eam.i.0001-01-06-00000.nc'
   if 'conus' in grid: 
      # init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_conusx4v1_L80_c20231010.nc'
      init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_conusx4v1_L80_c20231109.nc'
if compset=='WCYCL1850NS':
   if 'ne11'  in grid: init_file_atm = f'{hiccup_data_path}/eami_mam4_Linoz_ne11np4_L80_c20231010.nc'
if compset=='FAQP':
   if 'ne4'   in grid: init_file_atm = f'{hiccup_data_path}/eami_aqp_ne4np4_L80_c20231010.nc'
   if 'ne30'  in grid: init_file_atm = f'{hiccup_data_path}/eami_aqp_ne30np4_L80_c20231010.nc'
if compset=='FRCE':
   if 'ne4'   in grid: init_file_atm = f'{hiccup_data_path}/eami_rce_ne4np4_L80_c20231010.nc'
   if 'ne30'  in grid: init_file_atm = f'{hiccup_data_path}/eami_rce_ne30np4_L80_c20231010.nc'
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')
atm_ntasks,atm_nthrds = num_nodes*128,1
atm_ntasks,atm_nthrds = num_nodes*64,2
# case_root = f'/lcrc/group/e3sm/ac.whannah/E3SMv3_dev/{case}'
case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'
#---------------------------------------------------------------------------------------------------
if newcase :
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
   cmd += f' --machine chrysalis '
   cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   # when specifying ncdata, do it here to avoid an error message
   file = open('user_nl_eam','w')
   file.write(f' ncdata = \'{init_file_atm}\' \n')
   file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 80 \" ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
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
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write(" inithist = \'MONTHLY\' \n")
   file.write(" inithist = \'ENDOFRUN\' \n")
   if 'dtime' in globals():
      if dtime < 15*60: 
         file.write(f'se_tstep            = {dtime/6} \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle   = 1 \n')
         file.write(f'dt_tracer_factor    = 6 \n')
         file.write(f'hypervis_subcycle_q = 6 \n')
      # if dtime == 20*60: 
      #    file.write(f'se_tstep            = {dtime/6} \n')
      #    file.write(f'dt_remap_factor     = 1 \n')
      #    file.write(f'hypervis_subcycle   = 1 \n')
      #    file.write(f'dt_tracer_factor    = 6 \n')
      #    file.write(f'hypervis_subcycle_q = 6 \n')
   file.close()
   #-------------------------------------------------------
   # specify a non-default time step
   if 'dtime' in locals(): 
      ncpl = 86400 / dtime
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
      run_cmd(f'./xmlchange LND_NCPL={str(ncpl)}')
   #-------------------------------------------------------
   # Set some run-time stuff
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if 'queue'    in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'stop_opt' in locals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in locals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
