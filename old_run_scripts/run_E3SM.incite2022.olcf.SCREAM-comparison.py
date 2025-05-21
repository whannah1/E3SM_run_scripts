#!/usr/bin/env python
# This case is meant to be compared with this case:
# /gpfs/alpine/cli115/proj-shared/donahue/run_cases/ne1024pg2_ne1024pg2.F2010-SCREAMv1.20221014_production_run.27604ccf3f1aaa88ea3413b774ef3817cad7343a
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5/' # master @ Oct 18, 2022

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

stop_opt,stop_n,resub,walltime = 'ndays',40,0,'4:00'

ne,npg =  30,2; grid = f'ne{ne}pg{npg}_oECv3'

num_nodes =  128

compset,arch = 'F2010-MMF1','GNUGPU'

iyr,imn,idy = 2013,10,1; init_date = f'{iyr}-{imn:02d}-{idy:02d}'

### specify case name based on configuration
case_list = ['E3SM','2022-SCREAMv1-COMP',compset,grid,init_date]
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

#---------------------------------------------------------------------------------------------------
# specify initial condition files

init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'

# init_file_sst = f'HICCUP.sst_noaa.{init_date}.c20220610.nc'
init_file_atm = 'HICCUP.atm_era5.2013-10-01.ne30np4.L60.nc'

land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_init_path = '/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch/ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-10-01/run/'
land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-10-01.elm.r.2013-10-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')


max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
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
   # ATM namelist
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' nhtfrq    = 0,-1,-3 \n') 
   file.write(' mfilt     = 1,24,8 \n') # 1-day files
   file.write(" fincl1    = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(            ",'CLOUD','CLDLIQ','CLDICE'")
   file.write(            ",'PTTEND','PTEQ'")             # 3D physics tendencies
   file.write(            ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   file.write('\n')
   file.write(" fincl2 = 'PS:I','PSL:I','TS:I'")
   file.write(         ",'PRECT:I','TMQ:I'")
   file.write(         ",'LHFLX:I','SHFLX:I'")             # surface fluxes
   file.write(         ",'FSNT:I','FLNT:I'")               # Net TOM heating rates
   file.write(         ",'FLNS:I','FSNS:I'")               # Surface rad for total column heating
   file.write(         ",'FSNTC:I','FLNTC:I'")             # clear sky heating rates for CRE
   file.write(         ",'FLUT:I','FSNTOA:I'")
   file.write(         ",'LWCF:I','SWCF:I'")               # cloud radiative foricng
   file.write(         ",'TGCLDLWP:I','TGCLDIWP:I'")       # liq/ice water path
   file.write(         ",'TAUX:I','TAUY:I'")               # surface stress
   file.write(         ",'TUQ:I','TVQ:I'")                         # vapor transport
   file.write(         ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model level
   file.write(         ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(         ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(         ",'Z300:I','Z500:I'")
   file.write(         ",'OMEGA850:I','OMEGA500:I'")
   file.write('\n')
   file.write(" fincl3 = 'PS:I'")
   file.write(         ",'T:I','Q:I','Z3:I'")                # 3D thermodynamic budget components
   file.write(         ",'U:I','V:I','OMEGA:I'")             # 3D velocity components
   file.write(         ",'CLOUD:I','CLDLIQ:I','CLDICE:I'")   # 3D cloud fields
   file.write(         ",'QRL:I','QRS:I'")                 # 3D radiative heating 
   file.write(         ",'QRLC:I','QRSC:I'")               # 3D clearsky radiative heating 
   file.write('\n')
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # Modified start date and SST file
   #-------------------------------------------------------
   os.system(f'./xmlchange --file env_run.xml RUN_STARTDATE=2013-10-01')

   sst_grid_file = '\\$DIN_LOC_ROOT/ocn/docn7/domain.ocn.0.25x0.25.c20190221.nc'
   sst_data_file = '\\$DIN_LOC_ROOT/ocn/docn7/SSTDATA/sst_ice_CMIP6_HighResMIP_E3SM_0.25x0.25_2010_clim_c20190125_intoisst.nc'

   os.system(f'./xmlchange --file env_run.xml  SSTICE_GRID_FILENAME={sst_grid_file}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={sst_data_file}')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN=1')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START=0')
   os.system(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END=0')
   #------------------------------------------------------- 
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
