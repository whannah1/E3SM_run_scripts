#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/scidac-2025-multifidelity

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'regular' # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:10:00'
stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365-32,0,'3:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,10-1,'4:00:00'

compset='F20TR'

# add_case(prefix='2025-MF-test-00',grid='ne18pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=8) # debug
# add_case(prefix='2025-MF-test-00',grid='ne18pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=8,debug=True) # debug
# add_case(prefix='2025-MF-test-00',grid='ne30pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=8)

add_case(prefix='2025-MF-test-00',grid='ne18pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=12)
# add_case(prefix='2025-MF-test-00',grid='ne22pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=18)
# add_case(prefix='2025-MF-test-00',grid='ne26pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=24)
add_case(prefix='2025-MF-test-00',grid='ne30pg2_r05_IcoswISC30E3r5',compset=compset,num_nodes=32)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   global debug_mode

   compset   = opts['compset']
   grid      = opts['grid']
   num_nodes = opts['num_nodes']

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['grid']:
         case_list.append(val.split('_')[0])
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
         # continue
      elif key in ['debug']:
         case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # exit()
   # return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 128,1 
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if 'debug' in opts:
         if opts['debug']: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #----------------------------------------------------------------------------
      # Namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w')
      file.write(' nhtfrq    = 0,-24 \n')
      file.write(' mfilt     = 1,1 \n')
      # file.write(" avgflag_pertape = 'A','A','I' \n")
      file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','BUTGWSPEC','UTGWORO','UTGWSPEC'")
      file.write(         ",'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'")
      file.write("\n")
      file.write(" fincl2 = 'PS','PRECT','FLUT','U850','U200'")
      file.write('\n')
      file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
      file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
      file.write(f' phys_grid_ctem_nfreq = -1 \n') # Frequency of TEM diagnostic calculations (neg => hours)
      file.close()
      #----------------------------------------------------------------------------
      # file=open('user_nl_elm','w')
      # file.write(f"finidat = '' \n")
      # file.close()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1985-01-01')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
