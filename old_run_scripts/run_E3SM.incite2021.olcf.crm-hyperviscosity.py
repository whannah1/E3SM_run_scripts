#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/'

print_commands_only = False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

ne,npg = 45,2
res = f'ne{ne}' if npg==0 else f'ne{ne}pg{npg}'
grid = f'{res}_r05_oECv3'


stop_opt,stop_n,resub,walltime = 'ndays',10,0,'3:00'


# crm_nx,crm_ny,crm_dx,gcm_nz,crm_nz,use_vt,use_momfb,use_crmhv,num_nodes = 512,1,100,125,120,True,False,False,1000
# crm_nx,crm_ny,crm_dx,gcm_nz,crm_nz,use_vt,use_momfb,use_crmhv,num_nodes = 512,1,100,125,120,True,False,True, 1000
# crm_nx,crm_ny,crm_dx,gcm_nz,crm_nz,use_vt,use_momfb,use_crmhv,num_nodes = 512,1,100,60,50,  True,False,False,1000
# crm_nx,crm_ny,crm_dx,gcm_nz,crm_nz,use_vt,use_momfb,use_crmhv,num_nodes = 512,1,100,60,50,  True,False,True, 1000

crm_nx,crm_ny,crm_dx,gcm_nz,crm_nz,use_vt,use_momfb,use_crmhv,num_nodes = 64,1,2000,60,50,  True,False,False, 128


compset = 'F-MMFXX'
arch    = 'GNUGPU'
rad_nx  = 4 

if crm_dx== 100: crm_dt=1


case_list = ['E3SM','INCITE2021-CRMHV',arch,grid,compset]

iyr,imn,idy = 2008,10,1
init_date = f'{iyr}-{imn:02d}-{idy:02d}'

if 'MMF' in compset:
   case_list.append(f'L{gcm_nz}')
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   case_list.append(f'CRMDX_{crm_dx}')
   # case_list.append(f'CRMDT_{crm_dt}')
   # case_list.append(f'NXRAD_{rad_nx}')
   if use_vt   : case_list.append('BVT')
   if use_momfb: case_list.append('MOMFB')
   if use_crmhv: case_list.append('CRMHV')
   
### version number
case_list.append('00') # initial runs


case = '.'.join(case_list)


# case = case+'.debug-on'
# case = case+'.checks-on'

### specify atmos and land initial condition file
atm_init_path = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'
lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
sst_init_file = f'HICCUP.sst_noaa.{init_date}.c20210625.nc'
atm_init_file = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L{gcm_nz}.c20210625.nc'
if ne==45: lnd_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
# Impose wall limits for Summit
#---------------------------------------------------------------------------------------------------
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60
if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes


#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   if print_commands_only: 
      print(f'{msg}')
   else:
      print(f'\n{msg}')
      if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   # Check if directory already exists
   if not print_commands_only:
      if os.path.isdir(case_dir+case): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid} -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='IBMGPU' : cmd += f' -compiler ibmgpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'atm_init_file' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      if 'crm_dt' in locals(): run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} \" ')
      if 'gcm_nz' in locals(): run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {gcm_nz} -crm_nz {crm_nz}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: 
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if  crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if  crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if  use_crmhv: cpp_opt += ' -DMMF_HYPERVISCOSITY'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   if num_nodes>1:
      cmd = './xmlchange -file env_mach_pes.xml '
      # if ne==30: alt_ntask = 1200
      # alt_ntask = atm_ntasks
      alt_ntask = 120
      cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = task_per_node
      cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      run_cmd(cmd)

   run_cmd('./xmlchange -file env_mach_pes.xml NTASKS_ESP=1,NTASKS_IAC=1')

   #-------------------------------------------------------
   # 64_data format is needed for large numbers of columns (GCM or CRM)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      # Change inputdata from default due to permissions issue
      # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
      run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
      
      #-------------------------------------------------------
      # First query some stuff about the case
      #-------------------------------------------------------
      (ncpl        ,err) = sp.Popen('./xmlquery ATM_NCPL        -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (din_loc_root,err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (config_opts ,err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      file.write(' nhtfrq = 0,-1 \n')
      file.write(' mfilt  = 1,24 \n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")
      file.write(          ",'TAUX','TAUY'")               # surface stress

      # file.write(          ",'UBOT','VBOT','TBOT','QBOT'")
      # file.write(          ",'U200','V200'")
      # file.write(          ",'U700','V700','T700','Q700'")
      # file.write(          ",'U850','V850'")
      
      file.write(          ",'T','Q','Z3'")                # 3D thermodynamic budget components
      file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(          ",'QRL','QRS'")                 # 3D radiative heating 
      file.write(          ",'QRLC','QRSC'")               # 3D clearsky radiative heating 

      file.write(          ",'PTTEND','PTEQ'")             # 3D physics tendencies
      # file.write(          ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   
      if 'use_MMF' in config_opts :
         file.write(       ",'MMF_DT','MMF_DQ'")
         file.write(       ",'MMF_TK','MMF_TKE','MMF_TKES','MMF_TKEW'")
         file.write(       ",'MMF_PFLX','MMF_QTFLX'") # note MMF_TVFLUX is all zeros            

      file.write('\n')

      #------------------------------
      # Other namelist stuff
      #------------------------------
      ntask_dyn = int( num_dyn / atm_nthrds )
      file.write(f' dyn_npes = {ntask_dyn} \n')

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      if 'atm_init_file' in locals():
         file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')

      file.close()

      #-------------------------------------------------------
      # ELM namelist
      #-------------------------------------------------------
      if 'land_init_file' in locals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
         file.close()

      #-------------------------------------------------------
      # Set SST stuff for hindcast mode
      #-------------------------------------------------------
      os.system(f'./xmlchange -file env_run.xml      RUN_STARTDATE={init_date}')
      os.system(f'./xmlchange -file env_run.xml      SSTICE_DATA_FILENAME={atm_init_path}/{sst_init_file}')
      os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_ALIGN={iyr}')
      os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_START={iyr}')
      os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_END={iyr+1}')
      # os.system('./xmlchange -file env_build.xml    CALENDAR=GREGORIAN)

   #-------------------------------------------------------
   # CLM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      if 'lnd_init_file' in locals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
         file.close()
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
