#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC1/' # branch = whannah/mmf/chx-detection-exp

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
queue = 'regular'  # regular / debug 


# compset,nlev,dcape_flag    = 'FC5AV1C-L',72,True
# compset,nlev,dcape_flag    = 'FC5AV1C-L',72,False
compset,nlev,crm_nz,crm_dt = 'F-MMF1'   ,50,48,10

ne,npg  = 30,2
rad_nx  = 4
crm_dx  = 2000
crm_nx  = 64
crm_ny  = 1

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_{res}'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',2,0,'0:30:00'
else:
   if 'MMF' in compset: stop_opt,stop_n,resub,walltime = 'ndays',73,5*4-1,'6:00:00'
   if 'FC5' in compset: stop_opt,stop_n,resub,walltime = 'ndays',73,5*4-1,'6:00:00'


case_list = ['E3SM','CHX',grid,compset]


# if 'MMF' in compset:
   # case_list.append(f'NLEV_{nlev}')
   # case_list.append(f'NXY_{crm_nx}x{crm_ny}')

if 'FC5' in compset: 
   if not dcape_flag: case_list.append('no_dcape')

case_list.append('00')

case='.'.join(case_list)


# case = case+'.debug-on'
# case = case+'.checks-on'

#---------------------------------------------------------------------------------------------------
# Specify input files
#---------------------------------------------------------------------------------------------------

hiccup_path = '/global/cscratch1/sd/whannah/HICCUP/data'
if nlev==50: init_file_atm = f'{hiccup_path}/HICCUP.cami_mam3_Linoz_ne{ne}np4_L50_c20210623.nc'

land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
# if grid=='ne30pg2_r05_oECv3': land_init_file = f'{land_init_path}/CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01.clm2.r.2010-01-01-00000.nc'
if grid=='ne30pg2_ne30pg2': land_init_file = f'{land_init_path}/CLM_spinup.ICRUELM.ne30pg2_ne30pg2.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

if 'MMF' in compset: dtime = 20*60           # use 20 min for MMF (default is 30 min for E3SM @ ne30)

if 'dtime' in locals(): ncpl = 86400/dtime

if 'atm_ntasks' not in locals():
   if ne==30: atm_ntasks = 5400

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
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   # cmd += ' --pecount '+str(num_dyn)+'x1'
   if '.gnu.' in case : cmd = cmd + ' --compiler gnu '
   if '.pgi.' in case : cmd = cmd + ' --compiler pgi '
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   # (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
   #                                   stdout=sp.PIPE, shell=True, \
   #                                   universal_newlines=True).communicate()
   # config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # if changing vertical levels make sure to update ncdata here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_dx {crm_dx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt}   \" ')
      # if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Specify vertical grid
   if 'MMF' in compset:
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {nlev} -crm_nz {crm_nz} \" ')
   else:
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {nlev} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.FLUX_BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS '
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'

   # CRM variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   if 'debug-on' in case and 'MMFXX' in compset : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------  
   # Set tasks and threads - disable threading for MMF

   if 'atm_ntasks' in locals(): 
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
   
   if 'MMF' in compset: run_cmd(f'./xmlchange -file env_mach_pes.xml NTHRDS_ATM=1 ')
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
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if stop_opt=='nstep':
      file.write(' nhtfrq    = 0,1 \n')
      file.write(f' mfilt     = 1,{stop_n} \n')
   else:
      file.write(' nhtfrq    = 0,-1,-3 \n')
      file.write(' mfilt     = 1,24,8 \n')

   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'T850','Q850'")
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   
   file.write('\n')
   file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   if 'MMF' in compset: 
      file.write(          ",'CRM_QV:I','CRM_QC:I','CRM_U:I'")
   file.write('\n')

   #------------------------------
   # Other ATM namelist stuff
   #------------------------------

   if '.no_dcape' in case:
      file.write(f' zmconv_trigdcape_ull         = .false. \n')
      file.write(f' zmconv_trig_dcape_only       = .false. \n')
      file.write(f' zmconv_trig_ull_only         = .true. \n')


   if 'atm_ntasks' in locals(): 
      if num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')   
   
   # file.write(" inithist = \'MONTHLY\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')   

   # dycor parameters when using shorter time step
   if 'dtime' in locals():
      if dtime==20*60 and ne==30 : 
         file.write(f'dt_tracer_factor = 4 \n')
         file.write(f'dt_remap_factor = 4 \n')
         file.write(f'hypervis_subcycle_q = 4 \n')
         file.write(f'se_tstep = 300 \n')

   # close atm namelist file
   file.close()
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
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
