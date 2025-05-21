#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# for hybrid coupled runs we need o remove the "xtime" variable from MPAS restarts
# NCO commands below were suggested by Chris Golaz

# mv v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc tmp.nc
# ncks -O --hdr_pad=10000 tmp.nc v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc
# ncrename -v xtime,xtime.orig v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc
# rm tmp.nc

# mv v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc tmp.nc
# ncks -O --hdr_pad=10000 tmp.nc v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc
# ncrename -v xtime,xtime.orig v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc
# rm tmp.nc

# or just remove the variable entirely
#  ncks -x -v xtime in.nc out.nc 
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # branch => whannah/mmf/2022-coupled-historical

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30'

### common settings
ne,npg = 120,2
# grid   = f'ne{ne}pg{npg}_oECv3'
grid   = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'


### MMF options
use_vt,use_mf = True,True
crm_nx,crm_ny = 64,1
rad_nx        = 4 

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUGPU',1000, False
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUGPU',1000, True
# compset,arch,num_nodes,disable_output = 'WCYCL1950',     'GNUCPU', 256, False

### test the impact of VT+ESMT
# ne,npg=4,2; compset,arch,num_nodes,disable_output,use_vt,use_mf = 'F2010-MMF1','GNUGPU',1,True,False,False
# ne,npg=4,2; compset,arch,num_nodes,disable_output,use_vt,use_mf = 'F2010-MMF1','GNUGPU',1,True,True,True
# ne,npg=4,2; compset,arch,num_nodes,disable_output,use_vt,use_mf = 'F2010-MMF1','GNUGPU',1,True,False,True
ne,npg=4,2; compset,arch,num_nodes,disable_output,use_vt,use_mf = 'F2010-MMF1','GNUGPU',1,True,True,False

if ne==4: grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

### specify case name based on configuration
case_list = ['E3SM','2022-KPP',f'ne{ne}pg{npg}',compset]
if ne==4 and use_vt: case_list.append('VT')
if ne==4 and use_mf: case_list.append('ESMT')
if not ne==4 and disable_output: case_list.append('NO-OUTPUT')
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

#---------------------------------------------------------------------------------------------------
# land initial condition and surface data files
if 'WCYCL' in compset:
   lnd_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
   lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   lnd_init_file = 'ELM_spinup.ICRUELM.r0125_r0125_oRRS18to6v3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   #---------------------------------------------------------------------------------------------------
   # Ocean, sea ice, and river initial conditions
   ocn_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files/v1.HR.piControl.advection-bug-fix'
   ocn_init_file = 'mpaso.rst.0089-03-01_00000.nc'
   ice_init_file = 'mpascice.rst.0089-03-01_00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

# dtime = 20*60   # GCM physics time step
if 'dtime' in locals(): ncpl  = 86400 / dtime

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
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   #    file.close()
   #-------------------------------------------------------
   # set time step in all components to be consistent for MMF
   if 'WCYCL' in compset and 'MMF' in compset:
      dtime = 20*60; ncpl  = 86400 / dtime
      run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if 'MMF' in compset: 
      if  crm_ny==1 and use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if  crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   if 'WCYCL' in compset:
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
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
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
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)

   if num_dyn<(ntasks_atm*atm_nthrds): 
      file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')

   # file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   # if 'init_file_atm' in locals():
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   #-------------------------------------------------------
   if 'lnd_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # OCN namelist
   #-------------------------------------------------------
   if 'WCYCL' in compset and 'MMF' in compset:
      dtime = 20*60
      nfile = 'user_nl_mpaso'
      file = open(nfile,'w')
      nminutes = int(dtime/60)
      file.write(f' config_dt = \'00:{nminutes}:00\' \n')
      file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency
   if disable_output:
      run_cmd(f'./xmlchange -file env_run.xml REST_OPTION=NEVER')
   else:
      run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')

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
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
