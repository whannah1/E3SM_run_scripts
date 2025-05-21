#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'    # m3312 / m3305 / m4310

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC0/' # master as of 2023-01-19

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

queue = 'regular'  # regular / debug 

arch = 'GNUCPU' # GNUCPU / GNUGPU / CORI / CORIGNU

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',365,0,'5:00:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73,0,'2:00:00'

# compset,ne,npg,grid = 'F2010',30,2,'ne30pg2_EC30to60E2r2'
# compset,ne,npg,grid = 'F2010-CICE',16,2,'ne16pg2_ne16pg2'; num_nodes=4
compset,ne,npg,grid = 'F2010',16,2,'ne16pg2_oECv3'; num_nodes=8

nlev= 72;         case='.'.join(['E3SM','QBO-TEST-00',compset,f'ne{ne}pg{npg}',f'L{nlev}'])
# nlev= 72; nsm=40; case='.'.join(['E3SM','QBO-TEST-00',compset,f'ne{ne}pg{npg}',f'L{nlev}-nsu{nsm:02d}']) # smoothing in upper levels
# nlev= 80; nsm=40; case='.'.join(['E3SM','QBO-TEST-00',compset,f'ne{ne}pg{npg}',f'L{nlev}-rsu{nsm:02d}']) # smoothing + refinement

atm_init_scratch = '/pscratch/sd/w/whannah/HICCUP/data'
lnd_init_scratch = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch'

#---------------------------------------------------------------------------------------------------
if ne==16:
   if 'L72-nsu' in case: 
      atm_init_file = f'{atm_init_scratch}/cami_mam3_Linoz_ne16np4_L72_c160614.L72_nsmooth_40_upper_lev_only_c20230131.nc'
   else:
      atm_init_file = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne16np4_L72_c160614.nc'
   if grid=='ne16pg2_ne16pg2': lnd_init_file = f'{lnd_init_scratch}/ELM_spinup.ICRUELM.ne16pg2_ne16pg2.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   if grid=='ne16pg2_oECv3'  : lnd_init_file = f'{lnd_init_scratch}/ELM_spinup.ICRUELM.ne16pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   lnd_data_file = f'{lnd_init_scratch}/surfdata_ne16pg2_simyr2010_c230202.nc'
#---------------------------------------------------------------------------------------------------
def lnd_update_namelist():
   if 'lnd_init_file' in locals() or 'lnd_data_file' in globals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      if 'lnd_init_file' in globals(): file.write(f' finidat = \'{lnd_init_file}\' \n')
      if 'lnd_data_file' in globals(): file.write(f' fsurdat = \'{lnd_data_file}\' \n')
      file.close()
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch  : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch  : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
if arch=='CORI'   : max_mpi_per_node,atm_nthrds  = 64,1
if arch=='CORIGNU': max_mpi_per_node,atm_nthrds  = 64,1
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(clr.RED+"\nThis case already exists!\n"+clr.END)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CORI'   : cmd += f' -mach cori-knl -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CORIGNU': cmd += f' -mach cori-knl -compiler gnu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)

   # update mapping files
   if grid=='ne16pg2_oECv3':
      fmap_atm2ocn = '$SCRATCH/e3sm_scratch/init_scratch/maps/map_ne16pg2_to_oEC60to30v3_mono.20230201.nc'
      fmap_ocn2atm = '$SCRATCH/e3sm_scratch/init_scratch/maps/map_oEC60to30v3_to_ne16pg2_mono.20230201.nc'
      smap_atm2ocn = '$SCRATCH/e3sm_scratch/init_scratch/maps/map_ne16pg2_to_oEC60to30v3_bilin.20230201.nc'
   os.chdir(case_dir+case+'/')
   os.system(f'./xmlchange --file env_run.xml ATM2OCN_FMAPNAME={fmap_atm2ocn}')
   os.system(f'./xmlchange --file env_run.xml ATM2OCN_SMAPNAME={smap_atm2ocn}')
   os.system(f'./xmlchange --file env_run.xml ATM2OCN_VMAPNAME={smap_atm2ocn}')
   os.system(f'./xmlchange --file env_run.xml OCN2ATM_FMAPNAME={fmap_ocn2atm}')
   os.system(f'./xmlchange --file env_run.xml OCN2ATM_SMAPNAME={fmap_ocn2atm}')

#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

   #-------------------------------------------------------
   # if specifying ncdata, finidat, or fsurdat, do it here to avoid an error message
   if 'atm_init_file' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{atm_init_file}\' \n')
      file.close()
   lnd_update_namelist()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   #-------------------------------------------------------
   if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # fix domain file issue
   #-------------------------------------------------------
   os.system(f'./xmlchange --file env_run.xml ATM_DOMAIN_FILE=domain.lnd.ne16pg2_oEC60to30v3.230203.nc')
   os.system(f'./xmlchange --file env_run.xml LND_DOMAIN_FILE=domain.lnd.ne16pg2_oEC60to30v3.230203.nc')
   os.system(f'./xmlchange --file env_run.xml OCN_DOMAIN_FILE=domain.ocn.oEC60to30v3.230203.nc')
   os.system(f'./xmlchange --file env_run.xml ICE_DOMAIN_FILE=domain.ocn.oEC60to30v3.230203.nc')
   
   os.system(f'./xmlchange --file env_run.xml ATM_DOMAIN_PATH=/global/cfs/cdirs/m3312/whannah/init_files/domain_files')
   os.system(f'./xmlchange --file env_run.xml LND_DOMAIN_PATH=/global/cfs/cdirs/m3312/whannah/init_files/domain_files')
   os.system(f'./xmlchange --file env_run.xml OCN_DOMAIN_PATH=/global/cfs/cdirs/m3312/whannah/init_files/domain_files')
   os.system(f'./xmlchange --file env_run.xml ICE_DOMAIN_PATH=/global/cfs/cdirs/m3312/whannah/init_files/domain_files')
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,8 \n')
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
   file.write(          ",'UTGWSPEC','BUTGWSPEC','UTGWORO','BTAUE','BTAUW'")   # fields sugested by Yaga
   file.write(          ",'BUTEND1','BUTEND2','BUTEND3','BUTEND4','BUTEND5'") # Beres U-tendency
   # Beres tau at each phase speed
   # file.write(          ",'BTAUXSp00','BTAUXSp01','BTAUXSp02','BTAUXSp03','BTAUXSp04'")
   # file.write(                      ",'BTAUXSp05','BTAUXSp06','BTAUXSp07','BTAUXSp08'") 
   # file.write(                      ",'BTAUXSp09','BTAUXSp10','BTAUXSp11','BTAUXSp12'")
   # file.write(                      ",'BTAUXSp13','BTAUXSp14','BTAUXSp15','BTAUXSp16'")
   # file.write(                      ",'BTAUXSp17','BTAUXSp18','BTAUXSp19','BTAUXSp20'")
   # file.write(                      ",'BTAUXSp21','BTAUXSp22','BTAUXSp23','BTAUXSp24'")
   # file.write(                      ",'BTAUXSp25','BTAUXSp26','BTAUXSp27','BTAUXSp28'")
   # file.write(                      ",'BTAUXSp29','BTAUXSp30','BTAUXSp31','BTAUXSp32'")
   # file.write(                      ",'BTAUXSn01','BTAUXSn02','BTAUXSn03','BTAUXSn04'")
   # file.write(                      ",'BTAUXSn05','BTAUXSn06','BTAUXSn07','BTAUXSn08'")
   # file.write(                      ",'BTAUXSn09','BTAUXSn10','BTAUXSn11','BTAUXSn12'")
   # file.write(                      ",'BTAUXSn13','BTAUXSn14','BTAUXSn15','BTAUXSn16'")
   # file.write(                      ",'BTAUXSn17','BTAUXSn18','BTAUXSn19','BTAUXSn20'")
   # file.write(                      ",'BTAUXSn21','BTAUXSn22','BTAUXSn23','BTAUXSn24'")
   # file.write(                      ",'BTAUXSn25','BTAUXSn26','BTAUXSn27','BTAUXSn28'")
   # file.write(                      ",'BTAUXSn29','BTAUXSn30','BTAUXSn31','BTAUXSn32'")
   file.write('\n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECL'")
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
 
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   if 'atm_init_file' in locals(): file.write(f' ncdata = \'{atm_init_file}\' \n')

   # file.write(" inithist = \'ENDOFRUN\' \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   # close atm namelist file
   file.close()

   #-------------------------------------------------------
   lnd_update_namelist()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
