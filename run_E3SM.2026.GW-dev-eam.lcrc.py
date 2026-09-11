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
top_dir  = os.getenv('HOME')+'/E3SM/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',6,0,'0:10:00'; queue='debug'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'; queue='debug'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91*2,0,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,4-1,'4:00:00'
#---------------------------------------------------------------------------------------------------
# EAM testing for stealth features

src_dir = f'{top_dir}/E3SM_SRC1' # branch => whannah/eam/2026-gwd-updates
# add_case(prefix='2026-GW-DEV-EAM-00', compset='F2010', grid='ne4pg2_oQU480', num_nodes=1)

# add_case(prefix='2026-GW-DEV-EAM-00', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=False)
# add_case(prefix='2026-GW-DEV-EAM-00', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=True)

# manually disable taucd scaling
# add_case(prefix='2026-GW-DEV-EAM-01', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=True) 

# # refactor how RR scaling works taucd scaling still diabled
# add_case(prefix='2026-GW-DEV-EAM-02', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=True)

# # same as 02 but enable taucd scaling
# add_case(prefix='2026-GW-DEV-EAM-03', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=True)

# same as 03 - update tapering limits - eff_res_grid_num_max = 20
add_case(prefix='2026-GW-DEV-EAM-04', compset='F2010', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=8, use_rr=True)

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'   in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'  in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_' in opts['grid']: grid_name = 'ne120pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['debug']:     continue
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
   # print(f' clean        : {clean}')
   # print(f' newcase      : {newcase}')
   # print(f' config       : {config}')
   # print(f' build        : {build}')
   # print(f' submit       : {submit}')
   # print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   #------------------------------------------------------------------------------------------------
   # exit()
   #------------------------------------------------------------------------------------------------
   comp = None
   if opts['compset'] in ['F2010']:
      comp = 'eam'
   else:
      comp = 'eamxx'
   #------------------------------------------------------------------------------------------------
   case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'

   if 'num_nodes' in opts:
      num_nodes = opts['num_nodes']
      max_mpi_per_node,atm_nthrds = 64,1 ; max_task_per_node = 64
      atm_ntasks = max_mpi_per_node*num_nodes
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
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
      # cmd += f' --mach chrysalis --compiler gnu'
      cmd += f' --mach chrysalis --compiler intel'
      # cmd += f' --mach bebop --compiler intel'
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
      if clean : run_cmd('./case.setup --clean-all')
      run_cmd('./case.setup --reset')
      #-------------------------------------------------------------------------
      if opts.get('use_gw',False):
         run_cmd(f'./atmchange physics::atm_procs_list+=gw')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      # run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
      # run_cmd('./case.build --clean ice  && ./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if comp=='eam':
         file=open('user_nl_eam','w')
         # file.write(f'ncdata = \'{init_file_eam}\'\n')
         file.write(f"avgflag_pertape = 'A','A'\n")
         file.write(f"nhtfrq = 0,-24\n")
         file.write(f"mfilt = 1,1\n")
         file.write(f"fincl1 = 'PS', 'PRECT','Z3','CLOUD','CLDLIQ','CLDICE'")
         file.write(f",'UTGWORO','BUTGWSPEC','UTGWSPEC'")
         file.write(f'\n')
         if opts.get('use_rr'):
            file.write(f"use_gw_front_rr_scaling = .true.\n")
         else:
            file.write(f"use_gw_front_rr_scaling = .false.\n")
         file.close()
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
