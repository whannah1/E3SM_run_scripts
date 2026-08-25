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
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC1' # branch => whannah/eamxx/support-new-L128

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00'

#---------------------------------------------------------------------------------------------------

kwargs = {'prefix':'2026-L128-TEST-00','compset':'F2010-SCREAMv1'}

# add_case(**kwargs, arch='GPU', num_nodes=1,   grid='ne4pg2_ne4pg2')
# add_case(**kwargs, arch='GPU', num_nodes=2,   grid='ne30pg2_ne30pg2')
add_case(**kwargs, arch='GPU', num_nodes=2,   grid='ne32pg2_ne32pg2')
add_case(**kwargs, arch='GPU', num_nodes=4,   grid='ne64pg2_ne64pg2')
add_case(**kwargs, arch='GPU', num_nodes=16,  grid='ne120pg2_ne120pg2')
add_case(**kwargs, arch='GPU', num_nodes=16,  grid='ne128pg2_ne128pg2')
add_case(**kwargs, arch='GPU', num_nodes=64,  grid='ne256pg2_ne256pg2')
add_case(**kwargs, arch='GPU', num_nodes=256, grid='ne512pg2_ne512pg2')
add_case(**kwargs, arch='GPU', num_nodes=512, grid='ne1024pg2_ne1024pg2')

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch','grid']: case_list.append(val)
      elif key in ['debug']:        continue
      elif key in ['num_nodes']:    case_list.append(f'NN_{val}')
      elif key in ['num_tasks']:    case_list.append(f'NT_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if opts.get('debug',False): case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   # return
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
   debug_mode = opts.get('debug', False)
   arch       = opts.get('arch','CPU')
   #------------------------------------------------------------------------------------------------
   machine,compiler = 'frontier','craygnu-mphipcc'
   if arch=='GPU':machine,compiler='pm-gpu','gnugpu';case_root=f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'
   if arch=='CPU':machine,compiler='pm-cpu','gnu'   ;case_root=f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'num_nodes' in opts:
      if arch=='GPU': max_mpi_per_node,atm_nthrds =   4,1
      if arch=='CPU': max_mpi_per_node,atm_nthrds = 128,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
      cmd += f' --pecount {atm_ntasks}x1 --machine={machine} --compiler={compiler} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      # use updated SPA data file
      DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
      run_cmd(f'./atmchange -b spa_data_file="{DIN_LOC_ROOT}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      #-------------------------------------------------------------------------
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
