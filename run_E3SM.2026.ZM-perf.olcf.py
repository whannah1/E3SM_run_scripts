#!/usr/bin/env python
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
''' Notes
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => whannah/eamxx/zm-atm-proc

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# debug_mode = False

# queue = 'regular'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:05:00'; queue = 'debug'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'; queue = 'debug'
stop_opt,stop_n,resub,walltime = 'ndays',5,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'3:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'12:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx ZM performance scaling

# prefix = '2026-ZM-PERF-00'
prefix = '2026-ZM-PERF-01' # fix inconsistencies

compset = 'F2010-SCREAMv1'

add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 1)
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 2)
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 4)
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 8)
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=16)

compset = 'F2010xx-ZM-CICE'

# add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 1, zm='f90')
# add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 2, zm='f90')
# add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 4, zm='f90')
# add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 8, zm='f90')
# add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=16, zm='f90')

add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 1, zm='cxx')
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 2, zm='cxx')
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 4, zm='cxx')
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes= 8, zm='cxx')
add_case(prefix=prefix, compset=compset, grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=16, zm='cxx')


#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'   in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'  in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_' in opts['grid']: grid_name = 'ne120pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   # global debug_mode
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   # arch       = opts['arch']  if opts.get('arch')  else 'CPU'
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: case_list.append(f'NN_{val:03}')
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
   print(f' clean        : {clean}')
   print(f' newcase      : {newcase}')
   print(f' config       : {config}')
   print(f' build        : {build}')
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   # arch       = opts['arch']  if opts.get('arch')  else 'CPU'
   enable_zm  = False
   #----------------------------------------------------------------------------
   # return
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts:
      max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
      # if arch=='GPU': max_mpi_per_node,atm_nthrds =   4,1
      # if arch=='CPU': max_mpi_per_node,atm_nthrds = 128,1
      # if arch=='CPU' and 'ne4pg2' in opts['grid']: max_mpi_per_node,atm_nthrds = 96,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #----------------------------------------------------------------------------
   # if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   # if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {opts["compset"]}'
      cmd += f' --res {opts["grid"]} '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      # if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      # if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' --machine=frontier --compiler=craygnu-mphipcc '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if opts.get('zm') is not None:
         if opts.get('zm')=='f90': run_cmd(f'./atmchange -b zm::use_fortran_bridge=true')
         if opts.get('zm')=='cxx': run_cmd(f'./atmchange -b zm::use_fortran_bridge=false')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      # run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange REST_OPTION=never')
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
