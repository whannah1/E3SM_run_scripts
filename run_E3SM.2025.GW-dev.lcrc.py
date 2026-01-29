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
src_dir  = f'{top_dir}/E3SM_SRC2/' # branch => whannah/eamxx/create-gwd-atm-proc

# clean        = True
# newcase      = True
# config       = True
build        = True
# submit       = True
# continue_run = True

# debug_mode = False

queue = 'debug'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',2,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91,1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,4-1,'4:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx GWD process testing

add_case(prefix='2025-GW-DEV-00', compset='F2010-SCREAMv1', grid='ne4pg2_oQU480', num_nodes=1, use_gw=True)

# add_case(prefix='2025-GW-DEV-00', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=4, debug=True)

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
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   #------------------------------------------------------------------------------------------------
   # exit()
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
      if 'use_gw' in opts:
         if opts['use_gw']:
            run_cmd(f'./atmchange mac_aero_mic::atm_procs_list+=gw')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if 'SCREAM' in opts['compset']:
         hist_file_list = []
         def add_hist_file(hist_file,txt):
            file=open(hist_file,'w'); file.write(txt); file.close()
            hist_file_list.append(hist_file)
         #----------------------------------------------------------------------
         # add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D_inst)
         # hist_file_list_str = ','.join(hist_file_list)
         # run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      else:
         # EAM namelist options
         nfile = 'user_nl_eam'
         file = open(nfile,'w') 
         file.write(eam_opts)
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

   print()
   print(clr.RED+'WARNING - all output is disabled for debugging!'+clr.END)
   print()
#---------------------------------------------------------------------------------------------------
eam_opts = f'''
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-24
 mfilt  = 1,1
 fincl1 = 'PRECT','Z3','CLOUD','CLDLIQ','CLDICE'
'''
#---------------------------------------------------------------------------------------------------
field_txt_2D = '\n'
# field_txt_2D += '      - precip_total_surf_mass_flux'
# field_txt_2D += '      - LiqWaterPath'
# field_txt_2D += '      - surf_sens_flux'
# field_txt_2D += '      - surf_evap'
# field_txt_2D += '      - surf_mom_flux'
field_txt_2D += '      - U_at_model_bot'
# field_txt_2D += '      - V_at_model_bot'
# field_txt_2D += '      - ash'


# hist_opts_2D_inst = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.2D.1hr
# Averaging Type: Instant
# Max Snapshots Per File: 24
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_2D}
# output_control:
#    Frequency: 1
#    frequency_units: nhours
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''

hist_opts_2D_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
Averaging Type: Instant
Max Snapshots Per File: 48
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: nsteps
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
