#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # whannah/mmf/test-scaled-dx

print_commands_only = False

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

ne,npg,rad_nx    = 0,2,4
use_vt,use_momfb = False,False
# nlev,crm_nz      = 60,50


crm_nx,crm_ny = 32,1; arch,num_nodes,stop_opt,stop_n,resub,walltime = 'GNUGPU',128,'nday',15,1,'1:00'  # for testing
# crm_nx,crm_ny = 32,32; arch,num_nodes,stop_opt,stop_n,resub,walltime = 'GNUGPU',1000,'nday',1,0,'2:00'


grid,grid_name = 'ne0_cubeface_grad_ne30x3pg2','ne30x3pg2'
# grid,grid_name = 'ne0_cubeface_grad_ne4x6pg2','ne4x6pg2'
# grid,grid_name = 'ne0_cubeface_grad_ne4x5pg2','ne4x5pg2'

compset = 'F-MMFXX-AQP1'

# use_dx_scaling, dx_scale, crm_dx, crm_dt = False,     0,2000,10
use_dx_scaling, dx_scale, crm_dx, crm_dt = False,     0, 200, 2
# use_dx_scaling, dx_scale, crm_dx, crm_dt = True,'12e-3', 200, 2

# crm_dx,crm_dt = 2e3,10; case='.'.join(['E3SM','AQUA-RRM-TEST',compset,f'CRMDX_{crm_dx}','00']) # control
# crm_dx,crm_dt = 2e2,2;  case='.'.join(['E3SM','AQUA-RRM-TEST',compset,f'CRMDX_{crm_dx}','00']) # control
# crm_dx,crm_dt = 2e2,2;  case='.'.join(['E3SM','AQUA-RRM-TEST',compset,f'DXSCL_{crm_dx}','00']) # scale crm_dx by DXSCL

case_list = ['E3SM','AQUA-RRM-TEST',compset,grid_name]

if 'MMF' in compset:
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   if use_dx_scaling: 
      case_list.append(f'DXSCL_{dx_scale}')
   else:
      case_list.append(f'CRMDX_{crm_dx}')  
   if use_vt        : case_list.append('BVT')
   if use_momfb     : case_list.append('MOMFB')
      

case_list.append('00') # initial tests

case='.'.join(case_list)

# case = case+'.debug-on'
# case = case+'.checks-on'

### specify atmos initial condition file
hiccup_scratch = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'
init_file_atm = f'{hiccup_scratch}/eam_i_aqua_RRM-cubeface-grad_L60_c20210907.nc'


# Impose wall limits for Summit
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# if 'AQUA-RRM-TEST' in case: dtime = 5*60
if 'AQUA-RRM-TEST' in case: dtime = 2*60+30

# if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

max_task_per_node = 42
if 'CPU' in arch :
   max_mpi_per_node  = 42
   atm_nthrds        = 1
if 'GPU' in arch :
   max_mpi_per_node  = 6
   atm_nthrds        = 7

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

   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + ' -compset '+compset+' -res '+grid
   cmd = cmd + ' -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
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
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: 
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

      params = [p.split('_') for p in case.split('.')]
      for p in params: 
         if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
         if p[0]=='DXSCL': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx 200 -crm_dx_scale {p[1]} \" ')

      # params = [p.split('_') for p in case.split('.')]
      # for p in params:
      #    if p[0]=='L': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} -crm_nz {p[2]} \" ')

      # if 'nlev'   in locals(): run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {nlev} \" ')
      # if 'crm_nz' in locals(): run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {crm_nz} \" ')

   # else:
   #    # non-MMF
   #    params = [p.split('_') for p in case.split('.')]
   #    for p in params:
   #       if p[0]=='L': 
   #          if p[1]!=72: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} \" ')

   

   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if 'debug-on' in case: cpp_opt += ' -DYAKL_DEBUG'

   # if 'DXSCL' in case: cpp_opt += ' -DSCALE_CRM_DX '

   if  crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if  crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   # if ne==30: alt_ntask = 1200
   # alt_ntask = atm_ntasks
   alt_ntask = 120
   cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   alt_ntask = task_per_node
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   ### don't use threads
   # nthrds = 2
   # cmd = f'./xmlchange -file env_mach_pes.xml '
   # cmd += f'NTHRDS_CPL={nthrds},NTHRDS_CPL={nthrds},'
   # cmd += f'NTHRDS_OCN={nthrds},NTHRDS_ICE={nthrds}'
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
      file.write(' nhtfrq = 0,-3,-24 \n')
      file.write(' mfilt  = 1, 8,1 \n')
      file.write(" fincl2 = 'PS','TS'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")
      file.write(          ",'TAUX','TAUY'")               # surface stress

      file.write(          ",'UBOT','VBOT'")
      file.write(          ",'TBOT','QBOT'")
      file.write(          ",'U200','U850'")
      file.write(          ",'V200','V850'")

      # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
      # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles

      # file.write(          ",'TOT_DU','TOT_DV'")          # total momentum tendencies
      # file.write(          ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
      # file.write(          ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
      # file.write(          ",'DUV','DVV'")                # 3D PBL tendencies
      # # file.write(          ",'RAY_DU','RAY_DV'")          # 3D Rayleigh friction tendencies
      # if 'MMF' in compset:
      #    if use_momfb: file.write(",'MMF_DU','MMF_DV'")
      #    # file.write(       ",'MMF_DT','MMF_DQ'")           # CRM heating/moistening tendencies
      #    # file.write(       ",'MMF_TLS','MMF_QTLS' ")       # CRM large-scale forcing

      file.write('\n')

      # file.write(" fincl3 =  'T','Q','Z3' ")               # 3D thermodynamic budget components
      # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
      # file.write(          ",'TOT_DU','TOT_DV'")          # total momentum tendencies
      # file.write(          ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
      # file.write(          ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
      # file.write(          ",'DUV','DVV'")                # 3D PBL tendencies
      # if 'MMF' in compset and use_momfb: file.write(",'MMF_DU','MMF_DV'")
      # file.write('\n')

      #------------------------------
      # Other namelist stuff
      #------------------------------

      # limit dynamics tasks
      # if num_dyn<atm_ntasks: 
      #    if num_nodes==1013 and ne==45:
      #       ntask_dyn = 500*task_per_node
      #       file.write(f' dyn_npes = {ntask_dyn} \n')
      #    else:
      #       file.write(f' dyn_npes = {num_dyn} \n')

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      if 'dtime' in locals():
         if dtime == 5*60 :
            file.write(f'dt_tracer_factor = 5 \n')
            # file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 60 \n')
         if dtime == 2*60+30:
            file.write(f'dt_tracer_factor = 5 \n')
            # file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 30 \n')

      if 'init_file_atm' in locals():
         file.write(f' ncdata = \'{init_file_atm}\'\n')

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
