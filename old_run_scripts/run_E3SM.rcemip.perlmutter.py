#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm_g'    # m3312 / m3305 / m1517 / e3sm_g

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC4/'

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

# ne,npg,num_nodes = 4,2,1
ne,npg,num_nodes = 30,2,128


# compset = 'F-EAMv1-RCEMIP'
# compset = 'F-MMFXX-RCEMIP'
compset,arch = 'F-EAM-RCEROT','GNUCPU'; num_nodes = 64
# compset,arch = 'F-EAM-RCEROT','GNUCPU'; num_nodes = 32
# compset,arch = 'F-MMFXX-RCEROT','GNUGPU'

# arch = 'GNUGPU'

# stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10:00'
# stop_opt,stop_n,resub,walltime = 'ndays',180,2*8,'3:00:00' 

stop_opt,stop_n,resub,walltime = 'ndays',365*2,4,'3:00:00' 



# Set grid string
res = 'ne'+str(ne) if npg==0 else 'ne'+str(ne)+'pg'+str(npg)

# # Retreive current git hash for case name
# git_hash = sp.check_output(f'cd {src_dir}; git log -n1 --format=format:"%H"',shell=True,universal_newlines=True)
# case = f'E3SM_{compset}_{res}_master-{git_hash[-6:]}'   # control

# case = '.'.join(['E3SM',arch,res,compset,'BVT','01']) # includes MSE budget terms

# case = '.'.join(['E3SM',arch,res,compset,'BVT',         '02']) # MSE budget terms + history file bug fix
# case = '.'.join(['E3SM',arch,res,compset,'BVT','FIX_LW','02']) # prescribed LW tendencies from control run
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_LW','02']) # homogenize LW tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','FIX_LW','NO_SW','02']) # prescribed LW tendencies from control - no SW
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRAD','02']) # homogenize LW+SW tendencies globally each step

# case = '.'.join(['E3SM',arch,res,compset,'BVT','RADNX_1','02']) # control w/ single rad column
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRT','02']) # homogenize LW+SW tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRS','02']) # homogenize SW    tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRL','02']) # homogenize LW    tendencies globally each step

# case = '.'.join(['E3SM',arch,res,compset,'BVT','RADNX_1','03']) # control w/ new alt CRM tendency variable
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRT','03']) # homogenize LW+SW tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRS','03']) # homogenize SW    tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRL','03']) # homogenize LW    tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','FIX_QRT','03']) # prescribed LW+SW tendencies globally each step


# case = '.'.join(['E3SM',arch,res,compset,                  '04']) # non-MMF control
# case = '.'.join(['E3SM',arch,res,compset,'GBL_QRT',        '04']) # non-MMF + homogenize LW+SW tendencies globally each step
case = '.'.join(['E3SM',arch,res,compset,'FIX_QRT',        '04']) # non-MMF + prescribed LW+SW tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'FIX_QRT',        '04a']) # test smaller node count (32)

# case = '.'.join(['E3SM',arch,res,compset,'BVT','RADNX_1','04']) # control w/ new alt CRM tendency variable
# case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRT','04']) # homogenize LW+SW tendencies globally each step
# case = '.'.join(['E3SM',arch,res,compset,'BVT','FIX_QRT','04']) # prescribed LW+SW tendencies globally each step

### cori cases for debugging
# arch='GNUCPU'; case = '.'.join(['E3SM',arch,res,compset,'BVT','RADNX_1','02a','CORI']) # control w/ single rad column
# arch='GNUCPU'; case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRT','02','CORI']) # homogenize LW+SW tendencies globally each step
# arch='GNUCPU'; case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRS','02','CORI']) # homogenize SW    tendencies globally each step
# arch='GNUCPU'; case = '.'.join(['E3SM',arch,res,compset,'BVT','GBL_QRL','02','CORI']) # homogenize LW    tendencies globally each step

if '.CORI' in case:
   # stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
   stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:30:00'
   queue = 'debug'
   acct = 'm3312'

# case = case+'_debug-on'
# case = case+'_checks-on'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6
# dtime = 20*60           # use 20 min for SP (default is 30 min for E3SM @ ne30)
dtime = 10*60
# if ne==120: dtime = 5*60
# ncpl  = 86400 / dtime

if arch=='GNUCPU': atm_nthrds = 1
if arch=='GNUGPU': atm_nthrds = 8

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
   grid = res+'_'+res
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
   # Add special MMF options based on case name
   #-------------------------------------------------------
   cpp_opt = ''
   if '.FLUX-BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS '
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'

   if '.GBL_QR'  in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad 1 \" ')
   if '.FIX_QR'  in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad 1 \" ')

   if '.GBL_QRT' in case: cpp_opt += ' -DMMF_GLOBAL_QRT '
   if '.GBL_QRS' in case: cpp_opt += ' -DMMF_GLOBAL_QRS '
   if '.GBL_QRL' in case: cpp_opt += ' -DMMF_GLOBAL_QRL '

   if '.FIX_QRT' in case: cpp_opt += ' -DMMF_PRESCRIBED_QRS -DMMF_PRESCRIBED_QRL '
   if '.FIX_QRS' in case: cpp_opt += ' -DMMF_PRESCRIBED_QRS '
   if '.FIX_QRL' in case: cpp_opt += ' -DMMF_PRESCRIBED_QRL '
   
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   # CRM variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)

   # Explicitly adjust CRM or rad cols when requested
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
   #-------------------------------------------------------
   # 64_data format is needed for large output files
   #-------------------------------------------------------
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   #-------------------------------------------------------
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
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, \
                                     universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if '.CORI' in case:
      file.write(' nhtfrq    = 0,-3,-3 \n')
      file.write(' mfilt     = 1,8,8 \n')
   else:
      file.write(' nhtfrq    = 0,-3,-24 \n')
      file.write(' mfilt     = 1,8,1 \n')
   file.write('\n')
   file.write(" fincl1    = 'Z3'") # this is for easier use of height axis on profile plots
   if 'MMF' in compset:
      file.write(           ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
      file.write(           ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
      file.write(           ",'DDSE_CRM','DQLV_CRM'") # 
      file.write(           ",'DDSE_QRS','DDSE_QRL'") # 
      file.write(           ",'DDSE_CEF','DQLV_CEF'") # 
      file.write(           ",'DDSE_PBL','DQLV_PBL'") # 
      file.write(           ",'DDSE_GWD'")            #  
   else:
      file.write(          ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
      file.write(          ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
      file.write(          ",'DDSE_CLD','DQLV_CLD'") # convection schemes
      file.write(          ",'DDSE_QRS','DDSE_QRL'") # 
      file.write(          ",'DDSE_CEF','DQLV_CEF'") # 
      file.write(          ",'DDSE_GWD'")            # 
   file.write('\n')

   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'TBOT','QBOT'")
   file.write(             ",'UBOT','VBOT'")
   file.write(             ",'U200','V200'")
   file.write(             ",'U850','V850'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liquid and ice water paths
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write('\n')
   
   file.write(" fincl3    = 'PS','T','Q','Z3'")            # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   if 'MMF' in compset:
      file.write(          ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
      file.write(          ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
      file.write(          ",'DDSE_CRM','DQLV_CRM'") # 
      file.write(          ",'DDSE_QRS','DDSE_QRL'") # 
      file.write(          ",'DDSE_CEF','DQLV_CEF'") # 
      file.write(          ",'DDSE_PBL','DQLV_PBL'") # 
      file.write(          ",'DDSE_GWD'")            # 
      file.write(          ",'DDSE_CRM_ALT','DQLV_CRM_ALT'") 
   else:
      file.write(          ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
      file.write(          ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
      file.write(          ",'DDSE_CLD','DQLV_CLD'") # convection schemes
      file.write(          ",'DDSE_QRS','DDSE_QRL'") # 
      file.write(          ",'DDSE_CEF','DQLV_CEF'") # 
      file.write(          ",'DDSE_GWD'")            # 
   if '.CORI' in case:
      file.write(          ",'QRS','QRL'") # 
   file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   # file.write(' use_crm_accel = .false. \n')

   # file.write(" inithist = \'MONTHLY\' \n")
   # file.write(' inithist = \'ENDOFRUN\' \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   file.close()
         
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # def xml_check_and_set(file_name,var_name,value):
   #    if var_name in open(file_name).read(): 
   #       run_cmd('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )
   
   # xml_check_and_set('env_workflow.xml','JOB_WALLCLOCK_TIME',     walltime)
   # xml_check_and_set('env_batch.xml',   'USER_REQUESTED_WALLTIME',walltime)
   
   # xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   # xml_check_and_set('env_workflow.xml','PROJECT',acct)

   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')

   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Done!
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') # Print the case name again
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
