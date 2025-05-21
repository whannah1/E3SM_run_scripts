#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310' # SciDAC QBO project
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => maint-2.1

# clean        = True
newcase      = True
# config       = True
# build        = True
# submit       = True
# continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:10:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',365,10-1,'6:00:00'

num_nodes = 32; ne,npg,grid = 30,2,'ne30pg2_EC30to60E2r2'

### select case to run
compset='F20TR-MMF1'; nlev=64;crm_nz=54;case = '.'.join(['E3SM','2023-SCIDAC-TEST',grid,compset,f'L{nlev}'])
# compset='F20TR-MMF1'; nlev=72;crm_nz=60;case = '.'.join(['E3SM','2023-SCIDAC',grid,compset,f'L{nlev}'])
# compset='F20TR'     ; nlev=72;         ;case = '.'.join(['E3SM','2023-SCIDAC',grid,compset,f'L{nlev}'])
# compset='F20TR'     ; nlev=80;         ;case = '.'.join(['E3SM','2023-SCIDAC',grid,compset,f'L{nlev}'])

if debug_mode: case += '.debug'

#---------------------------------------------------------------------------------------------------
# Set input data paths
#---------------------------------------------------------------------------------------------------
init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'
if 'MMF' in compset:
   arch = 'GNUGPU'
   if nlev==64: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.L64_c20230819.nc'
   if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.L72_c20230819.nc'
else:
   arch = 'GNUCPU'
   if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.nc'
   if nlev==80: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'

init_path_lnd = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
init_case_lnd = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.2010-01-01'
init_file_lnd = f'{init_path_lnd}/{init_case_lnd}.elm.r.2010-01-01-00000.nc'
data_path_lnd = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
data_file_lnd = f'{data_path_lnd}/surfdata_ne30pg2_simyr2010_c210402.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes

if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' --project {acct} '
   cmd += f' --walltime {walltime} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   # # Copy this run script into the case directory
   # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   # if specifying ncdata, do it here to avoid an error message
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
   # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
   #-------------------------------------------------------
   # PE layout mods from Noel
   if 'CPU' in arch: cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
   if 'GPU' in arch: cpl_stride = 4; cpl_ntasks = atm_ntasks / cpl_stride
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
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
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-3,-24 \n')
   file.write(' mfilt     = 1,40,5 \n')
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
   # file.write(          ",'CLDLIQ','CLDICE'")                  # (forgot to enable this)
   file.write(          ",'UTGWSPEC','BUTGWSPEC','UTGWORO','BTAUE','BTAUW'")   # fields sugested by Yaga
   file.write(          ",'BUTEND1','BUTEND2','BUTEND3','BUTEND4','BUTEND5'") # Beres U-tendency
   # Beres tau at each phase speed
   file.write(          ",'BTAUXSp00','BTAUXSp01','BTAUXSp02','BTAUXSp03','BTAUXSp04'")
   file.write(                      ",'BTAUXSp05','BTAUXSp06','BTAUXSp07','BTAUXSp08'") 
   file.write(                      ",'BTAUXSp09','BTAUXSp10','BTAUXSp11','BTAUXSp12'")
   file.write(                      ",'BTAUXSp13','BTAUXSp14','BTAUXSp15','BTAUXSp16'")
   file.write(                      ",'BTAUXSp17','BTAUXSp18','BTAUXSp19','BTAUXSp20'")
   file.write(                      ",'BTAUXSp21','BTAUXSp22','BTAUXSp23','BTAUXSp24'")
   file.write(                      ",'BTAUXSp25','BTAUXSp26','BTAUXSp27','BTAUXSp28'")
   file.write(                      ",'BTAUXSp29','BTAUXSp30','BTAUXSp31','BTAUXSp32'")
   file.write(                      ",'BTAUXSn01','BTAUXSn02','BTAUXSn03','BTAUXSn04'")
   file.write(                      ",'BTAUXSn05','BTAUXSn06','BTAUXSn07','BTAUXSn08'")
   file.write(                      ",'BTAUXSn09','BTAUXSn10','BTAUXSn11','BTAUXSn12'")
   file.write(                      ",'BTAUXSn13','BTAUXSn14','BTAUXSn15','BTAUXSn16'")
   file.write(                      ",'BTAUXSn17','BTAUXSn18','BTAUXSn19','BTAUXSn20'")
   file.write(                      ",'BTAUXSn21','BTAUXSn22','BTAUXSn23','BTAUXSn24'")
   file.write(                      ",'BTAUXSn25','BTAUXSn26','BTAUXSn27','BTAUXSn28'")
   file.write(                      ",'BTAUXSn29','BTAUXSn30','BTAUXSn31','BTAUXSn32'")
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
   # h2 is mainly for calculating TEM 
   file.write(" fincl3 = 'PS','TS','PSL'")
   file.write(          ",'T','Q','Z3'")                       # 3D thermodynamic budget components
   file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
   file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
   file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
   file.write(          ",'UTGWORO','UTGWSPEC','BUTGWSPEC'")   # gravity wave U tendencies
   file.write('\n')

   # ,'MSKtem','VTH2d','UV2d','UW2d','U2d','V2d','TH2d','W2d' # FV TE terms
   
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   # file.write(f' cosp_lite = .true. \n')
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write(" inithist = \'ENDOFRUN\' \n")
   file.close()
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'init_file_lnd' in locals() or 'data_file_lnd' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'init_file_lnd' in locals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
      if 'data_file_lnd' in locals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
      # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
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
