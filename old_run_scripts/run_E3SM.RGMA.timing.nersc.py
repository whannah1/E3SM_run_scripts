#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3305'    # m3312 / m3305
top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC3/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'regular'  # regular / debug 

compset,ne,npg = 'F-MMF1',30,2 
# compset,ne,npg = 'FC5AV1C-L',30,2
# compset,ne,npg = 'FC5AV1C-H01A',120,2 


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_r05_oECv3'   # f'{res}_r05_oECv3' / f'{res}_{res}'


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',5,0,'3:00:00'

atm_ntasks = 10800 # 5400 / 10800 / 8000
# nthrds = 2

# case_num = '00' # initial tests - 1 day
# case_num = '01' # switch to default pcols=16 and nthrds=2
# case_num = '02' # same as 01 + 5 days and bigger CRM + RRTMGP and prescribed aero
# case_num = '03' # same as 02, but switch to branch with single aerosol optics modification
case_num = '04' # new tests that match main runs but varying the CRM time step and MSA

if case_num=='03': src_dir  = top_dir+'E3SM_SRC2/'

case_list = ['E3SM','RGMA-timing',grid,compset,f'ntasks_{atm_ntasks}',case_num]
case_list.append('hist_ouput')
# if 'MMF' in compset: case_list = case_list[:3]+['CRMNX_64','RADNX_4','MSA_4']+case_list[4:]
if 'MMF' in compset: case_list = case_list[:4]+['CRMNX_64','CRMDX_2000','CRMDT_6','RADNX_4','MSA_3']+case_list[4:]
case = '.'.join(case_list)


# if 'nthrds' in locals():case = '.'.join(['E3SM','RGMA-timing',grid,compset,f'ntasks_{atm_ntasks}',f'nthrds_{nthrds}',case_num])
# case = case+'.debug-on'
# case = case+'.checks-on'

land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
land_spinup_case = 'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01'
land_init_file = f'{land_init_path}/{land_spinup_case}.clm2.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

if 'MMF' in compset and ne==4  : dtime = 20*60
if 'MMF' in compset and ne==30 : dtime = 20*60
if 'FC5' in compset and ne==30 : dtime = 20*60
# if 'FC5' in compset and ne==120: dtime = 5*60
# if ne==120: dtime = 5*60
if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

# if 'MMF' in compset and ne==30 : atm_ntasks = 10800
# if 'FC5' in compset and ne==120: atm_ntasks = 10800
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
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
   # Adjust pcols for grid
   # if npg==2: run_cmd(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols 8 \"')
   #-------------------------------------------------------
   # explicitly specify rad option
   # if '.RRTMG.'  in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmg \"')
   # if '.RRTMGP.' in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
   if 'MMF' in compset:
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx 128 \" ')
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad 8 \" ')
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
         if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
         if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
         if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
   else:
      run_cmd('./xmlchange -id CAM_CONFIG_OPTS -val \" -phys cam5 -clubb_sgs -microphys mg2 '\
                                                   '-nlev 72 -clubb_sgs -rad rrtmgp -chem none \"')
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -chem none \"')
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   # params = [p.split('_') for p in case.split('.')]
   # for p in params:
   #    if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
   #    if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.FLUX-BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS '
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)
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

   if 'MMF' in compset:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')
   else:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 2 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_CPL -val 2 ')
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_LND -val 2 ')
      # if 'nthrds' in locals():
      #    run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val {nthrds} ')
      #    run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTHRDS_CPL -val {nthrds} ')
      #    run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTHRDS_LND -val {nthrds} ')
      # else:
      #    run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 4 ')
      #    run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_CPL -val 4 ')
      #    run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_LND -val 4 ')
   #-------------------------------------------------------
   # Switch the dycore
   if '.THETA-L.' in case: os.system('./xmlchange CAM_TARGET=theta-l ' )
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
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', 
                                     stdout=sp.PIPE, shell=True,
                                     universal_newlines=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', 
                                     stdout=sp.PIPE, shell=True, 
                                     universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if 'hist_ouput' in case:
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
   #------------------------------
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
   #------------------------------
   file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   if 'dtime' in locals(): 
      if ne==30 and dtime==(20*60): file.write(" rsplit    = 2 \n")

   # file.write(" inithist = \'MONTHLY\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')
   
   # if ne==120 and npg==2 : 
   #    file = open('user_nl_cpl','w') 
   #    file.write(' eps_agrid = 1e-11 \n')
   #    file.close()

   if 'MMF' in compset:
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='MSA': file.write(f' crm_accel_factor = {p[1]} \n')

   file.close()

   #-------------------------------------------------------
   # CLM namelist
   #-------------------------------------------------------   
   nfile = 'user_nl_clm'
   file = open(nfile,'w')
   if 'land_init_file' in locals():
      file.write(f' finidat = \'{land_init_file}\' \n')
   if 'hist_ouput' in case:
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
   # Modify aera tolerance for pg2
   #-------------------------------------------------------
   if ne==120 and npg==2 : run_cmd('./xmlchange -file env_run.xml  EPS_AGRID=1e-11' )

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # disable restart files
   run_cmd(f'./xmlchange REST_OPTION=never')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')


# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
