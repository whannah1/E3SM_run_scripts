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
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => whannah/2025-polar-albedo-test

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

arch = 'GNUCPU' # GNUCPU / GNUGPU

# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',32,0,'0:30:00'
queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',365,0,'2:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',365,3,'2:00:00'

compset='F2010'

ne,npg,grid = 30,2,f'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 32


# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset]) # control
# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_00']) # force SW+LW albedo=1 < -60 degrees
# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_01']) # force SW    albedo=1 < -60 degrees
# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_02']) # decrease albedo by 0.02 < -60 degrees
# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_03']) # only modify direct albedos
# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_04']) # only modify diffuse albedos

# case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_10']) # proportional increase in SNICAR single scattering albedo
case = '.'.join(['E3SM','2025-polar-albedo-test-00',compset,'ALBEDO_HACK_11']) # proportional increase in SNICAR single scattering albedo
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 
atm_ntasks = max_mpi_per_node*num_nodes

if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

#-------------------------------------------------------------------------------
# din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
# init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'

# # atm_init_file = f'{init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
# lnd_init_file = f'{init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'

# lnd_data_root = f'{din_loc_root}/lnd/clm2/surfdata_map'
# lnd_data_file = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
# lnd_luse_file = f'{lnd_data_root}/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'

# lnd_init_root = '/pscratch/sd/w/whannah/files_finidat'
   # lnd_init_file = f'{lnd_init_root}/ELM_spinup.2024-SCIDAC.ICRUELM-SP.ne30pg2_r05_IcoswISC30E3r5.44-yr.2024-01-01.elm.r.2020-01-01-00000.nc'

# RUN_START_DATE = '1995-01-01'
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   if arch=='GNUCPU' : cmd += f' --mach pm-cpu --compiler gnu    --pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' --mach pm-gpu --compiler gnugpu --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --case {case} --handle-preexisting-dirs u '
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --compset {compset} --res {grid} '
   cmd += f' --project {acct} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #----------------------------------------------------------------------------
   cpp_opt = ''
   if 'ALBEDO_HACK_00' in case: cpp_opt += f' -DALBEDO_HACK_00'
   if 'ALBEDO_HACK_01' in case: cpp_opt += f' -DALBEDO_HACK_01'
   if 'ALBEDO_HACK_02' in case: cpp_opt += f' -DALBEDO_HACK_02'
   if 'ALBEDO_HACK_03' in case: cpp_opt += f' -DALBEDO_HACK_03'
   if 'ALBEDO_HACK_04' in case: cpp_opt += f' -DALBEDO_HACK_04'
   
   if 'ALBEDO_HACK_10' in case: cpp_opt += f' -DALBEDO_HACK_10'
   if 'ALBEDO_HACK_11' in case: cpp_opt += f' -DALBEDO_HACK_11'
   
   # if cpp_opt != '' :
   #    run_cmd(f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS --val \" -cppdefs \' {cpp_opt} \'  \"')

   if cpp_opt != '' :
      run_cmd(f'./xmlchange --append --file env_build.xml --id ELM_CONFIG_OPTS --val \" -cppdefs \' -DMODAL_AER {cpp_opt} \'  \"')
   #----------------------------------------------------------------------------
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   run_cmd('./case.setup --reset')
   #----------------------------------------------------------------------------
   # if arch=='GNUGPU': run_dir = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}/run'
   # if arch=='GNUCPU': run_dir = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}/run'
   # ic_path = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'
   # # run_cmd('./xmlchange RUN_STARTDATE=1950-01-01,START_TOD=0')
   # run_cmd('./xmlchange RUN_TYPE=hybrid')
   # run_cmd('./xmlchange GET_REFCASE=FALSE')   
   # run_cmd('./xmlchange RUN_REFCASE=\'v3.LR.amip_0101\'')
   # run_cmd('./xmlchange RUN_REFDATE=2000-01-01')
   # run_cmd(f'cp {ic_path}/* {run_dir}/')
#---------------------------------------------------------------------------------------------------
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if submit :
   #----------------------------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   # Specify history output frequency and variables
   file.write(' nhtfrq    = 0 \n')
   file.write(' mfilt     = 1 \n')
   file.write(" avgflag_pertape = 'A','A','I' \n")
   file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','ASDIR','ASDIF','ALDIR','ALDIF'\n")
   file.close()
   #----------------------------------------------------------------------------
   lnd_init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'
   lnd_init_file = f'{lnd_init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'
   # defulat does not work => surfdata_0.5x0.5_simyr2010_c230922_with_TOP.nc
   lnd_data_root = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   # lnd_data_file = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c240308_TOP.nc'
   lnd_data_file = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
   file=open('user_nl_elm','w')
   file.write(f" fsurdat = \'{lnd_data_file}\' \n")
   file.write(f" check_finidat_pct_consistency = .false. \n")
   file.write(f" finidat = \'{lnd_init_file}\' \n")
   file.close()
   #----------------------------------------------------------------------------
   # Set some run-time stuff
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   #----------------------------------------------------------------------------
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
