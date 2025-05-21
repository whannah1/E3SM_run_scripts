#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
ne,npg = 0,0
newcase,config,build,clean,submit,continue_run,copy_p3_data = False,False,False,False,False,False, False

acct = 'm3312_g'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'/E3SM_SRC4' # whannah/mmf/coriolis-test

# clean        = True
#newcase      = True
#config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 

### Compset
compset='F2010-MMF1'

arch = 'GNUGPU' # GNUGPU / GNUCPU


# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00' # quick test
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00' # 1-month test
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'5:00:00' # for 3D testing
# stop_opt,stop_n,resub,walltime = 'ndays',92,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'4:00:00' # for 2D runs


### set grid
ne=30; grid=f'ne30pg2_oECv3';  num_nodes=64
# ne=4; grid=f'ne4pg2_oQU480';  num_nodes=1

#-------------------------------------------------------------------------------
nx,ny=64,1
# nx,ny=32,32

# doXUcor=False ; doXWcor=False; doSUcor=False; doSWcor=False # control
### only explicit
# doXUcor=True  ; doXWcor=False; doSUcor=False; doSWcor=False # x
# doXUcor=False ; doXWcor=True ; doSUcor=False; doSWcor=False # x
doXUcor=True  ; doXWcor=True ; doSUcor=False; doSWcor=False # x
### only scalar
# doXUcor=False ; doXWcor=False; doSUcor=True ; doSWcor=False # x
# doXUcor=False ; doXWcor=False; doSUcor=False; doSWcor=True  # x
# doXUcor=False ; doXWcor=False; doSUcor=True ; doSWcor=True  # x
### mix of explicit and scalar
# doXUcor=True  ; doXWcor=True ; doSUcor=True ; doSWcor=False # 
# doXUcor=True  ; doXWcor=False; doSUcor=False; doSWcor=False # 
# doXUcor=True  ; doXWcor=False; doSUcor=True ; doSWcor=False # 
#-------------------------------------------------------------------------------

if doXWcor and doSWcor: raise ValueError("\nWhat do you think you're doing?!?!\n")

# case_list=['E3SM','2024-coriolis',arch,grid,compset]
# case_list=['E3SM','2024-coriolis-00',arch,grid,compset] # used wrong branch?
# case_list=['E3SM','2024-coriolis-01',arch,grid,compset]
# case_list=['E3SM','2024-coriolis-02',arch,grid,compset] # move coriolis call before SGS
# case_list=['E3SM','2024-coriolis-03',arch,grid,compset] # change fcorz formula to use cosine
# case_list=['E3SM','2024-coriolis-04',arch,grid,compset] # disable ESMT
case_list=['E3SM','2024-coriolis-05',arch,grid,compset] # use U perturbations in W tend
case_list.append(f'NXY_{nx}_{ny}')
case_list.append('XU-on' if doXUcor else 'XU-off')
case_list.append('XW-on' if doXWcor else 'XW-off')
case_list.append('SU-on' if doSUcor else 'SU-off')
case_list.append('SW-on' if doSWcor else 'SW-off')

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# print(case); exit()

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
if grid=='ne30pg2_oECv3':
   land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch'
   land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   land_data_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {nx} -crm_ny {ny} \" ')
   #-------------------------------------------------------
   cpp_opt = ''
   if doXUcor or doXWcor or doSUcor or doSWcor: cpp_opt += f' -DMMF_DO_CORIOLIS'
   if doXUcor: cpp_opt += f' -DMMF_DO_CORIOLIS_U'
   if doXWcor: cpp_opt += f' -DMMF_DO_CORIOLIS_W'
   if doSUcor: cpp_opt += f' -DMMF_DO_CORIOLIS_ESMT'
   if doSWcor: cpp_opt += f' -DMMF_DO_CORIOLIS_ESMT_W'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # ATM namelist
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-1,-1 \n')
   file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECSC'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TBOT','QBOT'")
   file.write('\n')
   # file.write(" fincl3 =  'PS','PSL'")
   # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   # if 'MMF' in compset:
   #    file.write(       ",'QRLC','QRSC'")
   #    file.write(       ",'CRM_QRL','CRM_QRLC'")
   #    file.write(       ",'CRM_U','CRM_W'")
   #    file.write(       ",'CRM_T','CRM_QV'")
   #    file.write(       ",'CRM_QC','CRM_QI'")
   #    file.write(       ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
   #    file.write(       ",'CRM_QRAD'")
   #    file.write(       ",'MMF_TLS','MMF_QTLS'")
   #    file.write(       ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
   #    file.write(       ",'MMF_QRL','MMF_QRS'")
   #    file.write(       ",'MMF_QV','MMF_QC','MMF_QI','MMF_QR'")
   #    if 'MMF1' in compset:
   #       file.write(    ",'MMF_QTLS'")
   #    if 'MMF2' in compset:
   #       file.write(    ",'MMF_NC','MMF_NI','MMF_NR'")
   #       file.write(    ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
   #       file.write(    ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
   #       file.write(    ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
   #       file.write(    ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
   #       # file.write(    ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
   #       file.write(    ",'MMF_LIQ_ICE','MMF_VAP_LIQ','MMF_VAP_ICE'")
   #    file.write('\n')

   file.write(f' mmf_orientation_angle = 0 \n') # E/W

   file.close()
   #-------------------------------------------------------
   # LND namelist
   if 'land_init_file' in locals() or 'land_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
