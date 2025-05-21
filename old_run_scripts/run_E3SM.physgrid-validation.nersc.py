#!/usr/bin/env python
# main ne30 runs hash = ????
# extra ne45pg2 hash = 10243edce395689224cb162f34193f6771327537
# extra physgrd runs for tendency power spectra = 65b8ff37cc1a33913eac828b9677758af46a7c9b

#---------------------------------------------------------------------------------------------------
# grid changes needed for extra power spectrum runs
#---------------------------------------------------------------------------------------------------
# +++ b/cime_config/config_grids.xml
# @@ -1281,7 +1281,27 @@
#        <grid name="rof">r05</grid>
#        <grid name="glc">null</grid>
#        <grid name="wav">null</grid>
# -      <mask>gx1v6</mask>
# +      <mask>oEC60to30v3</mask>
# +    </model_grid>
# +
# +    <model_grid alias="ne30pg3_ne30pg3" compset="(DOCN|XOCN|SOCN|AQP1)">
# +      <grid name="atm">ne30np4.pg3</grid>
# +      <grid name="lnd">ne30np4.pg3</grid>
# +      <grid name="ocnice">ne30np4.pg3</grid>
# +      <grid name="rof">r05</grid>
# +      <grid name="glc">null</grid>
# +      <grid name="wav">null</grid>
# +      <mask>oEC60to30v3</mask>
# +    </model_grid>
# +
# +    <model_grid alias="ne30pg4_ne30pg4" compset="(DOCN|XOCN|SOCN|AQP1)">
# +      <grid name="atm">ne30np4.pg4</grid>
# +      <grid name="lnd">ne30np4.pg4</grid>
# +      <grid name="ocnice">ne30np4.pg4</grid>
# +      <grid name="rof">r05</grid>
# +      <grid name="glc">null</grid>
# +      <grid name="wav">null</grid>
# +      <mask>oEC60to30v3</mask>
#      </model_grid>

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os,datetime
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305 / e3sm
top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC1/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'regular'  # regular / debug


if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
else:
   # stop_opt,stop_n,resub,walltime = 'ndays',73,(4*5-1),'8:00:00'
   stop_opt,stop_n,resub,walltime = 'ndays',73*2,4,'6:00:00'
   # if 'conus' in case: walltime = '13:00:00'
   # if 'conus' in case: stop_opt,stop_n,resub,walltime = 'ndays',73,25,'6:00:00' # 5+ years
   # if 'PGVAL-TIMING' in case: stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'

compset = 'F2010SC5-CMIP6'    # F2010SC5-CMIP6 / FC5AV1C-L
# compset = 'F-EAM-AQP1'


# atm_ntasks, nthrds = 5400, 2
atm_ntasks, nthrds = 2700, 2

ne,npg = 30,0
# ne,npg = 30,2
# ne,npg = 30,3
# ne,npg = 30,4

# ne,npg = 45,2

#-----------------------------------
# Timing runs
#-----------------------------------
# atm_ntasks = 5400; ne,npg = 30,0
# atm_ntasks = 5400; ne,npg = 30,2
# atm_ntasks = 5400; ne,npg = 30,3
# atm_ntasks = 5400; ne,npg = 30,4

# atm_ntasks = 2700; ne,npg = 30,0
# atm_ntasks = 2700; ne,npg = 30,2
# atm_ntasks = 2700; ne,npg = 30,3
# atm_ntasks = 2700; ne,npg = 30,4

# atm_ntasks = 1350; ne,npg = 30,0
# atm_ntasks = 1350; ne,npg = 30,2
# atm_ntasks = 1350; ne,npg = 30,3
# atm_ntasks = 1350; ne,npg = 30,4
#-----------------------------------
#-----------------------------------


if ne>0:
   res = 'ne'+str(ne)+'pg'+str(npg)
   res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
else:
   if npg==0: res = 'conusx4v1'
   if npg==2: res = 'conusx4v1pg2'

if 'AV1C' in compset : grid = f'{res}_{res}'
if '2010' in compset : grid = f'{res}_r05_oECv3'
if 'AQP1' in compset : grid = f'{res}_{res}'
# grid = f'{res}_{res}'

git_hash = sp.check_output(f'cd {src_dir}; git log -n1 --format=format:"%H"',shell=True,universal_newlines=True)
# git_hash = 'cbe53b' # main ne30 and RRM runs
# git_hash = '' # ne45pg2 case for spectral analysis

#-----------------------------------
#-----------------------------------

### original runs
# if 'E3SM_SRC1' in src_dir : case = '.'.join(['E3SM','PGVAL',grid,compset,f'master-{git_hash[-6:]}'])
# if 'E3SM_SRC2' in src_dir : case = '.'.join(['E3SM','PGVAL',grid,compset,f'maint1-{git_hash[-6:]}'])

# case = '.'.join(['E3SM','PGVAL',grid,compset,f'master-{git_hash[-6:]}'])

### timing runs (AQP1)
# case = '.'.join(['E3SM','PGVAL-TIMING',grid,compset,f'master-{git_hash[-6:]}',f'ntask_{atm_ntasks}',f'nthrds_{nthrds}'])

### Runs for dynamics forcing spectra
case = '.'.join(['E3SM','PGVAL-XTRA',grid,compset,f'master-{git_hash[-6:]}'])

#-----------------------------------
#-----------------------------------


land_init_path = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files'
if '_r05_oECv3' in grid:      land_init_file = f'{land_init_path}/CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01.clm2.r.2010-01-01-00000.nc'
if grid=='ne45pg2_r05_oECv3': land_init_file = f'{land_init_path}/CLM_spinup.ICRUCLM45.ne45pg2_r05_oECv3.20-yr.2010-10-01.clm2.r.2005-10-01-00000.nc'
# if grid=='ne30_ne30': 
#    land_init_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/initdata_map/'
#    land_init_file = 'clmi.ICLM45BC.ne30_ne30.d0241119c.clm2.r.nc'

if 'PGVAL-XTRA' in case: del land_init_file

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# num_dyn = ne*ne*6

# if ne==30: atm_ntasks = 5400
# if ne==45: atm_ntasks = 5400
# if 'conusx4v1' in res: atm_ntasks = 9600
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print('\n'+msg+'\n')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += f' -compset {compset}'
   cmd += f' -res {grid}'
   cmd += f' --pecount {atm_ntasks}x1'
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

   if npg>0:
      num_dyn = ne*ne*6
      pcols = (npg * npg * num_dyn + (atm_ntasks*nthrds) - 1) / (atm_ntasks*nthrds)
      if (pcols > 40): pcols = 16
      if (pcols > 20): pcols = (pcols + 1) / 2
      pcols = int(pcols)
      run_cmd(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols {pcols} \"')

   # if npg==2: run_cmd(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols 8 \"')
   # if npg==3: run_cmd(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols 16 \"') 
   # if npg==4: run_cmd(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols 16 \"') 
      
   # for pg3 and pg4 these need to be set explicitly since there's no default PE layout
   cmd = './xmlchange -file env_mach_pes.xml '
   cmd += f' NTASKS_ATM={atm_ntasks}'
   cmd += ',NTASKS_LND=1350,NTASKS_CPL=1350,NTASKS_OCN=1200,NTASKS_ICE=1200'
   cmd += ',NTASKS_ROF=32,NTASKS_WAV=32,NTASKS_GLC=32,NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   run_cmd(f'./xmlchange -file env_mach_pes.xml NTHRDS_ATM={nthrds},NTHRDS_CPL={nthrds},NTHRDS_LND=1')

   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

   run_cmd('./xmlquery NTASKS NTHRDS')
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
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', 
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   # nfile = 'user_nl_cam'
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   if 'PGVAL-TIMING' not in case: 
      file.write(' nhtfrq    = 0,-3,-24 \n')
      file.write(' mfilt     = 1,40,5 \n')
      file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
      if 'FC5AV1C-L' not in compset :
         file.write(          ",'DYN_T','DYN_Q','DYN_U','DYN_OMEGA','DYN_PS'")
      file.write('\n')
      file.write(" fincl2    = 'PS','TS'")
      file.write(             ",'PRECT','TMQ','LHFLX','SHFLX'")
      file.write(             ",'FSNT','FLNT','FLNS','FSNS'") # Net TOM and sfc heating rates
      file.write(             ",'TGCLDLWP','TGCLDIWP'")    
      file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
      file.write(             ",'OMEGA850','OMEGA500'")
      file.write(             ",'T500','T850','Q850'")
      file.write(             ",'U200','U850','V200','V850'")
      file.write('\n')
      file.write(" fincl3    = 'T','Q','U','V','OMEGA'")
      file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(             ",'PTTEND','DTCOND','DCQ'")     # 3D physics tendencies
      file.write(             ",'PTTEND','DYN_PTTEND'")     # 3D physics tendencies
      if 'FC5AV1C-L' not in compset :
         file.write(          ",'DYN_T','DYN_Q','DYN_U','DYN_V','DYN_OMEGA' ")
      file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   file.write(" inithist = \'YEARLY\' \n") # ENDOFRUN
   file.close()
   
   if 'land_init_file' in locals():
      # nfile = 'user_nl_clm'
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_file}\' \n')
      file.close()

   # Turn off CICE history files
   nfile = 'user_nl_cice'
   file = open(nfile,'w')
   file.write(" histfreq = 'x','x','x','x','x' \n")
   file.close()

   if 'conus' in res: 
      # run_cmd('./xmlchange -file env_run.xml EPS_AAREA=5.0e-7' )  # default=1.0e-07
      run_cmd('./xmlchange -file env_run.xml EPS_AGRID=3.e-10' )  # default=1.e-12
      run_cmd('./xmlchange -file env_run.xml EPS_FRAC=3e-2' )     # default=1e-2
   else:
      # run_cmd('./xmlchange -file env_run.xml EPS_AGRID=1e-11' )
      run_cmd('./xmlchange -file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'PGVAL-TIMING' in case: run_cmd(f'./xmlchange REST_OPTION=never')

   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   run_cmd(f"./xmlchange CONTINUE_RUN={'TRUE' if continue_run else 'FALSE'}")
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 