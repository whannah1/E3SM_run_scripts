#!/usr/bin/env python
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
''' Ben's decadal run script for reference
/ccs/home/brhillman/codes/scream/cases/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run.decadal-amip.sh
'''
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => bartgol/eamxx/fix-7682

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True


# queue = 'regular'

stop_opt,stop_n,resub,walltime = 'nhours',2,2,'0:30:00'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

add_case(prefix='2026-BUG-TEST-00', compset='F2010-SCREAMv1', grid='ne4pg2_ne4pg2', num_nodes=1 )

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'    in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'   in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_'  in opts['grid']: grid_name = 'ne120pg2'
   if 'ne256pg2_'  in opts['grid']: grid_name = 'ne256pg2'
   if 'ne1024pg2_' in opts['grid']: grid_name = 'ne1024pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','grid','init']:
         case_list.append(val)
      # elif key in ['grid']: 
      #    case_list.append(get_grid_name(opts))
      elif key in ['num_nodes','compset']:
         continue
         # case_list.append(f'NN_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #------------------------------------------------------------------------------------------------
   # exit()
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']

   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']
   compset = opts['compset']
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case}'
      cmd += f' --output-root {case_root}'
      cmd += f' --script-root {case_root}/case_scripts'
      cmd += f' --handle-preexisting-dirs u'
      cmd += f' --compset {compset} --res {grid}'
      cmd += f' --project {acct}'
      cmd += f' --machine=frontier --compiler=craygnu-mphipcc'
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds}'
      run_cmd(cmd)
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
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      # add_hist_file(f'{case_root}/case_scripts/scream_output_2D_10min_inst.yaml',hist_opts_2D_10min_inst)
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_3hr_inst.yaml',hist_opts_2D_3hr_avg)
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_3hr_avg.yaml', hist_opts_2D_3hr_inst)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
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
#---------------------------------------------------------------------------------------------------

var_list_2D = '''
         - ps
         - precip_total_surf_mass_flux
         - VapWaterPath
         - surf_sens_flux
         - U_at_850hPa
         - LW_flux_up_at_model_top
'''

hist_opts_2D_3hr_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
averaging_type: average
max_snapshots_per_file: 8
fields:
   physics_pg2:
      field_names:{var_list_2D}
output_control:
   frequency: 3
   frequency_units: nhours
restart:
   force_new_file: false
'''

hist_opts_2D_3hr_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
averaging_type: instant
max_snapshots_per_file: 8
fields:
   physics_pg2:
      field_names:{var_list_2D}
output_control:
   frequency: 3
   frequency_units: nhours
restart:
   force_new_file: false
'''





#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
