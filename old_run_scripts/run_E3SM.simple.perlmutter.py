#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm_g'    # m3312 / m3305 / m1517 / e3sm_g

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC1/'

print_commands_only = False

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

### rainfall runoff experiments
# compset,arch,num_nodes,use_momfb,use_vt,no_runoff,max_infil,no_pond = 'F-MMFXX','GNUGPU',128,True,True,False,False,False
# compset,arch,num_nodes,use_momfb,use_vt,no_runoff,max_infil,no_pond = 'F-MMFXX','GNUGPU',128,True,True, True,False,False
compset,arch,num_nodes,use_momfb,use_vt,no_runoff,max_infil,no_pond = 'F-MMFXX','GNUGPU',128,True,True, True, True, True


stop_opt,stop_n,resub,walltime = 'ndays',365,3,'4:00:00'

ne,npg = 30,2
res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_r05_oECv3'


case_list = ['E3SM','RUNOFF-TEST',arch,grid,compset]

if 'MMF' in compset:
   # case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   if use_momfb: case_list.append('MOMFB')
   if use_vt   : case_list.append('BVT')
   if no_runoff: case_list.append('NO-RUNOFF')
   if max_infil: case_list.append('MAX-INFIL')
   if no_pond  : case_list.append('NO-POND')
case_list.append('00')

case='.'.join(case_list)

# case = case+'.debug-on'
# case = case+'.checks-on'

### specify land initial condition file
land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch'
land_init_file = f'ELM_spinup.ICRUELM.ne{ne}pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60
# if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
atm_ntasks = max_mpi_per_node*num_nodes

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
   #-------------------------------------------------------
   # Check if directory already exists
   #-------------------------------------------------------
   if not print_commands_only:
      if os.path.isdir(case_dir+case): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)
   #-------------------------------------------------------
   # run create_newcase
   #------------------------------------------------------- 
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += f' -compset {compset} -res {grid} '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # set tasks per node
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}')
   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val 64 ') # not needed
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
   #-------------------------------------------------------
   # Copy this run script into the case directory
   #-------------------------------------------------------
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   script_path = os.getenv('HOME')+'/E3SM/'+os.path.realpath(__file__).split('/')[-1]
   run_cmd(f'cp {script_path} {case_dir}/{case}/run_script.{timestamp}.py')
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
   if 'MMF' in compset and use_vt:
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if no_runoff: cpp_opt += ' -DNORUNOFF'
   if max_infil: cpp_opt += ' -DMAXSOILINFILTRATION'
   if no_pond  : cpp_opt += ' -DDISABLEPOND'

   if use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   # if  crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   # if  crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # # Set tasks for all components
   # cmd = './xmlchange -file env_mach_pes.xml '
   # # if ne==30: alt_ntask = 1200
   # alt_ntask = atm_ntasks
   # cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   # alt_ntask = task_per_node
   # cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   # cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   # run_cmd(cmd)
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
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      run_cmd('./xmlchange DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata ')
      
      #-------------------------------------------------------
      # Query some stuff about the case
      #-------------------------------------------------------
      # (ncpl        ,err) = sp.Popen('./xmlquery ATM_NCPL        -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      # (din_loc_root,err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      # (config_opts ,err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      # file.write(' nhtfrq    = 0,-3,-24 \n')
      # file.write(' mfilt     = 1,8,1 \n')
      file.write(' nhtfrq    = 0,-3 \n')
      file.write(' mfilt     = 1,8 \n')
      file.write(" fincl1    = 'Z3'") # this is for easier use of height axis on profile plots
      file.write(            ",'PTTEND','PTEQ'")
      file.write(            ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write('\n')
      file.write(" fincl2    = 'PS','TS','PSL'")
      file.write(            ",'PRECT:A','PRECT:I','TMQ'")
      file.write(            ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(            ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
      file.write(            ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(            ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(            ",'TGCLDLWP','TGCLDIWP'")    
      file.write(            ",'TUQ','TVQ'")                 # total zonal/meridional water flux
      # file.write(            ",'TAUX','TAUY'")               # surface stress
      # file.write(            ",'TREFHT','QREFHT','QFLX'")    # Reference height T/q
      # instantaneous variables for hurricane tracking 
      file.write(            ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'")
      file.write(            ",'T900:I','Q900:I','U900:I','V900:I'")
      file.write(            ",'T850:I','Q850:I','U850:I','V850:I'")
      # file.write(            ",'T700:I','Q700:I','U700:I','V700:I'")
      file.write(            ",'OMEGA850:I','OMEGA500:I'")
      file.write(            ",'Z300:I','Z500:I'")
      file.write('\n')

      # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
      # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(             ",'PTTEND','PTEQ'")
      # file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------
      # # limit dynamics tasks
      # if num_dyn<atm_ntasks: file.write(f' dyn_npes = {num_dyn} \n')

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      if 'atm_init_file' in locals():
         file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')

      file.close()
      
   #-------------------------------------------------------
   # ELM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      if 'land_init_file' in locals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
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
