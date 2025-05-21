#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
ne,npg = 0,0
newcase,config,build,clean,submit,continue_run,copy_p3_data = False,False,False,False,False,False, False

acct = 'cli115'

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch'  # batch / debug 

### Compset
# compset='FAQP-MMF1'
# compset='FAQP-MMF2'
# compset='FRCE-MMF1'
# compset='FRCE-MMF2'
# compset='F2010'
# compset='F2010-MMF1'
compset='F2010-MMF2'
# compset='F2010-MMF2-AWFL'
# compset='FSCM-ARM97'
# compset='FSCM-ARM97-MMF1'
# compset='FSCM-ARM97-MMF2'
# compset='FSCM-ARM97-MMF2-AWFL'

src_dir=top_dir+'/E3SM_SRC1'
arch = 'GNUGPU' # GNUGPU / GNUCPU
ne   = 30

if 'SCM' in compset: 
   # stop_opt,stop_n,resub,walltime = 'nstep',3,0,'0:30'
   # stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'
   stop_opt,stop_n,resub,walltime = 'ndays',26,0,'2:00'
else:
   # stop_opt,stop_n,resub,walltime = 'nstep',20,1,'1:00'
   # stop_opt,stop_n,resub,walltime = 'ndays',8,4*3-1,'3:00'
   stop_opt,stop_n,resub,walltime = 'ndays',8,0,'2:00'
   # stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'
   # stop_opt,stop_n,resub,walltime = 'ndays',11,2,'3:00'

### set grid
# if ne==30: npg = 2; grid=f'ne{ne}pg{npg}_oECv3';         num_nodes=64
if ne==30: npg = 2; grid=f'ne{ne}pg{npg}_oECv3';         num_nodes=32
if ne== 4: npg = 2; grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}'; num_nodes=1
if 'SCM' in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}'; num_nodes=1


# case_list=['E3SM','PAM-DEV-2023-00',arch,grid,compset] # verify new compset config
# case_list=['E3SM','PAM-DEV-2023-00a',arch,grid,compset] # include bug fix in SAM case 
# case_list=['E3SM','PAM-DEV-2023-01',arch,grid,compset] # disable SHOC checks allow SHOC to use sfc flux for mixing
# case_list=['E3SM','PAM-DEV-2023-02',arch,grid,compset] # change the CRM feedback - calculate mix ration after density diff
# case_list=['E3SM','PAM-DEV-2023-03',arch,grid,compset] # modify conversions in SHOC
# case_list=['E3SM','PAM-DEV-2023-04',arch,grid,compset] # disable rho_d forcing
# case_list=['E3SM','PAM-DEV-2023-05',arch,grid,compset] # disable rho_d forcing and recall
# case_list=['E3SM','PAM-DEV-2023-06',arch,grid,compset] # use adjusted GCM temp for forcing INVALID - I double counted the adjustment!
# case_list=['E3SM','PAM-DEV-2023-07',arch,grid,compset] # combine 4 & 6                     INVALID - I double counted the adjustment!
# case_list=['E3SM','PAM-DEV-2023-08',arch,grid,compset] # switch to separate q forcing & disable rho_d forcing
# case_list=['E3SM','PAM-DEV-2023-09',arch,grid,compset] # switch to separate q forcing & retain rho_d forcing
# case_list=['E3SM','PAM-DEV-2023-10',arch,grid,compset] # use qt forcing & use GCM rho_d in CRM w/o rho_d forcing
# case_list=['E3SM','PAM-DEV-2023-11',arch,grid,compset] # Change P3 mixing ratio, pressure, dpres from dry to wet
# case_list=['E3SM','PAM-DEV-2023-12',arch,grid,compset] # 11 + set precip to zero - if CWV changes then maybe mass conservation is causing problems?
# case_list=['E3SM','PAM-DEV-2023-13',arch,grid,compset] # retry 11 without disabled rho_d forcing :-/
# case_list=['E3SM','PAM-DEV-2023-14',arch,grid,compset] # modify P3 inputs for nccn, nuceat, ni_act
# case_list=['E3SM','PAM-DEV-2023-15',arch,grid,compset] # set P3 input cloud frac to 1 (nccn=1e3)
# case_list=['E3SM','PAM-DEV-2023-16',arch,grid,compset] # nccn=1e9
# case_list=['E3SM','PAM-DEV-2023-17',arch,grid,compset] # disable dycor
# case_list=['E3SM','PAM-DEV-2023-18',arch,grid,compset] # cldfrac=1 + nccn=1e6
# case_list=['E3SM','PAM-DEV-2023-19',arch,grid,compset] # cldfrac=1 + nccn=1e9
# case_list=['E3SM','PAM-DEV-2023-20',arch,grid,compset] # cldfrac=1 + nccn=1e1
# case_list=['E3SM','PAM-DEV-2023-21',arch,grid,compset] # 15 + let SHOC use sfc flux (i.e. 01)
# case_list=['E3SM','PAM-DEV-2023-22',arch,grid,compset] # 15 + let SHOC apply sfc flux v1 - disable PBL T/q tend
# case_list=['E3SM','PAM-DEV-2023-23',arch,grid,compset] # 15 + let SHOC apply sfc flux v2 - disable PBL T/q input flux
# case_list=['E3SM','PAM-DEV-2023-24',arch,grid,compset] # 15 redo after sfc flux bug fix
# case_list=['E3SM','PAM-DEV-2023-25',arch,grid,compset] # cldfrac=1 + nccn=1e12
# case_list=['E3SM','PAM-DEV-2023-26',arch,grid,compset] # cldfrac=1 + do_prescribed_CCN=false, do_predict_nc=true, nccn=0, nc_nuceat_tend=0, ni_activated=0
# case_list=['E3SM','PAM-DEV-2023-27',arch,grid,compset] # cldfrac=1 + do_prescribed_CCN=false, do_predict_nc=true, nccn=0, nc_nuceat_tend=1, ni_activated=1
# case_list=['E3SM','PAM-DEV-2023-28',arch,grid,compset] # 27 + NCPL = 20 min (previous cases use NCPL = 1-hour)
# case_list=['E3SM','PAM-DEV-2023-29',arch,grid,compset] # cldfrac=1 + do_prescribed_CCN=true, do_predict_nc=true, nccn=50e6

# retry PAM-A + cldfrac=1 + do_prescribed_CCN=true, do_predict_nc=true, nccn=50e6
# also disable dry density forcing - start by updating to new GCM dry density every CRM call
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-30',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}']
# crm_dt=10; case_list=['E3SM','PAM-DEV-2023-30',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}']
# crm_dt= 1; case_list=['E3SM','PAM-DEV-2023-30',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-30',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']
# crm_dt=20; case_list=['E3SM','PAM-DEV-2023-30',arch,grid,compset,f'CDT_{crm_dt:02d}']

# test MSA in PAM
# crm_dt= 2; case_list=['E3SM','PAM-DEV-2023-31',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}']
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-31',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}']

# add dry density to MSA
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-32',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}']
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-32',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}',f'GDT_1200']

# disable MSA & update PAM submodule - test Matt's PAM-A updates
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-33',arch,grid,compset,'PD-C',f'CDT_{crm_dt:02d}'] # just verify PAM-C hasn't changed
# crm_dt= 5; case_list=['E3SM','PAM-DEV-2023-33',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']
# crm_dt=10; case_list=['E3SM','PAM-DEV-2023-33',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']
# crm_dt=20; case_list=['E3SM','PAM-DEV-2023-33',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']

# test MSA in PAM-A
# crm_dt=10; case_list=['E3SM','PAM-DEV-2023-34',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']
# crm_dt=20; case_list=['E3SM','PAM-DEV-2023-34',arch,grid,compset,'PD-A',f'CDT_{crm_dt:02d}']

# test updated build config & revisit time step sensitivity
# case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset]
# if 'MMF2' in compset:
   # crm_dt= 8; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}']
   # crm_dt=10; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}']
   # crm_dt=20; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}']
   # crm_dt=30; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}']
   # crm_dt= 1; crm_dpp=1; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 2; crm_dpp=1; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 4; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 5; crm_dpp=1; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 5; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 5; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 8; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt= 8; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt=10; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt=10; crm_dpp=6; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt=10; crm_dpp=8; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
   # crm_dt=20; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# else:
#    case_list=['E3SM','PAM-DEV-2023-35',arch,grid,compset]


# 36 - focused ensemble to figure out how to efficiently run F2010 @ ne30   
# if 'MMF2-AWFL' in compset:
#    crm_dt= 10; dpp=2; msa=2
#    case_list=['E3SM','PAM-DEV-2023-36',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{dpp}',f'MSA_{msa}']
# elif 'MMF2' in compset:
#    # crm_dt= 2; dpp=2; msa=4
#    crm_dt= 4; dpp=2; msa=2
#    # crm_dt= 5; dpp=1; msa=2
#    # crm_dt= 8; dpp=4; msa=2
#    # crm_dt=10; dpp=4; msa=2
#    case_list=['E3SM','PAM-DEV-2023-36',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{dpp}',f'MSA_{msa}']
# else:
#    case_list=['E3SM','PAM-DEV-2023-36',arch,grid,compset]

### 37 - seems like we need crm_dt=4 sec in order for ne30 to be viable - do a longer integration
# case_list=['E3SM','PAM-DEV-2023-37',arch,grid,compset] 

### 38 - test new forcing appraoch - Sept 22, 2023
# crm_dt= 4; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-38',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt=10; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-38',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']

### various updates - new water forcing approach / new dycor temperature treatment / added hyperdiffusion
# case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset]
# crm_dt= 4; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt= 8; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt= 8; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt= 10; crm_dpp=4; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt= 16; crm_dpp=8; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}']
# crm_dt= 5; msa=4; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'MSA_{msa}'] 
# crm_dt= 4; msa=3; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'MSA_{msa}'] 

crm_dt= 8; crm_dpp=2; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'CDT_{crm_dt:02d}',f'DPP_{crm_dpp}','NN_32']

# nthrds=1; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'6x{nthrds}']
# nthrds=2; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'6x{nthrds}']
# nthrds=7; case_list=['E3SM','PAM-DEV-2023-40',arch,grid,compset,f'6x{nthrds}']

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
if grid=='ne30pg2_oECv3':
   land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 

# SCM defaults to NCPL=12 (2 hour time step) - switch back to MMF default 
# if 'MMF' in compset and 'dtime' not in locals():
# if 'MMF' in compset: dtime = 20*60; ncpl  = 86400 / dtime

if 'SCM' in compset and 'PD-C' in case: dtime = 60*60; ncpl  = 86400 / dtime
if 'SCM' in compset and 'PD-A' in case: dtime = 20*60; ncpl  = 86400 / dtime
# if 'SCM' in compset: dtime = 60*60; ncpl  = 86400 / dtime
# if 'SCM' in compset: dtime = 20*60; ncpl  = 86400 / dtime

if 'gcm_dt' in locals():
   dtime = gcm_dt; ncpl = int( 86400 / dtime )

max_task_per_node = 42
# if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'nthrds' in locals():
   if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 6,nthrds
   if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,nthrds
else:
   if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 6,1
   if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,1
if 'FSCM' in compset: max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config : 
   if ne==4 and npg==2: run_cmd(f'./xmlchange NTASKS_OCN=16,NTASKS_ICE=16')

   if 'crm_dt' in locals():
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')

   if '.PD-C' in case:run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -pam_dycor spam \" ')
   if '.PD-A' in case:run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -pam_dycor awfl \" ')


   cpp_defs = ''
   if 'crm_dpp' in locals(): cpp_defs += f' -DMMF_PAM_DPP={crm_dpp}'
   if     'dpp' in locals(): cpp_defs += f' -DMMF_PAM_DPP={dpp}'

   if cpp_defs != '': run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' {cpp_defs} \'  \"')

   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# copy P3 lookup table data
# if copy_p3_data and 'PAM' in compset:
#    (run_dir, err) = sp.Popen("./xmlquery RUNDIR --value",stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
#    if not os.path.exists(f'{run_dir}/p3_data'): os.mkdir(f'{run_dir}/p3_data')
#    run_cmd(f'cp {src_dir}/components/eam/src/physics/crm/pam/external/physics/micro/p3/tables/p3_lookup_table* {run_dir}/p3_data/ ')
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
   if '.PD-A' in case and stop_opt=='nstep':
      file.write(f' nhtfrq = 0,1,1 \n')
      file.write(f' mfilt  = 1,{stop_n},{stop_n} \n')
      # step_per_day = int(ncpl)*stop_n
      # file.write(f' nhtfrq = 0,1,1 \n')
      # file.write(f' mfilt  = 1,{step_per_day},{step_per_day} \n')
   else:
      file.write(' nhtfrq = 0,-1,-1 \n')
      file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
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

   if 'SCM' in compset:
      file.write(" fincl3 =  'PS','PSL'")
      file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
      file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
      if 'MMF' in compset:
         file.write(       ",'QRLC','QRSC'")
         file.write(       ",'CRM_QRL','CRM_QRLC'")
         file.write(       ",'CRM_U','CRM_W'")
         file.write(       ",'CRM_T','CRM_QV'")
         file.write(       ",'CRM_QC','CRM_QI'")
         file.write(       ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
         file.write(       ",'CRM_QRAD'")
         file.write(       ",'MMF_TLS','MMF_QTLS'")
         file.write(       ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
         file.write(       ",'MMF_QRL','MMF_QRS'")
         file.write(       ",'MMF_QV','MMF_QC','MMF_QI','MMF_QR'")
         # if 'MMF1' in compset:
         #    file.write(    ",'MMF_QTLS'")
         if 'MMF2' in compset:
            file.write(    ",'MMF_NC','MMF_NI','MMF_NR'")
            file.write(    ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
            file.write(    ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
            file.write(    ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
            file.write(    ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
            # file.write(    ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
            file.write(    ",'MMF_LIQ_ICE','MMF_VAP_LIQ','MMF_VAP_ICE'")
      file.write('\n')

   if 'msa' in locals(): 
      file.write(f'crm_accel_factor = {msa} \n')

   if 'no-accel' in case:
      file.write(f'use_crm_accel = .false. \n')

   if 'gcm_dt' in locals():
      if gcm_dt == 1*60 :
         file.write(f'dt_tracer_factor = 1 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')
         file.write(f'hypervis_subcycle_q = 1 \n')
      if gcm_dt < 20*60 :
         file.write(f'dt_tracer_factor    = 1 \n')
         file.write(f'dt_remap_factor     = 1 \n')
         file.write(f'hypervis_subcycle_q = 1 \n')
         file.write(f'se_tstep = {gcm_dt} \n')
         

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
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
