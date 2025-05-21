#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3305'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'regular'  # regular / debug

compset = 'FC5AV1C-L'
# compset = 'F2010SC5-CMIP6'
# compset = 'F-MMF1'
# compset = 'F-MMF2'

# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
if queue=='debug'  : 
   # stop_opt,stop_n,resub,walltime = 'nsteps',20,0,'0:30:00'
   if compset=='FC5AV1C-L': stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
if queue=='regular': 
   if compset=='FC5AV1C-L': stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00:00'
   if compset=='F-MMF1'   : stop_opt,stop_n,resub,walltime = 'ndays',5,0,'3:00:00'
   if compset=='F-MMF2'   : stop_opt,stop_n,resub,walltime = 'ndays',5,0,'10:00:00'
  
ne,npg = 30,0
res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_r05_oECv3'

iyr,imn,idy = 2011,5,20
init_date = f'{iyr}-{imn:02d}-{idy:02d}'
init_file_dir = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/'
init_file_sst = f'HICCUP.sst_noaa.{init_date}.nc'

case = '.'.join(['E3SM','HINDCAST',init_date,grid,compset,'00']) 

init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L72.nc'

# case = case+'_debug-on'
# case = case+'_checks-on'

# Specify land initial condition file
land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2011-05-01'
land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/'   # general init file staging
land_init_file = f'{land_init_path}/{land_init_case}.clm2.r.{init_date}-00000.nc'

if grid=='ne30_r05_oECv3': land_init_file = ''

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# num_dyn = ne*ne*6
# if ne==120: dtime = 5*60
if 'dtime' in locals(): ncpl = 86400 / dtime

# Enforce max node limit on debug queue
# if queue=='debug' and num_dyn>(64*32) : num_dyn = 64*32
# if num_dyn==0 : num_dyn = 4000

if ne== 30: atm_ntasks = 5400
if ne==120: atm_ntasks = 5400
#---------------------------------------------------------------------------------------------------
# Define run command
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print('\n'+msg+'\n')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
if newcase :
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # Adjust radiative columns
   # if 'F-MMF' in compset : 
   #    os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -crm_nx_rad 4 \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks and threads - disable threading for SP
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
   #-------------------------------------------------------
   # Switch the dycore?
   if '.THETA-L.' in case: os.system('./xmlchange CAM_TARGET=theta-l ' )
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

   run_cmd('./xmlquery NTASKS NTHRDS')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : os.system('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : os.system('./case.build --clean')
   os.system('./case.build')
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
   nfile = 'user_nl_cam'
   file = open('user_nl_cam','w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,8 \n')
   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT'")
   file.write(             ",'TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'Z100','Z500','Z700'")
   file.write(             ",'T500','T850','Q850'")
   file.write(             ",'T850:I','Q850:I'")                 # 3D radiative heating profiles
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(             ",'PTTEND','DTCOND','DCQ'")                 # 3D radiative heating profiles
   # if 'use_SPCAM' in cam_config_opts or 'use_MMF' in cam_config_opts :
   #    file.write(         ",'CRM_PREC'")
   #    file.write(         ",'CRM_QRAD'")
   #    file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
   #    file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
   #    file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
   #    file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
   #    file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
   #    file.write(         ",'SPTKE','SPTKES'")
   #    file.write(         ",'CRM_T','CRM_U'")
   #    file.write(         ",'SPMC','MU_CRM'")
   # if 'ESMT' in case:
   #    # file.write(         ",'SPDT','SPDQ'")
   #    file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
   #    file.write(",'U_ESMT','V_ESMT'")
   #    # file.write(",'UCONVMOM','VCONVMOM'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')
   file.close()

   if ne==120 and npg==2 : os.system('./xmlchange -file env_run.xml      EPS_AGRID=1e-11' )
   
   file = open('user_nl_clm','w')
   file.write(' hist_nhtfrq = 0,-3 \n')
   file.write(' hist_mfilt  = 1,24 \n')
   file.write(" hist_fincl2 = 'TBOT','QTOPSOIL','H2OSOI'")
   # file.write(              ",'FGEV','FCEV','FCTR','Rnet'")
   # file.write(              ",'FSH_V','FSH_G','TLAI','ZWT','ZWT_PERCH'")
   # file.write(              ",'QSOIL','QVEGT','QCHARGE'")
   if land_init_file is not None: file.write(f' finidat = \'{land_init_file}\' \n')
   file.close()

   #-------------------------------------------------------
   # Special stuff for hindcast mode
   #-------------------------------------------------------
   os.system(f'./xmlchange -file env_run.xml  RUN_STARTDATE={init_date}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_DATA_FILENAME={init_file_dir}{init_file_sst}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_ALIGN={iyr}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_START={iyr}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_END={iyr+1}')
   # os.system('./xmlchange -file env_build.xml CALENDAR=GREGORIAN)

   # Specify the initial condition file
   file = open('user_nl_cam','a') 
   file.write(f' ncdata = \'{init_file_dir}{init_file_atm}\'\n')
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
# Done!
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') # Print the case name again
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
