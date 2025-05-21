#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4/' # branch => whannah/mmf/2022-cess

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = True

queue = 'debug' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:20'

### common settings
# ne,npg = 120,2; grid = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'
ne,npg =  30,2; grid = f'ne{ne}pg{npg}_r05_oECv3'

if ne==120: num_nodes = 1000
if ne== 30: num_nodes =  128

### MMF options
use_vt,use_mf = True,True
crm_nx,crm_ny = 64,1
rad_nx        = 4 

if ne==120: crm_dx =  500
if ne== 30: crm_dx = 2000

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

compset,arch = 'F2010-MMF1','GNUGPU'

### specify case name based on configuration
case_list = ['E3SM','2022-DYAMOND',f'ne{ne}pg{npg}',compset]
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files
if '_r05_' in grid:
   land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   land_data_file = 'surfdata_0.5x0.5_simyr2010_c191025.nc'

   land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

# GCM physics time step
if ne== 30 : dtime = 15*60
if ne==120 : dtime =  5*60

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
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx} \" ')
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
   cmd = './xmlchange -file env_mach_pes.xml '
   if num_nodes>200:
      alt_ntask = 1024; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 256*6; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   if num_nodes<200:
      alt_ntask = 768; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 768; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
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
   # init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
   init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   ntasks_atm = None
   (ntasks_atm     , err) = sp.Popen('./xmlquery NTASKS_ATM    -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   ntasks_atm = float(ntasks_atm)
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   # file.write(' nhtfrq    = 0,-1 \n') 
   # file.write(' mfilt     = 1, 24 \n') # 1-day files
   # file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   # file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   # file.write('\n')
   # file.write(" fincl2    = 'PS','PSL','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'FLUT','FSNTOA'")
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'TUQ','TVQ'")                         # vapor transport
   # file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   # file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(             ",'Z300:I','Z500:I'")
   # file.write(             ",'OMEGA850:I','OMEGA500:I'")
   # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
   # file.write('\n')
   #------------------------------
   #------------------------------
   file.write('empty_htapes=.true.\n')
   # output freq: 1/3 steps=15 min, -3=3hrs
   if ne==120: nn = 3
   if ne== 30: nn = 1
   file.write(f'nhtfrq = {nn},{nn},{nn},{nn},-3,-3,-3,-3,-3,-3\n') 
   file.write(f'mfilt = 96,96,96,96,8,8,8,8,8,8\n') #new file freq: daily in all cases
   file.write("fincl1 = 'CLDLOW:I','CLDMED:I','CLDHGH:I','CLDTOT:I'") 
   file.write(        ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   # file.write(        ",'TMCLDLIQ:I','TMCLDICE:I'") 
   # file.write(        ",'TMRAINQM:I','TMCLDRIM:I'")
   file.write(        ",'TMQ:I','CAPE:I','CIN:I'")
   file.write('\n')
   file.write("fincl2 = 'PS:I','PSL:I,'TS:I','TREFHT:I','QREFHT:I'")
   # file.write(        ",'PRECT:I','PRECSL:I','WINDSPD_10M:I'")
   file.write(        ",'PRECT:I'")
   file.write(        ",'TAUX:I','TAUY:I','SHFLX:I','LHFLX:I'")
   file.write('\n')
   file.write("fincl3 = 'FSNTOA:I','FLNT:I','FLNTC:I','FSNTOAC:I'")
   file.write(        ",'FSNS:I','FSDS:I','FLNS:I','FLDS:I'")
   file.write('\n')
   file.write("fincl4 = 'RH200:I','RH500:I','RH700:I','RH850:I'")
   file.write(        ",'OMEGA200:I','OMEGA500:I','OMEGA700:I','OMEGA850:I'")
   file.write(        ",'Z200:I','Z500:I','Z700:I','Z850:I'")
   # 3 hrly (mostly 3d) variables below here 
   # file.write("fincl5 = 'PS:I','PSL:I'")
   # file.write(        ",'TMNUMLIQ:I','TMNUMICE:I','TMNUMRAI:I'")
   file.write('\n')
   file.write("fincl6 = 'U:I','V:I'\n")
   file.write("fincl7 = 'T:I','Q:I','Z3:I'\n")
   file.write("fincl8 = 'CLDLIQ:I','CLDICE:I'\n")
   file.write("fincl9 = 'CLOUD:I','OMEGA:I'\n")
   # file.write("fincl10= 'EMIS:I','TOT_ICLD_VISTAU:I'\n")
   #------------------------------
   # Other namelist stuff
   #------------------------------
   if num_dyn<(ntasks_atm*atm_nthrds): 
      file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')

   file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   if 'init_file_atm' in locals():
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

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
   os.system(f'./xmlchange -file env_run.xml      RUN_STARTDATE=2020-01-20')

   sst_grid_file = '$DIN_LOC_ROOT/ocn/docn7/domain.ocn.360x720.201027.nc'
   sst_data_file = '$DIN_LOC_ROOT/atm/cam/sst/sst_ifs_360x720_20200110_20200305_c201013.nc'
   os.system(f'./xmlchange -file env_run.xml      SSTICE_GRID_FILENAME={sst_grid_file}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_DATA_FILENAME={sst_data_file}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_ALIGN=2020')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_START=2020')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_END=2020')
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
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
