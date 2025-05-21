#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, datetime
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,submit = False,False,False,False

acct = 'm3312'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => master @ ????

newcase      = True
config       = True
build        = True
submit       = True

continue_run = False

queue = 'regular'

stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'

# init_date = datetime.datetime.strptime('2020-01-01 00', '%Y-%m-%d %H')
init_date = datetime.datetime.strptime('2023-09-08 00', '%Y-%m-%d %H')

ens_num_list = []
# # perturbed IC files  - 0.1%
# ens_num_list.append('01')
# ens_num_list.append('02')
# ens_num_list.append('03')
# ens_num_list.append('04')
# ens_num_list.append('05')

# internally generated perturbations
ens_num_list.append('11')
ens_num_list.append('12')
ens_num_list.append('13')
ens_num_list.append('14')
ens_num_list.append('15')

# # more perturbed IC files - 1%
# ens_num_list.append('21')
# ens_num_list.append('22')
# ens_num_list.append('23')
# ens_num_list.append('24')
# ens_num_list.append('25')

# # more perturbed IC files - 10%
# ens_num_list.append('31')
# ens_num_list.append('32')
# ens_num_list.append('33')
# ens_num_list.append('34')
# ens_num_list.append('35')

# # more perturbed IC files - 100%
# ens_num_list.append('41')
# ens_num_list.append('42')
# ens_num_list.append('43')
# ens_num_list.append('44')
# ens_num_list.append('45')

# # perturbed namelist parameters
# ens_num_list.append('51')
# ens_num_list.append('52')
# ens_num_list.append('53')
# ens_num_list.append('54')
# ens_num_list.append('55')

#---------------------------------------------------------------------------------------------------
for ens_num in ens_num_list: 

   case = '.'.join(['E3SM',f'2024-E3SM-tutorial-hindcast-{ens_num}',init_date.strftime('%Y-%m-%d')])

   init_scratch  = '/global/cfs/projectdirs/m3312/whannah/HICCUP/E3SM_tutorial'
   # init_scratch  = '/global/cfs/projectdirs/e3sm/www/Tutorials/2024/practicum/day_4/atm_breakout'
   if int(ens_num)<=10 or int(ens_num)>20:
      init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne30np4.L80.{ens_num}.nc'
   if int(ens_num)>10 and int(ens_num)<=20:
      init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne30np4.L80.nc'
   init_file_sst = f'{init_scratch}/HICCUP.sst_noaa.{init_date.strftime("%Y-%m-%d")}.nc'
   #------------------------------------------------------------------------------------------------
   if 'init_file_atm' not in locals(): raise RuntimeError('init_file_atm was not set')
   #------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   scratch_root = f'{os.getenv("SCRATCH")}/e3sm_scratch/pm-cpu'
   case_root = f'{scratch_root}/{case}'
   # case_root = f'/global/cfs/projectdirs/m3312/whannah/HICCUP/E3SM_tutorial/runs/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {scratch_root} --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset F2010 --res ne30pg2_oECv3 '
      cmd += f' --mach pm-cpu --pecount 256x1 '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   if config : run_cmd('./case.setup --reset')
   if build : run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------------------------
      # Namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      # Specify history output frequency and variables
      file.write(' nhtfrq    = 0,-3 \n')
      file.write(' mfilt     = 1,8 \n')
      file.write(" fincl2 = 'PS','TS','PSL'")                     # sfc temperature and pressure
      file.write(          ",'PRECT','TMQ'")                      # precipitation 
      file.write(          ",'LHFLX','SHFLX'")                    # surface fluxes
      file.write(          ",'FSNT','FLNT','FLUT'")               # Net TOM rad fluxes
      file.write(          ",'FLNS','FSNS'")                      # Net sfc rad fluxes
      file.write(          ",'TGCLDLWP','TGCLDIWP'")              # liq & ice water path
      file.write(          ",'TBOT','QBOT','UBOT','VBOT'")        # lowest model level
      file.write(          ",'T850','Q850','U850','V850','Z850'") # 850mb
      file.write(          ",'T500','Q500','U500','V500','Z500'") # 500mb
      file.write(          ",'T200','Q200','U200','V200','Z200'") # 200mb
      file.write(          ",'PHIS'") # sfc geopotential for TC tracking
      # atmos initial condition for hindcast
      if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
      if int(ens_num)>10 and int(ens_num)<=20:
         file.write(f' pertlim = {ens_num}e-10 \n')
      file.close()
      #-------------------------------------------------------------------------
      # Specify start date and SST file for hindcast
      sst_yr = int(init_date.strftime('%Y'))
      os.system(f'./xmlchange --file env_run.xml  RUN_STARTDATE={init_date.strftime("%Y-%m-%d")}')
      os.system(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={init_file_sst}')
      os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_yr}')
      os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_yr}')
      os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={sst_yr+1}')
      # os.system('./xmlchange --file env_build.xml CALENDAR=GREGORIAN)
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in locals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in locals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      #-------------------------------------------------------------------------
      if continue_run :
         run_cmd('./xmlchange CONTINUE_RUN=TRUE')
      else:
         run_cmd('./xmlchange CONTINUE_RUN=FALSE')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   del init_file_atm
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
