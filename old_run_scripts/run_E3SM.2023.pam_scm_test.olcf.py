#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/mmf/pam-impl

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # batch / debug 
arch = 'GNUGPU' # GNUCPU / GNUGPU

if queue=='debug': stop_opt,stop_n,resub,walltime = 'nstep',10, 0,'0:30'
if queue=='batch': stop_opt,stop_n,resub,walltime = 'nstep',10, 0,'0:30'
# if queue=='batch': stop_opt,stop_n,resub,walltime = 'ndays',10,0,'2:00'
# if queue=='batch': stop_opt,stop_n,resub,walltime = 'ndays',28,0,'2:00'

# compset='FSCM-ARM97-MMF1'
compset='FSCM-ARM97-MMF2'
# compset='FSCM-ARM97-MMF2-AWFL'

ne,npg,grid = 30,2,'ne30pg2_EC30to60E2r2'; num_nodes = 32
# ne,npg,grid = 4,2,'ne4pg2_ne4pg2'; num_nodes = 1
if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';              num_nodes=1


# case = '.'.join(['E3SM','2023-PAM-SCM-01',grid,compset])
# crm_nx=512; case = '.'.join(['E3SM','2023-PAM-SCM-01',grid,compset,f'NX_{crm_nx:02d}'])
# case = '.'.join(['E3SM','2023-PAM-SCM-02',grid,compset]) # test new forcing approach - Sept 22, 2023
# crm_dt=10; case = '.'.join(['E3SM','2023-PAM-SCM-02',grid,compset,f'CDT_{crm_dt:02d}']) 
# case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset]) # updated test new forcing- Sept 23, 2023
# crm_nx,crm_dx,crm_dt=256,100,1; case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,f'NX_{crm_nx:02d}',f'DX_{crm_dx:02d}',f'CDT_{crm_dt:02d}'])
# crm_nx,crm_dx,crm_dt=1024,100,1; case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,f'NX_{crm_nx:02d}',f'DX_{crm_dx:02d}',f'CDT_{crm_dt:02d}'])
# crm_nx=16; case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,f'NX_{crm_nx:02d}'])
# crm_nx=512; case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,f'NX_{crm_nx:02d}'])
# crm_dt=1;  case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,f'CDT_{crm_dt:02d}'])
# case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,'NO-MSA'])
# case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset,'HD']) # test added hyperdiffusion

# case = '.'.join(['E3SM','2023-PAM-SCM-04',grid,compset]) # change how forcing output is computed and compare QTLS vs DT 
# case = '.'.join(['E3SM','2023-PAM-SCM-05',grid,compset]) # retry forcing the unadjusted temperature - BAD IDEA

# case = '.'.join(['E3SM','2023-PAM-SCM-06',grid,compset]) # fix hyperdiffusion with shorter timescale (10s) AND force separate water species
# case = '.'.join(['E3SM','2023-PAM-SCM-06',grid,compset,'NO-HD']) # disable HD - force separate water species
# case = '.'.join(['E3SM','2023-PAM-SCM-06',grid,compset,'HD'])
# case = '.'.join(['E3SM','2023-PAM-SCM-07',grid,compset]) # continuosly update anelastic reference state - no hyperdiffusion
# case = '.'.join(['E3SM','2023-PAM-SCM-08',grid,compset]) # disable dry density save/recall - also revisit AWFL
# case = '.'.join(['E3SM','2023-PAM-SCM-09',grid,compset]) # set rain frac to zero 
# case = '.'.join(['E3SM','2023-PAM-SCM-10',grid,compset]) # set ice frac to zero 
# case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset]) # change dycor conversions of temperature
# case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset,'HD']) # 11 + hyperdiffusion
# case = '.'.join(['E3SM','2023-PAM-SCM-12',grid,compset,'HD']) # 11 + move HD to happen after SHOC
# case = '.'.join(['E3SM','2023-PAM-SCM-13',grid,compset,'HD']) # 12 + switch back to total water forcing

# double check if we can increase the time step...
# crm_dt= 5; case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset,'HD',f'CDT_{crm_dt:02d}']) 
# crm_dt= 8; case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset,'HD',f'CDT_{crm_dt:02d}']) 
# crm_dt=10; case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset,'HD',f'CDT_{crm_dt:02d}'])
# crm_dt= 8; crm_dpp=4; case = '.'.join(['E3SM','2023-PAM-SCM-11',grid,compset,'HD',f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']) 

# Oct 23 => whannah/mmf/pam-variance-transport


# crm_dt= 5; pam_hdt=   10; case = '.'.join(['E3SM','2023-PAM-SCM-14',grid,compset,f'CDT_{crm_dt:02d}',f'HDT_{pam_hdt:04d}']) 
# crm_dt= 5; pam_hdt= 1*60; case = '.'.join(['E3SM','2023-PAM-SCM-14',grid,compset,f'CDT_{crm_dt:02d}',f'HDT_{pam_hdt:04d}']) 
# crm_dt= 5; pam_hdt= 5*60; case = '.'.join(['E3SM','2023-PAM-SCM-14',grid,compset,f'CDT_{crm_dt:02d}',f'HDT_{pam_hdt:04d}']) 
# crm_dt= 5; pam_hdt=15*60; case = '.'.join(['E3SM','2023-PAM-SCM-14',grid,compset,f'CDT_{crm_dt:02d}',f'HDT_{pam_hdt:04d}']) 

# case = '.'.join(['E3SM','2023-PAM-SCM-15',grid,compset]) # sanity check for new tests that seem to always fail....
case = '.'.join(['E3SM','2023-PAM-SCM-16',grid,compset]) # another sanity check using current master @ Oct 31 

if debug_mode: case += '.debug'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# SCM defaults to NCPL=12 (2 hour time step) - switch back to MMF default 
# if 'MMF' in compset and 'dtime' not in locals():
if 'FSCM' in compset and 'MMF' in compset:
   dtime = 20*60; ncpl = 86400/dtime


# if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
# if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
# if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,1 ; max_task_per_node = 4
# if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   32,1 ; max_task_per_node = 32
if 'FSCM' in compset: max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
atm_ntasks = max_mpi_per_node*num_nodes

# if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
# if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
case_root = f'{case_dir}/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case_root}'
   # cmd += f' --output-root {case_root} '
   # cmd += f' --script-root {case_root} '
   # cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}')
#---------------------------------------------------------------------------------------------------
if config :
   # run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   # run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
   run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   if 'crm_dt' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
   if 'crm_dx' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx} \" ')
   if 'crm_nx' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} \" ')
   # if '.PD-A' in case:run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -pam_dycor awfl \" ')
   # file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
   # nlev=60;crm_nz=50
   # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
   # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
   if '.PD-A' in case:run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -pam_dycor awfl \" ')
   #-------------------------------------------------------
   cpp_opt = ''
   if 'crm_dpp' in locals(): cpp_opt += f' -DMMF_PAM_DPP={crm_dpp}'
   if 'pam_hdt' in locals(): cpp_opt += f' -DMMF_PAM_HDT={pam_hdt}'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   # file.write(' nhtfrq    = 0,-1 \n')
   # file.write(' mfilt     = 1,24 \n')
   file.write(' nhtfrq    = 0,1,1 \n')
   file.write(' mfilt     = 1,72,72 \n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECL','PRECSC'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # variables for tracking stuff like hurricanes
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I'")
   file.write(          ",'OMEGA850:I','OMEGA500:I'")
   file.write(          ",'U200:I','V200:I'")
   file.write('\n')
   if 'FSCM' in compset: 
      # 3D variables
      file.write(" fincl3 = 'PS','TS','PSL'")
      file.write(          ",'T','Q','Z3'")                       # 3D thermodynamic budget components
      file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
      file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
      file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
      file.write(          ",'QRLC','QRSC'")
      file.write(          ",'CRM_QRL','CRM_QRLC'")
      file.write(          ",'CRM_U','CRM_W'")
      file.write(          ",'CRM_T','CRM_QV'")
      file.write(          ",'CRM_QC','CRM_QI'")
      # file.write(          ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
      # file.write(          ",'CRM_QRAD'")
      # file.write(          ",'MMF_TLS','MMF_QTLS'")
      # # file.write(          ",'VDQ'") # PBL vapor tendency
      # file.write(          ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
      # file.write(          ",'MMF_QRL','MMF_QRS'")
      # file.write(          ",'MMF_QC','MMF_QI','MMF_QR'")
      # if 'MMF1' in compset:
      #    file.write(       ",'CRM_QPC','CRM_QPI'")
      # if 'MMF2' in compset:
      #    file.write(       ",'CRM_QR'")
      #    file.write(       ",'MMF_RHOD','MMF_RHOV'")
      #    file.write(       ",'MMF_NC','MMF_NI','MMF_NR'")
      #    file.write(       ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
      #    file.write(       ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
      #    file.write(       ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
      #    file.write(       ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
      #    # file.write(       ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
      #    file.write(       ",'MMF_LIQ_ICE','MMF_VAP_LIQ','MMF_VAP_ICE'")
      file.write('\n')
   
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   if '.NO-MSA.' in case: file.write(f'use_crm_accel = .false. \n')
   # file.write(f' cosp_lite = .true. \n')
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write(" inithist = \'ENDOFRUN\' \n")
   file.close()
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'init_file_lnd' in locals() or 'data_file_lnd' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'init_file_lnd' in locals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
      if 'data_file_lnd' in locals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
      # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'stop_opt' in locals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in locals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'queue'    in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in locals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

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
