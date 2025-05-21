#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC2/'

# clean        = True
newcase      = True
config       = True
build        = True
# submit       = True
# continue_run = True

debug_mode = False

# compset = 'I1850ELM'
# compset = 'FSCM-ARM97'
compset = 'FSCM-ARM97-MMF1'
# compset = 'FSCM-ARM97-MMF1-SAM'
# compset = 'FSCM-ARM97-MMF1-PAM'

# grid = '1x1_brazil'
ne,npg = 4,0; grid = f'ne{ne}_ne{ne}'

stop_opt,stop_n,resub = 'nstep',5,1

case_list = ['E3SM','TEST',grid,compset]
if debug_mode: case_list.append('debug')

case = '.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

atm_ntasks = 8

dtime = 20*60
if 'dtime' in locals(): ncpl = 86400/dtime

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
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}{case}'
   cmd += f' --machine macbook --compiler gnu --mpilib mpich '
   cmd += f'--compset {compset} --res {grid}'
   cmd += f' --pecount {atm_ntasks}x1'
   run_cmd(cmd)

   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')

   os.chdir(case_dir+case+'/')

   # specify the directories
   scratch_dir = os.getenv('HOME')+'/E3SM/scratch'
   input_dir = os.getenv('HOME')+'/E3SM/inputdata'
   run_cmd(f'./xmlchange EXEROOT=\'{scratch_dir}/{case}/bld\' ')
   run_cmd(f'./xmlchange RUNDIR=\'{scratch_dir}/{case}/run\' ')
   run_cmd(f'./xmlchange CIME_OUTPUT_ROOT=\'{scratch_dir}\' ')
   run_cmd(f'./xmlchange DIN_LOC_ROOT=\'{input_dir}\' ')
   
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   #    file.close()
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   run_cmd('./xmlchange PIO_VERSION=1')

   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   if 'ncpl' not in locals(): 
      (ncpl , err) = sp.Popen('./xmlquery ATM_NCPL -value', stdout=sp.PIPE, \
                              shell=True, universal_newlines=True).communicate()
      ncpl = float(ntasks_atm)
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   if stop_opt=='nstep':
      file.write(' nhtfrq    = 0,1 \n')
      file.write(' mfilt     = 1,72 \n')
   else:
      file.write(' nhtfrq    = 0,-1 \n')
      file.write(' mfilt     = 1,24 \n')
   # file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
   file.write('\n')
   file.write(" fincl2    = 'PS','PSL','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")
   file.write(             ",'TAUX','TAUY'")                       # surface stress
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(             ",'Z300:I','Z500:I'")
   # file.write(             ",'OMEGA850:I','OMEGA500:I'")
   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # if 'MMF' in compset: 
      # file.write(          ",'CRM_T','CRM_QV'")
      # file.write(          ",'CRM_T','CRM_W','CRM_U','CRM_QV','CRM_QC'")
      # file.write(          ",'MMF_DT','MMF_DQ','MMF_MCUP','MMF_MCDN'")

   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   file.write(" inithist = \'MONTHLY\' \n")
   
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()

   # if 'land_init_file' in locals():
   #    nfile = 'user_nl_elm'
   #    file = open(nfile,'w')
   #    file.write(f' finidat = \'{land_init_file}\' \n')
   #    file.close()

   # Turn off CICE history files
   # nfile = 'user_nl_cice'
   # file = open(nfile,'w') 
   # file.write(" histfreq = 'x','x','x','x','x' \n")
   # file.close()
         
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')

   # # special OSX/darwin stuff
   # run_cmd('./xmlchange --file env_run.xml --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 4 ')
   
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('time ./case.submit --no-batch ')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
