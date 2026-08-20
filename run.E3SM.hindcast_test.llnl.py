#!/usr/bin/env python
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,submit,continue_run = False,False,False,False,False
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
acct = 'strong'
top_dir  = os.getenv('HOME')+'/E3SM/'
src_dir  = f'{top_dir}/E3SM_SRC0/' # branch => master @ Aug 19 2026

# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

queue = 'pbatch' # pbatch / pdebug

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'; queue = 'pdebug'

#---------------------------------------------------------------------------------------------------

# add_case(prefix='2026-HC-TEST-00', grid='ne30pg2_r05_IcoswISC30E3r5', compset='F2010', num_nodes=4 )
add_case(prefix='2026-HC-TEST-00', grid='ne30pg2_r05_IcoswISC30E3r5', compset='F20TR', num_nodes=4 )

init_file = '/p/vast1/strong/hannah6/HICCUP/HICCUP.atm_era5.2022-08-26.00.ne30np4.L80.nc'

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items():
      if key in ['prefix','compset']: case_list.append(val)
      elif key in ['grid']:      case_list.append(val)
      # elif key in ['debug']:     continue
      elif key in ['num_nodes']: case_list.append(f'NN_{val}')
      elif key in ['num_tasks']: case_list.append(f'NT_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if debug_mode: case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   print(f' newcase      : {newcase}')
   print(f' config       : {config}')
   print(f' build        : {build}')
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   #----------------------------------------------------------------------------
   # return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 112,1
   atm_ntasks = max_mpi_per_node*opts['num_nodes']
   #----------------------------------------------------------------------------
   case_root = f'/p/vast1/strong/hannah6/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u'
      cmd += f' --output-root {case_root}'
      cmd += f' --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]}'
      cmd += f' --machine=dane --pecount {atm_ntasks}x{atm_nthrds} --project {acct}'
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # run_cmd(f'./xmlchange COMP_INTERFACE=mct') # override new moab default
      #-------------------------------------------------------------------------
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      # run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      nfile = 'user_nl_eam'
      file = open(nfile,'w')
      file.write(f' ncdata=\'{init_file}\'\n')
      file.close()
      #-------------------------------------------------------------------------
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------