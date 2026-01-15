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
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

arch = 'GNUCPU' # GNUCPU / GNUGPU

queue = 'debug'

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',11,3-1,'1:00:00'

compset='F2010'

ne,npg,grid = 30,2,f'ne30pg2_r05_IcoswISC30E3r5'; num_nodes = 8

# case = '.'.join(['E3SM','2024-SCIDAC-heating-test-00',compset]) # output data to analyze heating for GWD
# case = '.'.join(['E3SM','2024-SCIDAC-heating-test-01',compset]) # modified GWD - old method (control)
# case = '.'.join(['E3SM','2024-SCIDAC-heating-test-02',compset]) # modified GWD - new method
# case = '.'.join(['E3SM','2024-SCIDAC-heating-test-03',compset]) # modified GWD - Yuanpu's method
# case = '.'.join(['E3SM','2024-SCIDAC-heating-test-04',compset]) # modified GWD - new method revised to match Yuanpu
case = '.'.join(['E3SM','2024-SCIDAC-heating-test-05',compset]) # modified GWD - test build for PR branch

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
hst_fld += ",'TUQ','TVQ'"                 # vapor transport for AR tracking
hst_fld += ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'" # lowest model leve
hst_fld += ",'T900:I','Q900:I','U900:I','V900:I'" # 900mb data
hst_fld += ",'T850:I','Q850:I','U850:I','V850:I'" # 850mb data
hst_fld += ",'Z300:I','Z500:I'"
hst_fld += ",'OMEGA850:I','OMEGA500:I'"
hst_fld += ",'U200:I','V200:I'"
hst_fld += ",'T','Q','Z3'"                       # 3D thermodynamic budget components
hst_fld += ",'U','V','OMEGA'"                    # 3D velocity components
hst_fld += ",'QRL','QRS'"                        # 3D radiative heating profiles
hst_fld += ",'CLDLIQ','CLDICE'"                  # 3D cloud fields
hst_fld += ",'DTCOND','ZMDT'"
# hst_fld += ",'P3DT'" 
'''
to add P3DT - need to edit components/eam/src/physics/p3/eam/micro_p3_interface.F90
for micro_p3_init():
   call addfld ('P3DT',(/ 'lev' /), 'A','K/s','T tendency - P3 Microphysics')
for micro_p3_tend():
   ftem = 0
   ftem(:ncol,:pver) = ptend%s(:ncol,:pver)/cpair
   call outfld('P3DT', ftem, pcols, lchnk )
'''
hst_fld += ",'TTEND_CLUBB','CLOUDFRAC_CLUBB'"
hst_fld += ",'WP2_CLUBB','WP3_CLUBB'"
hst_fld += ",'HDEPTH','MAXQ0'"
hst_fld += ",'UTGWSPEC','BUTGWSPEC'"
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
   file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','HDEPTH','MAXQ0','UTGWSPEC','BUTGWSPEC'\n")
   file.write(f" fincl2 = {hst_fld} \n")
   file.write(f" fincl3 = {hst_fld} \n")
   if '2024-SCIDAC-heating-test-01' in case:
      file.write(f" use_gw_convect_old = .true. \n")
   else:
      file.write(f" use_gw_convect_old = .false. \n")
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
