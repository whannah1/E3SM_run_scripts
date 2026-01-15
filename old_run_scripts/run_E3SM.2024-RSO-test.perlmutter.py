#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/docn/add-relaxed-slab-ocean

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True



queue = 'regular' # debug / regular

# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',11,3-1,'1:00:00'

# queue = 'regular'; stop_opt,stop_n,resub,walltime = 'ndays',365,0,'2:00:00'
queue = 'regular'; stop_opt,stop_n,resub,walltime = 'ndays',365*5,0,'8:00:00'

compset='F2010'
# compset='F2010-RSO'

# grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 8
grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 22
# grid = 'ne4pg2_oQU480'; num_nodes = 1

# case = '.'.join(['E3SM','2024-RSO-test-00',compset]) # RSO_relax_tau = 8 days
# case = '.'.join(['E3SM','2024-RSO-test-01',compset]) # Fixed MLD = 50
# case = '.'.join(['E3SM','2024-RSO-test-02',compset]) # RSO_relax_tau = 2 days
# case = '.'.join(['E3SM','2024-RSO-test-03',compset]) # test new namelist defaults - should be identical to 01
# case = '.'.join(['E3SM','2024-RSO-test-03',grid,compset])

case = '.'.join(['E3SM','2024-RSO-test-04',compset]) # long-term test with only monthly output + updated branch

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# arch = 'GNUCPU' # GNUCPU / GNUGPU

# if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 
# if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 
# atm_ntasks = max_mpi_per_node*num_nodes

# if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
# if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
max_mpi_per_node,atm_nthrds  = 128,1
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   # if arch=='GNUCPU' : cmd += f' --mach pm-cpu --compiler gnu    --pecount {atm_ntasks}x{atm_nthrds} '
   # if arch=='GNUGPU' : cmd += f' --mach pm-gpu --compiler gnugpu --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --mach pm-cpu --compiler intel --pecount {atm_ntasks}x{atm_nthrds} '
   cmd += f' --case {case} --handle-preexisting-dirs u '
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --compset {compset} --res {grid} '
   cmd += f' --project {acct} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config :
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
hst_fld  =  "'PS','TS','PSL'"
hst_fld += ",'PRECT','TMQ'"
hst_fld += ",'SST'"
# hst_fld += ",'PRECC','PRECL'"
hst_fld += ",'LHFLX','SHFLX'"             # surface fluxes
hst_fld += ",'FSNT','FLNT','FLUT'"        # Net TOM heating rates
hst_fld += ",'FLNS','FSNS'"               # Surface rad for total column heating
hst_fld += ",'FSNTC','FLNTC'"             # clear sky heating rates for CRE
hst_fld += ",'TGCLDLWP','TGCLDIWP'"       # liq & ice water path
# hst_fld += ",'TUQ','TVQ'"                 # vapor transport for AR tracking
# hst_fld += ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'" # lowest model leve
# hst_fld += ",'T900:I','Q900:I','U900:I','V900:I'" # 900mb data
# hst_fld += ",'T850:I','Q850:I','U850:I','V850:I'" # 850mb data
# hst_fld += ",'Z300:I','Z500:I'"
# hst_fld += ",'OMEGA850:I','OMEGA500:I'"
# hst_fld += ",'U200:I','V200:I'"
#---------------------------------------------------------------------------------------------------
if submit :
   #----------------------------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   # Specify history output frequency and variables
   # file.write(' nhtfrq    = 0,1 \n')
   # file.write(' mfilt     = 1,48 \n')
   file.write(' nhtfrq    = 0 \n')
   file.write(' mfilt     = 1 \n')
   file.write(" fincl1 = 'SST','Z3','CLDLIQ','CLDICE','HDEPTH','MAXQ0','UTGWSPEC','BUTGWSPEC'\n")
   # file.write(f" fincl2 = {hst_fld} \n")
   # file.write(f" fincl3 = {hst_fld} \n")
   file.close()
   #----------------------------------------------------------------------------
   # Set some run-time stuff
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   #----------------------------------------------------------------------------
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
