#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases'
src_dir  = f'{top_dir}/E3SM_SRC4' # whannah/atm/add-interpolated-btau-output

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 

arch = 'GNUCPU' # GNUCPU / GNUGPU
num_nodes=32

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:10:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'

compset,ne,npg,grid = 'F2010',30,2,'ne30pg2_oECv3'

case='.'.join(['E3SM','BTAU-TEST-00',compset,f'ne{ne}pg{npg}'])

### debugging options
if debug_mode: case += '.debug'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch  : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch  : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(tcolor.RED+"\nThis case already exists!\n"+tcolor.ENDC)

   # cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   # cmd += f' -compset {compset} -res {grid} '
   # # cmd += ' --pecount 5400x1'
   # run_cmd(cmd)

   cmd = src_dir+f'/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid} '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}')
if config : 
   #-------------------------------------------------------
   # # if specifying ncdata, do it here to avoid an error message
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_atm}\' \n')
   #    file.close()
   #-------------------------------------------------------
   # Run case setup
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
   file.write(' nhtfrq    = 0,-3,-6 \n')
   file.write(' mfilt     = 1,8,4 \n')
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

   for p in range(-32,32+1): 
      if p< 0: file.write(f",'BTAUXSn{np.abs(p):02d}'")
      if p>=0: file.write(f",'BTAUXSp{np.abs(p):02d}'")
   for l in ['_100mb','_50mb','_30mb','_10mb']:
      for p in range(-32,32+1): 
         if p< 0: file.write(f",'BTAUXSn{np.abs(p):02d}{l}'")
         if p>=0: file.write(f",'BTAUXSp{np.abs(p):02d}{l}'")


   file.write('\n')
   # file.write(" fincl2 = 'PS','TS','PSL'")
   # file.write(          ",'PRECT','TMQ'")
   # file.write(          ",'PRECC','PRECL'")
   # file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
   # file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   # file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # # variables for tracking stuff like hurricanes
   # file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   # file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(          ",'Z300:I','Z500:I'")
   # file.write(          ",'OMEGA850:I','OMEGA500:I'")
   # file.write(          ",'U200:I','V200:I'")
   # file.write('\n')
   # # h2 is mainly for calculating TEM 
   # file.write(" fincl3 = 'PS','TS','PSL'")
   # file.write(          ",'T','Q','Z3'")                      # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
   # file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
   # file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
   # file.write(          ",'UTGWORO','UTGWSPEC','BUTGWSPEC'")   # gravity wave U tendencies
   # file.write('\n')

   # ,'MSKtem','VTH2d','UV2d','UW2d','U2d','V2d','TH2d','W2d' # FV TE terms
   
   #------------------------------
   # Other namelist stuff
   #------------------------------   
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
   # file.write(" inithist = \'ENDOFRUN\' \n")
   file.close()

   # exit(f'Check file: {case_dir}/{case}/user_nl_eam')

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
