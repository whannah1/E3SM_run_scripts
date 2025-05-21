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

# stop_opt,stop_n,resub,walltime = 'nstep',3,0,'0:30'
# stop_opt,stop_n,resub,walltime = 'nstep',4,0,'1:00'
# stop_opt,stop_n,resub,walltime = 'nstep',10,0,'0:30'
# stop_opt,stop_n,resub,walltime = 'nstep',230,0,'0:30'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00'
# stop_opt,stop_n,resub,walltime = 'ndays',20,0,'2:00'


### Case specific settings
# compset='F2010';          arch='GNUCPU';
# compset='F2010-MMF-SAM';  arch='GNUGPU';
# compset='F2010-MMF-SAM';  arch='GNUCPU';

# compset='F2010-MMF-PAM-A';arch='GNUGPU';pmod='F-QALL'
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'#; debug_mode=True;
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'

# compset='FAQP-MMF-SAM';  arch='GNUGPU'
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'
# compset='FAQP-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; debug_mode=True

# compset='F2010-MMF-PAM-A';arch='GNUCPU';pmod='F-QALL'; debug_mode=True
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; debug_mode=True; 
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; 
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'

# ---- F2010 CPU ----
# compset='FAQP-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; ne= 4;
# compset='FAQP-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; ne= 4; debug_mode=True
# compset='FAQP-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne= 4;
# compset='FAQP-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne= 4; debug_mode=True
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne= 4;
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; ne= 4;
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne= 4; debug_mode=True
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne=30;
# compset='F2010-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; ne=30; debug_mode=True
# ---- F2010 GPU ----
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 4;
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 4; debug_mode=True
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'; ne= 30;
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 30;
# compset='FAQP-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 30; debug_mode=True
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'; ne= 4;
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'; ne= 4; debug_mode=True 
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 4;
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne= 4; debug_mode=True
compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'; ne=30;
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne=30;
# compset='F2010-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; ne=30; debug_mode=True



# compset='FSCM-ARM97-MMF-SAM'  ;arch='GNUGPU'
# compset='FSCM-ARM97-MMF-PAM-A';arch='GNUGPU'
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUGPU';pmod='F-QALL'; #debug_mode=True;
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUGPU';pmod='F-QTOT'#;debug_mode=True;

# compset='FSCM-ARM97'  ;arch='GNUCPU'
# compset='FSCM-ARM97-MMF-SAM'  ;arch='GNUCPU';               #debug_mode=True
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUCPU';pmod='F-QALL'; debug_mode=True; 
# compset='FSCM-ARM97-MMF-PAM-C';arch='GNUCPU';pmod='F-QTOT'; #debug_mode=True

### set grid
if ne== 4: npg = 2; grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}';num_nodes=1
if ne==30: npg = 2; grid=f'ne{ne}pg{npg}_oECv3';        num_nodes=32
# if compset=='F2010'  : ne,npg = 4,2;grid=f'ne{ne}pg{npg}_oQU480';       num_nodes=1
# if 'F2010' in compset: ne,npg = 4,2;grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}';num_nodes=1
# if 'FAQP'  in compset: ne,npg = 4,2;grid=f'ne{ne}pg{npg}_ne{ne}pg{npg}';num_nodes=1
# if 'F2010' in compset: ne,npg =30,2;grid=f'ne{ne}pg{npg}_oECv3';        num_nodes=32
# if 'FAQP'  in compset: ne,npg =30,2;grid=f'ne{ne}pg{npg}_oECv3';        num_nodes=32
if 'FSCM'  in compset: ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';              num_nodes=1

# start over after build updates to use C++ P3/SHOC
# case_list=['E3SM','PAM-DEV-00',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # 
# case_list=['E3SM','PAM-DEV-01',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # reorder P3 vertical coord

# case_list=['E3SM','PAM-DEV-02',arch,compset,grid,'FQT']; src_dir=top_dir+'/E3SM_SRC0' # retest forcing - force total water
# case_list=['E3SM','PAM-DEV-02',arch,compset,grid,'FQV']; src_dir=top_dir+'/E3SM_SRC0' # retest forcing - force each tracer

# case_list=['E3SM','PAM-DEV-03',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # stick with forcing all tracers - fix output units
# case_list=['E3SM','PAM-DEV-04',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # try switching SHOC to wet mixing ratios and full pressure
# case_list=['E3SM','PAM-DEV-05',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # modify both SHOC+P3 - mixing ratios and pressure
# case_list=['E3SM','PAM-DEV-06',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # 05 + refactor gcm forcing
# case_list=['E3SM','PAM-DEV-07',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # 06 + change how P3 prog_state is set
# case_list=['E3SM','PAM-DEV-08',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # try disabling SHOC
# case_list=['E3SM','PAM-DEV-09',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # modify P3 input cloud fraction

# case_list=['E3SM','PAM-DEV-10',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0'
# case_list=['E3SM','PAM-DEV-11',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # use input dry density for feedback - also adjust qt forcing
# case_list=['E3SM','PAM-DEV-12',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # adjust how CRM state is recalled
# case_list=['E3SM','PAM-DEV-13',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # update SHOC interface theta variables and get final temp from DSE

# case_list=['E3SM','PAM-DEV-14',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # update reference state before PAM dycor - also save and force dry density
# case_list=['E3SM','PAM-DEV-15',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # add condensate to anelastic reference state
# case_list=['E3SM','PAM-DEV-16',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # omit phis from zint, reduce sponge layer time scale, and update rho_d to disable rho_d forcing


# test if reducing time step can lead to better stability (also increase sponge layer timescale to 6 min)
# crm_dt=10; case_list=['E3SM','PAM-DEV-17',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' 
# crm_dt=2;  case_list=['E3SM','PAM-DEV-17',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0'

# case_list=['E3SM','PAM-DEV-18',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # try to fix precipitation magnitude
# case_list=['E3SM','PAM-DEV-19',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # try to fix SHOC interface
# case_list=['E3SM','PAM-DEV-20',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # retry after bug fixes and clean up
# case_list=['E3SM','PAM-DEV-21',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # update SHOC inputs & retry getting temp from SHOC DSE
# case_list=['E3SM','PAM-DEV-22',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # minor SHOC interface adjustment (still using DSE for temperature)

# revisit time step sensitivity
# crm_dt=10; case_list=['E3SM','PAM-DEV-23',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' 
# crm_dt=1;  case_list=['E3SM','PAM-DEV-23',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0'

# test without dycor running
# disable_dycor=True; case_list=['E3SM','PAM-DEV-24',arch,compset,grid,'NO_DYCOR']; src_dir=top_dir+'/E3SM_SRC0' 
# disable_dycor_run=True; case_list=['E3SM','PAM-DEV-24',arch,compset,grid,'NO_DYCOR_RUN']; src_dir=top_dir+'/E3SM_SRC0' 

# crm_dt=10; case_list=['E3SM','PAM-DEV-25',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' # back to testing w/ dycor after fixing issues
# crm_dt=1;  case_list=['E3SM','PAM-DEV-25',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' # back to testing w/ dycor after fixing issues

# crm_dt=10; case_list=['E3SM','PAM-DEV-26',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' # fix how P3 lookup table data is loaded for better performance
# case_list=['E3SM','PAM-DEV-26',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # fix how P3 lookup table data is loaded for better performance

# case_list=['E3SM','PAM-DEV-27',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # fix P3 lookup table paths to avoid needing to hard code them

# case_list=['E3SM','PAM-DEV-28',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # fix friction... again
# crm_dt=1;  case_list=['E3SM','PAM-DEV-28',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0' # back to testing w/ dycor after fixing issues

# case_list=['E3SM','PAM-DEV-29',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # figure out why ne30 is unstable
# case_list=['E3SM','PAM-DEV-29.1',arch,compset,grid]; src_dir=top_dir+'/E3SM_SRC0' # test PAM compressible option
# crm_dt=1; gcm_dt=1*60;  case_list=['E3SM','PAM-DEV-29',arch,compset,grid,f'CDT_{crm_dt}',f'GDT_{gcm_dt}']; src_dir=top_dir+'/E3SM_SRC0'

# crm_dt=1;  case_list=['E3SM','PAM-DEV-30',arch,compset,grid,f'CDT_{crm_dt:02d}']; src_dir=top_dir+'/E3SM_SRC0'
# crm_dt=5;  case_list=['E3SM','PAM-DEV-30',arch,compset,grid,f'CDT_{crm_dt:02d}']; src_dir=top_dir+'/E3SM_SRC0'
# crm_dt=10;  case_list=['E3SM','PAM-DEV-30',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0'
# crm_dt=30;  case_list=['E3SM','PAM-DEV-30',arch,compset,grid,f'CDT_{crm_dt}']; src_dir=top_dir+'/E3SM_SRC0'
# crm_dt=10; gcm_dt=1*60;  case_list=['E3SM','PAM-DEV-30',arch,compset,grid,f'CDT_{crm_dt}',f'GDT_{gcm_dt}']; src_dir=top_dir+'/E3SM_SRC0'

# export CRM_DYN_PER_PHYS=2; nohup  ./run_E3SM.2022.pam_dev_test.olcf.py > run.cdpp_${CRM_DYN_PER_PHYS}.out &
# export CRM_DT=20 CRM_DPP=2; nohup  ./run_E3SM.2022.pam_dev_test.olcf.py > run.crm_dt_${CRM_DT}.cdpp_${CRM_DPP}.out &

# export CRM_DT=10 CRM_DPP=1;  ./run_E3SM.2022.pam_dev_test.olcf.py
# export CRM_DT=10 CRM_DPP=2;  ./run_E3SM.2022.pam_dev_test.olcf.py
# export CRM_DT=10 CRM_DPP=3;  ./run_E3SM.2022.pam_dev_test.olcf.py

# crm_dt           = int(os.getenv('CRM_DT'))
# crm_dyn_per_phys = int(os.getenv('CRM_DPP'))
# crm_dt=5; case_list=['E3SM','PAM-DEV-31',arch,compset,grid,f'CDT_{crm_dt:02d}',f'DPT_{crm_dyn_per_phys:02d}']; src_dir=top_dir+'/E3SM_SRC0' # systematic test of different time step settings
# case_list=['E3SM','PAM-DEV-31',arch,compset,grid,f'CDT_{crm_dt:02d}',f'DPT_{crm_dyn_per_phys:02d}']; src_dir=top_dir+'/E3SM_SRC0' # systematic test of different time step settings
# crm_dt=10; cdpp=2; case_list=['E3SM','PAM-DEV-31',arch,compset,grid,f'CDT_{crm_dt:02d}',f'DPT_{cdpp:02d}']; src_dir=top_dir+'/E3SM_SRC0' # systematic test of different time step settings

crm_dt=5; crm_dyn_per_phys=2; case_list=['E3SM','PAM-DEV-32',arch,compset,grid,f'CDT_{crm_dt:02d}',f'DPT_{crm_dyn_per_phys:02d}']; src_dir=top_dir+'/E3SM_SRC0' # super-cycle P3 - maybe issue @ 10-sec is due to SHOC?

if 'pmod' in locals(): case_list.append(pmod)

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
# land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
# # if grid=='ne30pg2_r05_oECv3':land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
# if grid=='ne30pg2_oECv3':
#    land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#    land_data_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
#    # land_data_file = 'surfdata_ne30pg2_simyr2010_c201210.nc'
#    land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 

# SCM defaults to NCPL=12 (2 hour time step) - switch back to MMF default 
# if 'MMF' in compset and 'dtime' not in locals():
if 'MMF' in compset:
   dtime = 20*60; ncpl  = 86400 / dtime
else:
   dtime = 60*60; ncpl  = 86400 / dtime


if 'gcm_dt' in locals():
   dtime = gcm_dt; ncpl = int( 86400 / dtime )

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
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
   if ne==4 and npg==2:
      run_cmd(f'./xmlchange NTASKS_OCN=16')
      run_cmd(f'./xmlchange NTASKS_ICE=16')

   if 'crm_dt' in locals():
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')

   cpp_defs = ''
   
   if 'F-QALL' in case and 'MMF-PAM-C' in compset: cpp_defs += ' -DMMF_PAM_FORCE_ALL_WATER_SPECIES '
   if 'F-QTOT' in case and 'MMF-PAM-C' in compset: cpp_defs += ' -DMMF_PAM_FORCE_TOTAL_WATER '

   if 'disable_dycor' in locals():
      if disable_dycor: 
         cpp_defs += ' -DMMF_PAM_DISABLE_DYCOR '
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx 5 \" ')
   if 'disable_dycor_run' in locals():
      if disable_dycor_run: 
         cpp_defs += ' -DMMF_PAM_DISABLE_DYCOR_RUN '
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx 5 \" ') 

   if 'crm_dyn_per_phys' in locals(): cpp_defs += f' -DCRM_DYN_PER_PHYS={crm_dyn_per_phys} '

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
   if stop_opt=='nstep':
      file.write(f' nhtfrq = 0,1,1 \n')
      file.write(f' mfilt  = 1,{stop_n},{stop_n} \n')
   else:
      file.write(' nhtfrq = 0,1,-1 \n')
      file.write(' mfilt  = 1,72,24 \n')
      # file.write(f' nhtfrq = 0,1,1 \n')
      # file.write(f' mfilt  = 1,{72*stop_n},{72*stop_n} \n')
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
   # if 'MMF' in compset:
   #    file.write(       ",'QRLC','QRSC'")
   #    file.write(       ",'CRM_QRL','CRM_QRLC'")
   #    file.write(       ",'CRM_U','CRM_W'")
   #    file.write(       ",'CRM_T','CRM_QV'")
   #    file.write(       ",'CRM_QC','CRM_QI'")
   #    file.write(       ",'CRM_RAD_T','CRM_RAD_QV','CRM_RAD_QC','CRM_RAD_QI','CRM_RAD_CLD'")
   #    file.write(       ",'CRM_QRAD'")
   #    file.write(       ",'MMF_TLS'")
   #    file.write(       ",'MMF_DT','MMF_DQ','MMF_DQC','MMF_DQI','MMF_DQR'")
   #    file.write(       ",'MMF_QRL','MMF_QRS'")
   #    file.write(       ",'MMF_QC','MMF_QI','MMF_QR'")
   #    if 'PAM' in compset:
   #       file.write(    ",'MMF_NC','MMF_NI','MMF_NR'")
   #       file.write(    ",'MMF_RHODLS','MMF_RHOVLS','MMF_RHOLLS','MMF_RHOILS'")
   #       file.write(    ",'MMF_DT_SGS','MMF_DQV_SGS','MMF_DQC_SGS','MMF_DQI_SGS','MMF_DQR_SGS'")
   #       file.write(    ",'MMF_DT_MICRO','MMF_DQV_MICRO','MMF_DQC_MICRO','MMF_DQI_MICRO','MMF_DQR_MICRO'")
   #       file.write(    ",'MMF_DT_DYCOR','MMF_DQV_DYCOR','MMF_DQC_DYCOR','MMF_DQI_DYCOR','MMF_DQR_DYCOR'")
   #       file.write(    ",'MMF_DT_SPONGE','MMF_DQV_SPONGE','MMF_DQC_SPONGE','MMF_DQI_SPONGE','MMF_DQR_SPONGE'")
   #       file.write(    ",'MMF_LIQ_ICE','MMF_VAP_LIQ','MMF_VAP_ICE'")
   file.write('\n')

   if 'gcm_dt' in locals():
      if gcm_dt == 1*60 :
         file.write(f'dt_tracer_factor = 1 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')
         file.write(f'hypervis_subcycle_q = 1 \n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   # if 'land_init_file' in locals() or 'land_data_file' in locals():
   #    nfile = 'user_nl_elm'
   #    file = open(nfile,'w')
   #    if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
   #    if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
   #    file.close()
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
