#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3305'
home = os.getenv('HOME')
case_dir = f'{home}/E3SM/Cases'
src_dir  = f'{home}/E3SM/E3SM_SRC3'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
queue = 'regular'  # regular / debug 

#----------------------------------------
# select case here
#----------------------------------------
# compset,ne,npg = 'FC5AV1C-L',30,2            # E3SM.RGMA.ne30pg2_r05_oECv3.FC5AV1C-L.00
compset,ne,npg = 'FC5AV1C-H01A',120,2      # E3SM.RGMA.ne120pg2_r05_oECv3.FC5AV1C-H01A.00
# compset,ne,npg = 'F-MMF1',30,2             # E3SM.RGMA.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.RADNX_4.00
#----------------------------------------
#----------------------------------------

grid = f'ne{ne}pg{npg}_r05_oECv3'

# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5,12,'0:30:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',32,0,'4:00:00'

# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73,5*3,'6:00:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73,5,'6:00:00'

# current state of MMF case: STOP_N=73, RESUBMIT=6 - starting 5 day submissions w/ debug queue
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',(73-5)/2,1,'3:00:00'

# specify case name
case_list = ['E3SM','RGMA',grid,compset,'00']
if 'MMF' in compset: case_list = case_list[:4]+['CRMNX_64','CRMDX_2000','RADNX_4']+case_list[4:]
case = '.'.join(case_list)


land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
land_spinup_case = 'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01'
land_init_file = f'{land_init_path}/{land_spinup_case}.clm2.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

atm_ntasks = 10800

num_dyn = ne*ne*6

# use 20 min physics time step for all low-res cases
if 'MMF' in compset and ne==4  : dtime = 20*60
if 'MMF' in compset and ne==30 : dtime = 20*60
if 'FC5' in compset and ne==30 : dtime = 20*60

if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC ; print(f'\n{msg}')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   run_cmd(f'{cmd} -case {case_dir}/{case} -compset {compset} -res {grid}')

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}/')
if config : 
   #-------------------------------------------------------
   if 'MMF' in compset:
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
         if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
         if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
   else:
      # make sure we are using RRTMGP and prescribed aerosols, which are not the default settings
      run_cmd('./xmlchange -id CAM_CONFIG_OPTS -val \" -phys cam5 -clubb_sgs -microphys mg2 '\
                                                   '-nlev 72 -clubb_sgs -rad rrtmgp -chem none \"')
   #-------------------------------------------------------
   # Set tasks and threads - disable threading for MMF
   if 'atm_ntasks' in locals(): 
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_CPL -val 1350 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_LND -val 1350 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_OCN -val 1200 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_ICE -val 1200 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_WAV -val 16 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_GLC -val 16 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTASKS_ROF -val 16 ')

   run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_CPL -val 2 ')
   run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_LND -val 2 ')
   # make sure threading is disabled in the atmosphere for the MMF
   if 'MMF' in compset:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')
   else:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 2 ')

   # Not sure why this isn't the same between resolutions but just set it here
   run_cmd('./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val 64 ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', 
                                    stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', 
                                    stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   file.write(' nhtfrq    = 0,-1,-3 \n')
   file.write(' mfilt     = 1,120,40 \n')
   file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
   if 'MMF' in case :
      file.write(          ",'SPQPEVP','SPMC','SPMCUP','SPMCDN','SPMCUUP','SPMCUDN'")
   file.write('\n')
   file.write(" fincl2    = 'PS','PSL','TS'")
   file.write(             ",'PRECC','PRECL'")                     # average precip rates
   file.write(             ",'PRECT:I','TMQ:I'")                   # instantaneous precip and CWV
   file.write(             ",'LHFLX','SHFLX'")                     # surface fluxes
   file.write(             ",'FSNT','FLNT'")                       # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                       # net sfc heating rates
   file.write(             ",'FSNTC','FLNTC'")                     # clear sky rates for CRE
   file.write(             ",'TGCLDLWP','TGCLDIWP'")               # liq/ice water path
   file.write(             ",'TAUX','TAUY'")                       # surface stress
   file.write(             ",'TREFHT','QREFHT','QFLX'")            # Reference height T/q
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   if 'MMF' in case :
      file.write(          ",'CRM_PREC:I'")                        # snapshot of CRM precip
   file.write('\n')
   file.write(" fincl3lonlat = '130w:30w_10n:60n' \n")
   file.write(" fincl3    =  'T','Q','Z3'")                        # 3D energy components
   file.write(             ",'U','V','OMEGA'")                     # 3D velocity components
   file.write(             ",'QRL','QRS'")                         # 3D radiative heating
   file.write(             ",'CLDLIQ','CLDICE'")                   # 3D cloud fields
   file.write('\n')
   #------------------------------
   # Prescribed aerosols
   if "chem none" in cam_config_opts :
      prescribed_aero_path = din_loc_root+'/atm/cam/chem/trop_mam/aero'
      prescribed_aero_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
      file.write(f' use_hetfrz_classnuc      = .false. \n')
      file.write(f' aerodep_flx_datapath     = \'{prescribed_aero_path}\' \n')
      file.write(f' aerodep_flx_file         = \'{prescribed_aero_file}\' \n')
      file.write(f' aerodep_flx_type         = \'CYCLICAL\' \n')
      file.write(f' aerodep_flx_cycle_yr     = 01 \n')
      file.write(f' prescribed_aero_datapath = \'{prescribed_aero_path}\' \n')
      file.write(f' prescribed_aero_file     = \'{prescribed_aero_file}\' \n')
      file.write(f' prescribed_aero_type     = \'CYCLICAL\' \n')
      file.write(f' prescribed_aero_cycle_yr = 01 \n')
      # disable linear photochemistry
      file.write(' linoz_data_file = \'\' \n')
      file.write(' linoz_data_path = \'\' \n')
      # constant hydrometeor number
      file.write(' micro_do_nccons = .true. \n')
      file.write(' micro_do_nicons = .true. \n')
      file.write(' micro_nccons    = 70.0D6 \n')
      file.write(' micro_nicons    = 0.0001D6 \n')
   #------------------------------
   # Other namelist stuff
   if 'dtime' in locals(): 
      if ne==30 and dtime==(20*60): file.write(" rsplit    = 2 \n")
   file.write(f' dyn_npes = {num_dyn} \n')   # limit dynamics tasks
   file.write(" inithist = \'YEARLY\' \n")   # write cami files yearly
   # set the CRM mean-state acceleration
   if 'MMF' in compset: 
      file.write( ' srf_flux_avg = 1 \n')    # sfc flux smoothing for MMF stability
      file.write(f' crm_accel_factor = 4 \n')
   file.close()
   #-------------------------------------------------------
   # CLM namelist
   #-------------------------------------------------------
   nfile = 'user_nl_clm'
   file = open(nfile,'w')
   if 'land_init_file' in locals():
      file.write(f' finidat = \'{land_init_file}\' \n')
   file.write(" hist_nhtfrq = 0,-1 \n")
   file.write(" hist_mfilt  = 1,120 \n")
   file.write(" hist_fincl2 = 'SOILWATER_10CM','SNOW'")
   file.write(              ",'QINTR','QDRIP','QH2OSFC'")
   file.write(              ",'QTOPSOIL','QINFL','QDRAI'")
   file.write(              ",'QOVER','QRUNOFF','QSOIL' ")
   file.write(              ",'QVEGE','QVEGT' ")
   file.write('\n')
   file.close()
   #-------------------------------------------------------
   # Modify area tolerance for pg2
   #-------------------------------------------------------
   if ne==120 and npg==2 : run_cmd('./xmlchange -file env_run.xml  EPS_AGRID=1e-11' )
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # run_cmd('./xmlchange -file env_run.xml  PIO_TYPENAME=netcdf' )
   run_cmd('./xmlchange -file env_run.xml  PIO_TYPENAME=pnetcdf' )

   # run_cmd(f'./xmlchange -file env_run.xml -id BFBFLAG -val FALSE')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

print(f'\n  case : {case}\n')  # Print the case name again
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
