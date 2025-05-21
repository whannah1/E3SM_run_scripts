#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp#, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli145'

case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/'

print_commands_only = False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

compset = 'F-MMFXX'



ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',5,0,'0:30'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime =  4,2,'GNUCPU',2,'ndays',1,0,'0:30'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime =  4,2,'GNUGPU',2,'ndays',1,0,'0:30'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'
   

# case = '.'.join(['E3SM','ESMT-TEST',arch,grid,compset,'00'])
case = '.'.join(['E3SM','ESMT-TEST',arch,grid,compset,'ESMT','00'])
# case = '.'.join(['E3SM','ESMT-TEST',arch,grid,compset,'ESMT-alt','00'])

# case = case+'.debug-on'
# case = case+'.checks-on'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

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
      if os.path.isdir(f'{case_dir}/{case}'): 
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
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      # file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # # explicitly specify rad option
   # if '.RRTMG.'    in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmg \"')
   # if '.RRTMGP.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
   # if '.RRTMGPXX.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp -rrtmgpxx \"')

   run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   # params = [p.split('_') for p in case.split('.')]
   # for p in params: 
   #    if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
   #    if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
   #    if p[0]=='CRMNY': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_ny {p[1]} \" ')
   #    if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
   #    if p[0]=='CRMNZ': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {p[1]} \" ')
   #    if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''

   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if '.ESMT.' in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if '.ESMT-alt.' in case: cpp_opt += ' -DMMF_ESMT '
   
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -cppdefs \'{cpp_opt} \'  \" '
      run_cmd(cmd)
   
   #-------------------------------------------------------
   # Set tasks and threads

   # # Set tasks for all components
   # cmd = './xmlchange -file env_mach_pes.xml '
   # # if ne==30: alt_ntask = 1200
   # # alt_ntask = atm_ntasks
   # alt_ntask = 600
   # cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   # alt_ntask = 675
   # cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # alt_ntask = max_mpi_per_node
   # cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   # cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   # run_cmd(cmd)
   

   # cmd = './xmlchange -file env_mach_pes.xml '
   # # cmd += f' NTASKS_ATM={atm_ntasks}'
   # # alt_ntask = task_per_node*np.ceil(ne/4)
   # if ne==4 : alt_ntask = task_per_node
   # if 'GPU' in arch:
   #    if ne==0  and num_nodes== 64: alt_ntask = 256
   #    if ne==0  and num_nodes==128: alt_ntask = 256
   #    if ne==30 and num_nodes== 64: alt_ntask = 256
   #    if ne==30 and num_nodes== 96: alt_ntask = 576
   #    if ne==30 and num_nodes==128: alt_ntask = 720
   # if 'CPU' in arch:
   #    if ne==30 and num_nodes== 64: alt_ntask = 1200
   #    if ne==30 and num_nodes==128: alt_ntask = 1200
   # cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   # cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   # alt_ntask = task_per_node
   # cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   # cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   # run_cmd(cmd)


   # cmd = './xmlchange -file env_mach_pes.xml '
   # if 'GPU' in arch: alt_nthrds = 7
   # if 'CPU' in arch: alt_nthrds = 1
   # cmd += f'NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   # cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   # cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTHRDS_GLC=1,NTHRDS_ESP=1,NTHRDS_IAC=1'
   # run_cmd(cmd)

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
   if 'ncpl' in locals(): 
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)},LND_NCPL={str(ncpl)},ICE_NCPL={str(ncpl)},OCN_NCPL={str(ncpl)}')
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
      if stop_opt=='nsteps' or stop_opt=='nstep' :
         file.write(' nhtfrq    = 0,1 \n') 
         file.write(' mfilt     = 1,'+str(stop_n)+' \n')
      else:
         file.write(' nhtfrq    = 0,-3 \n')
         file.write(' mfilt     = 1, 8 \n')
      file.write('\n')
      file.write(" fincl2    = 'PS','TS'")
      file.write(             ",'PRECT','TMQ'")
      file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
      file.write(             ",'TGCLDLWP','TGCLDIWP'")       # cloud water path
      # file.write(             ",'TGPRCLWP','TGPRCIWP'")       # precipitating water path
      # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
      # file.write(             ",'TAUX','TAUY'")               # surface stress
      # file.write(             ",'UBOT','VBOT'")
      # file.write(             ",'TBOT','QBOT'")
      # file.write(             ",'OMEGA850','OMEGA500'")
      # file.write(             ",'T500','T850','Q850'")
      # file.write(             ",'U200','U850'")
      # file.write(             ",'V200','V850'")

      # file.write(          ",'T','Q','Z3' ")              # 3D thermodynamic budget components
      # file.write(          ",'U','V','OMEGA'")            # 3D velocity components
      # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")  # 3D cloud fields
      # file.write(          ",'QRL','QRS'")                # 3D radiative heating profiles

      # file.write(          ",'TOT_DU','TOT_DV'")          # total momentum tendencies
      # file.write(          ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
      # file.write(          ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
      # file.write(          ",'DUV','DVV'")                # 3D PBL tendencies
      # if 'MMF' in compset: 
      #    file.write(       ",'MMF_DU','MMF_DV'")

      file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------
      # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')

      if num_dyn>0 and num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

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
