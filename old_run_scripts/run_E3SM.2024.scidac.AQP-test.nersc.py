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
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2024

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

arch = 'GNUCPU' # GNUCPU / GNUGPU

stop_opt,stop_n,resub,walltime = 'ndays',365,9-1,'4:00:00'

compset='FAQP'

# ne,npg,grid = 30,2,f'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 8
ne,npg,grid = 30,2,f'ne30pg2_ne30pg2'; num_nodes = 16

case = '.'.join(['E3SM','2024-SCIDAC-AQP-test-00',compset])

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 
if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 
atm_ntasks = max_mpi_per_node*num_nodes

if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   if arch=='GNUCPU' : cmd += f' --mach pm-cpu --compiler gnu    --pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' --mach pm-gpu --compiler gnugpu --pecount {atm_ntasks}x{atm_nthrds} '
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
hst_fld += ",'PRECC','PRECL'"
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
# hst_fld += ",'T','Q','Z3'"                       # 3D thermodynamic budget components
# hst_fld += ",'U','V','OMEGA'"                    # 3D velocity components
# hst_fld += ",'QRL','QRS'"                        # 3D radiative heating profiles
# hst_fld += ",'CLDLIQ','CLDICE'"                  # 3D cloud fields
# hst_fld += ",'DTCOND','ZMDT','P3DT'"
# hst_fld += ",'TTEND_CLUBB','CLOUDFRAC_CLUBB'"
# hst_fld += ",'WP2_CLUBB','WP3_CLUBB'"
#---------------------------------------------------------------------------------------------------
if submit :
   #----------------------------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   # Specify history output frequency and variables
   file.write(' nhtfrq    = 0,-3,-3 \n')
   file.write(' mfilt     = 1,8,8 \n')
   file.write(" avgflag_pertape = 'A','A','I' \n")
   file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE'\n")
   file.write(f" fincl2 = {hst_fld} \n")
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