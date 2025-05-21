#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

# src_dir  = top_dir+'E3SM_SRC1/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug 

ne,npg = 4,2
# compset,ne,npg = 'F-EAMv1-AQP1',4,2
# compset,ne,npg = 'FC5AV1C-L',30,2
# compset,ne,npg = 'F-MMFXX',4,2
# compset,ne,npg = 'F-MMF1',4,2
# compset,ne,npg = 'F-MMF2-ECPP',4,2
# compset,ne,npg = 'F-MMFXX-SCM-ARM97',4,0


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


if queue=='debug' : 
   # stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
   stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'


### run for Mikhail to analyze grid noise
# case = '.'.join(['E3SM',grid,compset,'CRMNX_64','CRMDX_2000','CRMDT_5','RADNX_1'])


### Aqua RRM test
# src_dir=top_dir+'E3SM_SRC2/'; case='.'.join(['E3SM','L60_test',grid,compset,'L72','00'])
# hiccup_scratch = '/global/cscratch1/sd/whannah/HICCUP/data'
# init_file_atm = f'{hiccup_scratch}/eam_i_aqua_RRM-cubeface-grad_L60_c20210907.nc'

### P3 timing test
# compset = 'F-MMFXX'
# compset = 'F-MMFXX-P3'
# compset = 'F-MMF1'
# compset = 'F-MMF2-ECPP'
# compset = 'F-MMF2-PAER'
# src_dir = top_dir+'E3SM_SRC1/'; atm_ntasks = 64*2
# case = '.'.join(['E3SM','P3-TIMING','gnu',grid,compset,'NO-MSA','00']) 

### P3 SCM test
# src_dir = top_dir+'E3SM_SRC1/'
# compset = 'F-MMFXX-P3-SCM-ARM97'
# npg = 0; grid = 'ne4_ne4'; stop_opt,stop_n,walltime = 'ndays',1,'00:30'
# # case = '.'.join(['E3SM','P3-TEST','gnu',compset,'00']) # 
# # case = '.'.join(['E3SM','P3-TEST','gnu',compset,'01']) # disable saturation adjustment
# case = '.'.join(['E3SM','P3-TEST',compset,'01']) # disable saturation adjustment

### flux injection tests
# src_dir = top_dir+'E3SM_SRC3/'; atm_ntasks = 64*2
# compset = 'F-MMF1'
# # case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST','gnu',grid,compset,'00']) # baseline
# # case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST','gnu',grid,compset,'01']) # flux injection mods (no change in actual flux)
# case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST','gnu',grid,compset,'02']) # flux injection mods + move fluxes

### test enabling VT+ESMT by default
src_dir = top_dir+'E3SM_SRC1/'; atm_ntasks = 64
compset = 'F2010-MMF1'
# compset = 'F2010-CICE'
case = '.'.join(['E3SM','TEST-VT-ESMT-DEFAULT',grid,compset,'00'])

case = case+'.debug-on'
# case = case+'.checks-on'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# ic_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/L60_initial_conditions/'
# if 'MMF' not in compset and '.L60.' in case: 
#    init_file_atm = f'{ic_path}/eam_i_mam3_Linoz_ne{ne}np4_L60_c20210823.nc'


# land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
# if grid=='ne30pg2_r05_oECv3': land_init_file = f'{land_init_path}/ELM_spinup.ICRUELM.{grid}.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

# dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)
# if ne==120: dtime = 5*60
# if 'dtime' in locals(): ncpl = 86400/dtime

if 'NTASKS' in case:
   params = [p.split('_') for p in case.split('.')]
   for p in params: 
      if p[0]=='NTASKS': atm_ntasks = int(p[1])

if 'atm_ntasks' not in locals():
   if ne==30: atm_ntasks = 5400
   if ne==4:  atm_ntasks = 64

if 'SCM' in compset: atm_ntasks = 1

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
   cmd += f' -compset {compset} -res {grid}'
   # cmd += ' --pecount '+str(num_dyn)+'x1'
   if '.gnu.'  in case : cmd = cmd + ' --compiler gnu '
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # if changing vertical levels make sure to update ncdata here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
      # if p[0]=='CRMNZ': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {p[1]} \" ')
      # if p[0]=='NLEV' : run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.FLUX_BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS '
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   
   if '.CRM_SFC_FLUX_TEST.' in case: 
      if '.01' in case: cpp_opt += ' -DMMF_TKE_MOD'
      if '.02' in case: cpp_opt += ' -DMMF_TKE_MOD -DMMF_CRM_SFC_FLUX'

   # CRM variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   if 'debug-on' in case and 'MMFXX' in compset : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads - disable threading for MMF
   # if ne!=120 and num_dyn!=0 : 

   if 'atm_ntasks' in locals(): 
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
   else:
      if 'MMF' in compset and ne==30: run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 5400 ')
      if 'MMF' in compset and ne==45: run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 5400 ')

   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   # if '.pio_v1.' in case: run_cmd('./xmlchange PIO_VERSION=1')
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # query some stuff about the case
   #-------------------------------------------------------
   # (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
   #                                   stdout=sp.PIPE, shell=True).communicate()
   # (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
   #                                    stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # atmos namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #-------------------------------------------------------
   # atmos history output
   #-------------------------------------------------------
   if stop_opt=='nstep' or 'SCM' in compset:
      file.write(' nhtfrq    = 0,1 \n')
      file.write(f' mfilt     = 1,{stop_n} \n')
   else:
      file.write(' nhtfrq    = 0,-1,-24 \n')
      file.write(' mfilt     = 1,24,1 \n')
      

   # if 'MMF' in compset: 
   #    file.write(" fincl1    = 'MMF_SUBCYCLE_FAC','TS','MMF_TK','MMF_TKE','MMF_TKES' \n")
   file.write('\n')
   file.write(" fincl2    = 'PS','TS','PSL'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'PRECC','PRECSC'")
   file.write(             ",'PRECL','PRECSL'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")       # cloud water path
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   # file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'T500','T850','Q850'")
   file.write(             ",'U200','U850'")
   # file.write(             ",'V200','V850'")

   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRS','QRL'")
   # file.write(             ",'DTENDTQ','RELHUM'")
   # if 'MMF' in compset: 
      # file.write(          ",'MMF_DT','MMF_DQ','MMF_DQC'")           # CRM heating/moistening tendencies
      # file.write(          ",'MMF_TLS','MMF_QTLS' ")       # CRM large-scale forcing
      # file.write(             ",'MMF_DQ','MMF_DQC'")
      # file.write(             ",'MMF_DT','MMF_DQ','MMF_MCUP','MMF_MCDN'")
      # if 'L60_test' in case: file.write(",'MMF_SUBCYCLE_FAC','MMF_TK','MMF_TKE','MMF_TKES','MMF_TKEW' ")
      # file.write(             ",'CRM_T','CRM_U','CRM_W'")
      # file.write(             ",'CRM_QV','CRM_QC','CRM_QPC'")
   file.write('\n')
   # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write('\n')

   #-------------------------------------------------------
   # Other atmos namelist stuff
   #-------------------------------------------------------
   if 'atm_ntasks' in locals(): 
      if num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   if '.NO-MSA.' in case: file.write(' use_crm_accel = .false.\n')

   # file.write(" inithist = \'MONTHLY\' \n")
   file.write(" inithist = \'ENDOFRUN\' \n")

   if '.FVT_' in case: 
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='FVT':
            file.write(f' MMF_VT_wn_max = {int(p[1])} \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   if compset=='FC5AV1C-P': file.write(' use_hetfrz_classnuc = .false. \n')

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   # land namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # Copy the P3 data directory to the run directory
   #-------------------------------------------------------
   if '-P3' in compset:
      data_dir = f'{src_dir}/components/eam/src/physics/crm/scream/data'
      run_dir  = f'{top_dir}/scratch/{case}/run/'

      run_cmd(f'cp -R {data_dir} {run_dir}')

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
