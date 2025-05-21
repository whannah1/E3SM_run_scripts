#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue = 'regular'  # regular / debug 

stop_opt,stop_n,resub,walltime = 'nstep',10,0,'1:00:00' # for ne4
# stop_opt,stop_n,resub,walltime = 'nstep',3,0,'0:10:00' # for SCM
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'

# arch = 'GNUGPU' # GNUCPU / GNUGPU / CORI / CORIGNU

### common settings
# compset='F2010';          arch='GNUCPU';
# compset='F2010-MMF-SAM';  arch='GNUGPU';
# compset='F2010-MMF-SAM';  arch='GNUCPU';

# compset='F2010-MMF-PAM-A';arch='GNUGPU';pmod='F-QALL'
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'

# compset='F2010-MMF-PAM-A';arch='GNUCPU';pmod='F-QALL'; #debug_mode=True
compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; debug_mode=True
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; #debug_mode=True

# compset='FSCM-ARM97-MMF-SAM'  ;arch='GNUGPU'
# compset='FSCM-ARM97-MMF-PAM-A';arch='GNUGPU'
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'

# compset='FSCM-ARM97'  ;arch='GNUCPU'
# compset='FSCM-ARM97-MMF-SAM'  ;arch='GNUCPU';               #debug_mode=True
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; debug_mode=True
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; debug_mode=True

### set grid
if 'F2010' in compset: ne,npg = 4,2;grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}';num_nodes=1
if compset=='F2010'  : ne,npg = 4,2;grid=f'ne{ne}pg{npg}_oQU480';       num_nodes=1
if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';              num_nodes=1


# case_list=['E3SM','PAM-DEV-00',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # whannah/mmf/change-pbuf-qt-to-qv
# case_list=['E3SM','PAM-DEV-01',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # whannah/mmf/crm-interface-rm-m2005-add-p3
# case_list=['E3SM','PAM-DEV-02',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC4' # whannah/mmf/pam-impl
# case_list=['E3SM','PAM-DEV-03',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC4' # restart PM test after having issues on Summit 2023-4-28
case_list=['E3SM','PAM-DEV-04',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC4' # fixed major issues - new issue that seems machine dependent?

if 'pmod' in locals(): case_list.append(pmod)

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
# if grid=='ne30pg2_r05_oECv3':land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
if grid=='ne30pg2_oECv3':
   land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   land_data_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   # land_data_file = 'surfdata_ne30pg2_simyr2010_c201210.nc'
   land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# SCM defaults to NCPL=12 (2 hour time step) - switch back to MMF default 
if 'MMF' in compset:
   dtime = 20*60; ncpl  = 86400 / dtime
else:
   dtime = 60*60; ncpl  = 86400 / dtime

if 'CPU' in arch  : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch  : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
if arch=='CORI'   : max_mpi_per_node,atm_nthrds  = 64,1
if arch=='CORIGNU': max_mpi_per_node,atm_nthrds  = 64,1
if 'FSCM' in compset: max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CORI'   : cmd += f' -mach cori-knl -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CORIGNU': cmd += f' -mach cori-knl -compiler gnu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config : 
   if ne==4 and npg==2:
      run_cmd(f'./xmlchange NTASKS_OCN=16')
      run_cmd(f'./xmlchange NTASKS_ICE=16')

   if 'crm_dt' in locals():
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
   if 'F-QALL' in case and 'MMF-PAM-C' in compset:
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DMMF_PAM_FORCE_ALL_WATER_SPECIES \'  \"')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# copy P3 lookup table data
(run_dir, err) = sp.Popen("./xmlquery RUNDIR --value",stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
if not os.path.exists(f'{run_dir}/p3_data'): os.mkdir(f'{run_dir}/p3_data')
run_cmd(f'cp {src_dir}/components/eam/src/physics/crm/pam/external/physics/micro/p3/tables/p3_lookup_table* {run_dir}/p3_data/ ')
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
   if stop_opt=='nstep':
      file.write(f' nhtfrq = 0,1,1 \n')
      file.write(f' mfilt  = 1,{stop_n},{stop_n} \n')
   else:
      file.write(' nhtfrq = 0,1,-1 \n')
      file.write(' mfilt  = 1,72,24 \n')
   file.write('\n')
   file.write(" fincl2 = 'PS','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECSC'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TBOT','QBOT'")
   file.write('\n')
   file.write(" fincl3 =  'PS','PSL'")
   file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   # if stop_opt=='nstep':
   if 'MMF' in compset:
      file.write(       ",'QRLC','QRSC'")
      file.write(       ",'CRM_QRL','CRM_QRLC'")
      file.write(       ",'CRM_U','CRM_W'")
      file.write(       ",'CRM_T','CRM_QV'")
      file.write(       ",'CRM_QC','CRM_QI'")
      file.write(       ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
      file.write(       ",'CRM_QRAD'")
      file.write(       ",'MMF_TLS'")
      file.write(       ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
      file.write(       ",'MMF_QRL','MMF_QRS'")
      file.write(       ",'MMF_QC','MMF_QI','MMF_QR'")
      if 'PAM' in compset:
         file.write(    ",'MMF_NC','MMF_NI','MMF_NR'")
         file.write(    ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
         file.write(    ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
         file.write(    ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
         file.write(    ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
         file.write(    ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
   file.write('\n')
   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'land_init_file' in locals() or 'land_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # use alternate start date
   # run_cmd(f'./xmlchange RUN_STARTDATE=\"1997-06-19\"')
   # run_cmd(f'./xmlchange RUN_STARTDATE=\"1997-06-20\"')
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
   if 'CPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
