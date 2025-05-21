#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'atm146'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/mmf/pam-updates

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue = 'regular'  # regular / debug 
arch = 'GNUCPU' # GNUCPU / GNUGPU 

stop_opt,stop_n,resub,walltime = 'ndays',1,1,'0:30'
# stop_opt,stop_n,resub,walltime = 'ndays',10,6-1,'3:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,2,'3:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,9-1,'3:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,10*5-1,'5:00'

compset='F2010'
# compset='F2010-MMF1'
# compset='F2010-MMF2'

ne,npg,grid=30,2,'ne30pg2_oECv3'; num_nodes=64
# ne,npg,grid=30,2,'ne30pg2_oECv3'; num_nodes=128
# ne,npg,grid = 4,2,'ne4pg2_ne4pg2';  num_nodes = 1

if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';   num_nodes = 1

# case_list = ['E3SM','2024-PAM-CHK-00',grid,compset]
# case_list = ['E3SM','2024-PAM-CHK-01',grid,compset] # larger CRM - crm_nx=65

# nlev=72;crm_nz=60; case_list = ['E3SM','2024-PAM-CHK-02',grid,compset,f'L{nlev}'] # default crm width but use new vertical grid
# case_list = ['E3SM','2024-PAM-CHK-03',grid,compset] # test for PR related edits
# nlev=72;crm_nz=60; case_list = ['E3SM','2024-PAM-CHK-04',grid,compset] # more tests - also need data for E3SM tutorial

# Increase crm_nx to combat excess precip
# nlev=72;crm_nz=60;crm_nx=65; case_list = ['E3SM','2024-PAM-CHK-05',grid,compset,f'NX_{crm_nx}'] 
# nlev=72;crm_nz=60;crm_nx=75; case_list = ['E3SM','2024-PAM-CHK-05',grid,compset,f'NX_{crm_nx}'] 
# nlev=72;crm_nz=60;crm_nx=95; case_list = ['E3SM','2024-PAM-CHK-05',grid,compset,f'NX_{crm_nx}'] 
# nlev=72;crm_nz=60;crm_nx=125; case_list = ['E3SM','2024-PAM-CHK-05',grid,compset,f'NX_{crm_nx}']

# case_list = ['E3SM','2024-PAM-CHK-06a',arch,grid,compset]  # check that PAM runs after updating branch
# case_list = ['E3SM','2024-PAM-CHK-07',arch,grid,compset]  # check MMF2 after SCREAM merge and fixes

# case_list = ['E3SM','2024-PAM-CHK-07-gcc-10.2',arch,grid,compset]  # check MMF2 after SCREAM merge and fixes
# case_list = ['E3SM','2024-PAM-CHK-07-gcc-11.1',arch,grid,compset]  # check MMF2 after SCREAM merge and fixes
# case_list = ['E3SM','2024-PAM-CHK-07-gcc-11.2',arch,grid,compset]  # check MMF2 after SCREAM merge and fixes
# case_list = ['E3SM','2024-PAM-CHK-07-gcc-12.1',arch,grid,compset]  # check MMF2 after SCREAM merge and fixes

case_list = ['E3SM','2024-PAM-CHK-07-gcc-11.2-alt',arch,grid,compset]  # update mpi version





if debug_mode: case_list.append('debug')
case='.'.join(case_list)

if 'nlev'   in locals(): 
   init_scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/init_scratch/'
   if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.L72_c20230819.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

case_root = f'{case_dir}/{case}'
#---------------------------------------------------------------------------------------------------
if 'FSCM' in compset: 
   max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
else:
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  =  42,1 ; max_task_per_node = 42
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   6,7 ; max_task_per_node = 6
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case_root}'
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
os.chdir(f'{case_root}')
if config : 
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   if 'nlev'   in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev   {nlev} \" ')
   if 'crm_nz' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
   if 'crm_nx' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} \" ')
   #-------------------------------------------------------
   # Run case setup
   if clean: run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit
if submit : 
   #-------------------------------------------------------
   # atmos namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #-------------------------------------------------------
   # atmos history output
   file.write(' nhtfrq    = 0,-3,-24 \n')
   file.write(' mfilt     = 1,8,1 \n')
   ### add some monthly variables to the default
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   ### hourly 2D variables
   file.write(" fincl2    = 'PS','TS','PSL'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'PRECC','PRECSC'")
   file.write(             ",'PRECL','PRECSL'")
   file.write(             ",'LHFLX','SHFLX'")                    # surface fluxes
   file.write(             ",'FSNT','FLNT'")                      # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                      # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")                    # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")                      # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")              # cloud water path
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT'")
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   file.write('\n')
   ### daily 3D variables
   # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write('\n')

   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   file.close() # close atm namelist file
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   # specify land initial condition file
   if grid=='ne30pg2_oECv3':
      land_init_path = '/gpfs/alpine2/atm146/proj-shared/hannah6/init_scratch/'
      land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
      land_data_path = '/gpfs/alpine2/atm146/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
      land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'
   if 'init_file_lnd' in globals() or 'data_file_lnd' in globals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'init_file_lnd' in globals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
      if 'data_file_lnd' in globals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
      file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'queue'    in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'stop_opt' in locals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in locals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
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
