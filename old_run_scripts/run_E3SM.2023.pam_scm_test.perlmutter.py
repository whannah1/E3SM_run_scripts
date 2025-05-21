#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
disable_compose = False

acct = 'm3312'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/mmf/pam-impl @ Aug 21

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 
arch = 'GNUGPU' # GNUCPU / GNUGPU

# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',10,0,'2:00:00'

# compset='FSCM-ARM97-MMF1'
compset='FSCM-ARM97-MMF2'

ne,npg,grid = 30,2,'ne30pg2_EC30to60E2r2'; num_nodes = 32
# ne,npg,grid = 4,2,'ne4pg2_ne4pg2'; num_nodes = 1
if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';              num_nodes=1


nlev=60;crm_nz=50

# case = '.'.join(['E3SM','2023-PAM-SCM-00',grid,compset])
# case = '.'.join(['E3SM','2023-PAM-SCM-00',grid,compset,'UCF_L','UCF_I','UCF_R']) # P3 cld_frac: l/r/i=1
# case = '.'.join(['E3SM','2023-PAM-SCM-00',grid,compset,'UCF_I','UCF_R'])         # P3 cld_frac: l=shoc,r/i=1
# case = '.'.join(['E3SM','2023-PAM-SCM-00',grid,compset,'UCF_I'])                 # P3 cld_frac: l/r=shoc,i=1
# case = '.'.join(['E3SM','2023-PAM-SCM-00',grid,compset])                         # P3 cld_frac: l/r/i=shoc
# case = '.'.join(['E3SM','2023-PAM-SCM-01',grid,compset])  # reset to uniform cld frac and enable phys tend stats
# case = '.'.join(['E3SM','2023-PAM-SCM-02',grid,compset]) # disable SHOC
# case = '.'.join(['E3SM','2023-PAM-SCM-03',grid,compset]) # refactor handling of P3 "prev" variables and fix bug
# case = '.'.join(['E3SM','2023-PAM-SCM-04',grid,compset]) # 03 + swap dry/wet assumptions in P3
# case = '.'.join(['E3SM','2023-PAM-SCM-05',grid,compset]) # 03 + alter cld_frac_i based on temperture (revert 04)
# case = '.'.join(['E3SM','2023-PAM-SCM-06',grid,compset]) # 03 + disable rho_d reset (revert 05)
# case = '.'.join(['E3SM','2023-PAM-SCM-07',grid,compset]) # 06 + test w/ static dry density
# case = '.'.join(['E3SM','2023-PAM-SCM-08',grid,compset]) # 03 + static number concentrations (c/i/r)
# case = '.'.join(['E3SM','2023-PAM-SCM-09',grid,compset]) # 08 but increase assumed number concentrations
case = '.'.join(['E3SM','2023-PAM-SCM-10',grid,compset]) # add forcing of number concentrations

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

if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
   run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
   #-------------------------------------------------------
   # PE layout mods from Noel
   if 'CPU' in arch: cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
   if 'GPU' in arch: cpl_stride = 4; cpl_ntasks = atm_ntasks / cpl_stride
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
   #-------------------------------------------------------
   cpp_opt = ''
   if '.UCF_L.' in case: cpp_opt += ' -DMMF_UNIFORM_CLD_FRAC_LIQ '
   if '.UCF_I.' in case: cpp_opt += ' -DMMF_UNIFORM_CLD_FRAC_ICE '
   if '.UCF_R.' in case: cpp_opt += ' -DMMF_UNIFORM_CLD_FRAC_RAIN '
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
      file.write(          ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
      file.write(          ",'CRM_QRAD'")
      file.write(          ",'MMF_TLS','MMF_QTLS'")
      # file.write(          ",'VDQ'") # PBL vapor tendency
      file.write(          ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
      file.write(          ",'MMF_QRL','MMF_QRS'")
      file.write(          ",'MMF_QC','MMF_QI','MMF_QR'")
      if 'MMF1' in compset:
         file.write(       ",'CRM_QPC','CRM_QPI'")
      if 'MMF2' in compset:
         file.write(       ",'CRM_QR'")
         file.write(       ",'MMF_RHOD','MMF_RHOV'")
         file.write(       ",'MMF_NC','MMF_NI','MMF_NR'")
         file.write(       ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
         file.write(       ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
         file.write(       ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
         file.write(       ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
         file.write(       ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
         file.write(       ",'MMF_LIQ_ICE','MMF_VAP_LIQ','MMF_VAP_ICE'")
      file.write('\n')
   

   if disable_compose:
      file.write(f' transport_alg       = 0 \n')
      file.write(f' hypervis_subcycle_q = 1 \n')
      file.write(f' dt_tracer_factor    = 1 \n')
   #------------------------------
   # Other namelist stuff
   #------------------------------   
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
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
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
