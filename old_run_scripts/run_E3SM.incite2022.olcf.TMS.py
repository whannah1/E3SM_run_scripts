#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5/' # branch => master+reduced-gpt @ Sept 21 2022

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'batch' # batch / debug

### run duration
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'4:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,5-1,'4:00'

### common settings
ne,npg    = 30,2
grid      = f'ne{ne}pg{npg}_oECv3'
compset   = 'F2010-MMF1'
arch      = 'GNUGPU'
num_nodes = 128


### specify case name based on configuration - 01 = redo with VT+ESMT
case_list = ['E3SM','INCITE2022-TMS-02',f'ne{ne}pg{npg}',compset,'TMS-ON']
# case_list = ['E3SM','INCITE2022-TMS-02',f'ne{ne}pg{npg}',compset,'TMS-OFF']

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files
land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
# land_data_file = 'surfdata_0.5x0.5_simyr2000_c200624.nc'
land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: 
      run_cmd('./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cppdefs \' -DYAKL_DEBUG \'  \" ')
      run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # # Specify history output frequency and variables
   # file.write(' nhtfrq     = 0,-1,-24 \n') 
   # file.write(' mfilt      = 1,24,1 \n') # 1-day files
   # file.write(" fincl1     = 'Z3'") # this is for easier use of height axis on profile plots   
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
   # file.write(             ",'CLDTOT_ISCCP','FISCCP1_COSP','CLDPTOP_ISCCP','MEANCLDALB_ISCCP'")
   # file.write(             ",'MEANPTOP_ISCCP','MEANTAU_ISCCP','MEANTB_ISCCP','MEANTBCLR_ISCCP'")
   # file.write(             ",'FSNS','FSNT'")               # probably default but add to be safe
   # file.write(             ",'FSNTOA','FSUTOA'")           # probably default but add to be safe
   # file.write(             ",'FSNTOAC','FSUTOAC'")         # probably default but add to be safe
   # file.write(             ",'FSNTC','FSNSC'")             # probably default but add to be safe
   # file.write(             ",'FSDSC','FSDS'")              # probably default but add to be safe
   # file.write('\n')
   # file.write(" fincl2    = 'PS','PSL','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'FLUT','FSNTOA'")             # more rad fields
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'QREFHT','TREFHT'")           # reference temperature and humidity
   # file.write(             ",'TUQ','TVQ'")                         # vapor transport
   # file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   # file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(             ",'Z300:I','Z500:I'")                   # height surfaces
   # file.write(             ",'OMEGA850:I','OMEGA500:I'")           # omega
   # file.write(             ",'U200:I','V200:I'")                   # 200mb winds
   # file.write('\n')
   #------------------------------
   # Other namelist stuff
   if 'TMS-ON'  in case: file.write(f' do_tms = .true. \n')
   if 'TMS-OFF' in case: file.write(f' do_tms = .false. \n')
   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'land_init_file' in locals() or 'land_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
