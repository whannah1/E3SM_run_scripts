#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/' # branch => whannah/mmf/KPP-dev

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'nday',3,0,'2:00'

### common settings
ne,npg = 120,2
# grid   = f'ne{ne}pg{npg}_oECv3'
grid   = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'


### MMF options
crm_nx,crm_ny = 64,1
rad_nx        = 4

use_dmdf = True

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUGPU',1000, True
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUCPU',1000, True
compset,arch,num_nodes,disable_output = 'F2010-MMF1','GNUGPU',1000, True
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

### specify case name based on configuration
case_list = ['E3SM','2022-KPP-DMDF',f'ne{ne}pg{npg}',compset]

case_list.append(f'NXY_{crm_nx}x{crm_ny}')
case_list.append(f'RXY_{rad_nx}')

if disable_output: case_list.append('NO-OUTPUT')
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# land initial condition and surface data files
lnd_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
# lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
lnd_data_file = 'surfdata_0.125x0.125_simyr2000_c190730.nc'
lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
lnd_init_file = 'ELM_spinup.ICRUELM.r0125_r0125_oRRS18to6v3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
# # Ocean, sea ice, and river(?) initial conditions
# ocn_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files/v1.HR.piControl.advection-bug-fix'
# ocn_init_file = 'mpaso.rst.0089-03-01_00000.nc'
# ice_init_file = 'mpascice.rst.0089-03-01_00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   # set time step in all components to be consistent for MMF
   dtime = 15*60; ncpl  = 86400 / dtime
   run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   rad_ny = rad_nx if crm_ny>1 else 1
   run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
   run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   # turn on the data dumping option
   if use_dmdf: cpp_opt += ' -DDMDF_SNAPSHOT'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   if num_nodes>200:
      alt_ntask = 1024; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 1024; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   if num_nodes<200:
      alt_ntask = 768; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 768; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   alt_ntask = max_mpi_per_node
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   # Change inputdata from default due to permissions issue
   run_cmd(f'./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   ntasks_atm = None
   (ntasks_atm, err) = sp.Popen('./xmlquery NTASKS_ATM -value', \
                                 stdout=sp.PIPE, shell=True, 
                                 universal_newlines=True).communicate()
   ntasks_atm = float(ntasks_atm)
   #-------------------------------------------------------
   # ATM namelist
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   # Specify history output frequency and variables
   if not disable_output:
      file.write(' nhtfrq    = 0,-1,-24 \n') 
      file.write(' mfilt     = 1, 24,1 \n') # 1-day files
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
      file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
      file.write('\n')
      file.write(" fincl2    = 'PS','PSL','TS'")
      file.write(             ",'PRECT','TMQ'")
      file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(             ",'FLUT','FSNTOA'")
      file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
      file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
      file.write(             ",'TAUX','TAUY'")               # surface stress
      file.write(             ",'TUQ','TVQ'")                         # vapor transport
      file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(             ",'Z300:I','Z500:I'")
      file.write(             ",'OMEGA850:I','OMEGA500:I'")
      # file.write('\n')
      # file.write(" fincl3    = 'PS'")
      file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
      file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
      file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
      file.write('\n')
   
   # Other ATM namelist stuff
   if num_dyn<(ntasks_atm*atm_nthrds): 
      file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')

   # file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   # if 'init_file_atm' in locals():
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   # need climatological ozone for perpetual 1950:
   # ERROR: find_times: all(all_data_times(:) > time) ozone_1.9x2.5_L26_1850-2015_rcp45_c101108.nc
   # data path = /gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/cam/ozone
   # file.write('prescribed_ozone_file      = \'ozone_1.9x2.5_L26_2000clim_c091112.nc\'\n')
   # file.write('prescribed_ozone_type      = \'CYCLICAL\'\n')
   # file.write('prescribed_ozone_cycle_yr  = 2000\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'lnd_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # # OCN namelist
   # dtime = 15*60
   # nfile = 'user_nl_mpaso'
   # file = open(nfile,'w')
   # nminutes = int(dtime/60)
   # file.write(f' config_dt = \'00:{nminutes}:00\' \n')
   # file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency
   rest_opt_str = f'{stop_opt},REST_N={stop_n}' if disable_output else 'NEVER'
   run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={rest_opt_str}')

   continue_flag = 'TRUE' if continue_run else 'FALSE'
   run_cmd(f'./xmlchange -file env_run.xml CONTINUE_RUN=TRUE {continue_flag}')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
