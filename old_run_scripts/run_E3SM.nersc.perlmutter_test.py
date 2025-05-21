#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm_g'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC1/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True


# ne,npg,num_nodes = 4,2,1

# ne,npg,num_nodes = 30,2,512
# ne,npg,num_nodes = 30,2,256
# ne,npg,num_nodes = 30,2,128
ne,npg,num_nodes = 30,2, 64
# ne,npg,num_nodes = 30,2, 32
# ne,npg,num_nodes = 30,2, 16
# ne,npg,num_nodes = 30,2, 8

compset,arch = 'F-MMFXX','GNUCPU'
# compset,arch = 'F-MMFXX','GNUGPU'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


stop_opt,stop_n,resub,walltime = 'ndays',10,0,'3:00:00'

if arch=='GNUCPU': atm_nthrds = 1
if arch=='GNUGPU': atm_nthrds = 8

# case='.'.join(['E3SM','PM_TEST',arch,grid,compset,f'NNODES_{num_nodes}',f'NTHRDS_{atm_nthrds}','00'])
case='.'.join(['E3SM','PM_TEST',arch,grid,compset,f'NNODES_{num_nodes}',f'NTHRDS_{atm_nthrds}','RADNX_16','00'])


# case = case+'.debug-on'
# case = case+'.checks-on'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch :
   max_mpi_per_node  = 64
   atm_nthrds        = 1
if 'GPU' in arch :
   max_mpi_per_node  = 4
   if 'atm_nthrds' not in locals():
      atm_nthrds        = 16

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
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   if os.path.isdir(f'{case_dir}/{case}'):
      exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
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
   # change run/bld scratch path
   #-------------------------------------------------------
   # scratch = '/pscratch/sd/w/whannah/e3sm_scratch/perlmutter/'
   # run_cmd(f'./xmlchange -file env_run.xml RUNDIR=\'{scratch}/$CASE/run\' ' )
   # run_cmd(f'./xmlchange -file env_run.xml EXEROOT=\'{scratch}/$CASE/bld\' ' )
   #-------------------------------------------------------
   # Copy this run script into the case directory
   #-------------------------------------------------------
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   script_path = os.getenv('HOME')+'/E3SM/'+os.path.realpath(__file__).split('/')[-1]
   run_cmd(f'cp {script_path} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')

   # if '.RRTMG.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmg \"')
   #-------------------------------------------------------
   # cpp_opt = ''
   # if 'debug-on' in case and 'MMFXX' in compset : cpp_opt += ' -DYAKL_DEBUG'
   # if cpp_opt != '' :
   #    cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
   #    cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
   #    run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads

   if 'atm_ntasks' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_ATM={atm_ntasks} ')
   if 'atm_nthrds' in locals(): run_cmd(f'./xmlchange -file env_mach_pes.xml NTHRDS_ATM={atm_nthrds} ')

   # if 'NTASKS' in case or 'NTHRDS' in case:
   #    params = [p.split('_') for p in case.split('.')]
   #    for p in params: 
   #       if p[0]=='NTASKS': run_cmd(f'./xmlchange -file env_mach_pes.xml NTASKS_ATM={p[1]} ')
   #       if p[0]=='NTHRDS': run_cmd(f'./xmlchange -file env_mach_pes.xml NTHRDS_ATM={p[1]} ')

   cmd = './xmlchange -file env_mach_pes.xml '
   alt_ntask = max_mpi_per_node*(num_nodes/2)
   cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   cmd = './xmlchange -file env_mach_pes.xml '
   if 'GPU' in arch :
      alt_nthrds = 8
      # if num_nodes>256: alt_nthrds = 1
   if 'CPU' in arch :
      alt_nthrds = 1
   cmd += f'NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTHRDS_GLC=1,NTHRDS_ESP=1,NTHRDS_IAC=1'
   run_cmd(cmd)

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
   run_cmd('./xmlchange DIN_LOC_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/perlmutter/inputdata ')
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   # (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
   #                                   stdout=sp.PIPE, shell=True).communicate()
   # (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
   #                                   stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   # if stop_opt=='nstep':
   #    file.write(' nhtfrq    = 0,1 \n')
   #    file.write(f' mfilt     = 1,{stop_n} \n')
   # else:
   #    file.write(' nhtfrq    = 0,-1,-24 \n')
   #    file.write(' mfilt     = 1,24,1 \n')
   # file.write(" fincl2    = 'PS','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   # file.write(             ",'T850','Q850'")
   # file.write(             ",'U200','U850'")
   # file.write(             ",'V200','V850'")

   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRS','QRL'")
   
   # file.write('\n')

   # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   file.write(" inithist = \'NONE\' \n")
   # file.write(" inithist = \'ENDOFRUN\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   if compset=='FC5AV1C-P': file.write(' use_hetfrz_classnuc = .false. \n')

   file.close() # close atm namelist file

   
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # disable restart files for better scaling estimate
   run_cmd(f'./xmlchange REST_OPTION=never')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
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
