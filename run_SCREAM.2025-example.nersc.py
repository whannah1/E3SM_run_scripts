#!/usr/bin/env python
import os, datetime, subprocess as sp
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

acct = 'm4310'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => master @ 2025-7-1

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'1:30:00'

arch = 'GPU'

#---------------------------------------------------------------------------------------------------
# build list of cases to run


add_case(prefix='2025-TEST-00', compset='F2010-SCREAMv1', grid='ne256pg2_ne256pg2', num_nodes=128 )


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
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['grid']: 
         case_list.append(get_grid_name(opts))
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
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
   exit()
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']

   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'

   num_nodes = opts['num_nodes']
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']#+'_'+opts['grid']
   compset = opts['compset']
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
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
      # if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_10min_inst.yaml',hist_opts_2D_10min_inst)
      # add_hist_file(f'{case_root}/case_scripts/scream_output_3D_10min_inst.yaml',hist_opts_3D_10min_inst)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
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
#---------------------------------------------------------------------------------------------------

field_txt_2D = '\n'
field_txt_2D += '      - ps'
field_txt_2D += '      - precip_total_surf_mass_flux'
field_txt_2D += '      - VapWaterPath'
field_txt_2D += '      - LiqWaterPath'
field_txt_2D += '      - IceWaterPath'
field_txt_2D += '      - surf_sens_flux'
field_txt_2D += '      - surface_upward_latent_heat_flux'
field_txt_2D += '      - wind_speed_10m'
field_txt_2D += '      - SW_flux_up_at_model_top'
field_txt_2D += '      - SW_flux_dn_at_model_top'
field_txt_2D += '      - LW_flux_up_at_model_top'
# field_txt_2D += '      - surf_evap'
# field_txt_2D += '      - surf_mom_flux'
# field_txt_2D += '      - horiz_winds_at_model_bot'
# field_txt_2D += '      - SW_flux_dn_at_model_bot'
# field_txt_2D += '      - SW_flux_up_at_model_bot'
# field_txt_2D += '      - LW_flux_dn_at_model_bot'
# field_txt_2D += '      - LW_flux_up_at_model_bot'
# field_txt_2D += '      - SW_flux_up_at_model_top'
# field_txt_2D += '      - SW_flux_dn_at_model_top'
# field_txt_2D += '      - LW_flux_up_at_model_top'

field_txt_3D = '\n'
field_txt_3D += '      - ps'
field_txt_3D += '      - omega'
field_txt_3D += '      - horiz_winds'
field_txt_3D += '      - qv'
field_txt_3D += '      - T_mid'
field_txt_3D += '      - z_mid'
# field_txt_3D += '      - qc'
# field_txt_3D += '      - qr'
# field_txt_3D += '      - qi'
# field_txt_3D += '      - qm'
# field_txt_3D += '      - nc'
# field_txt_3D += '      - nr'
# field_txt_3D += '      - ni'
# field_txt_3D += '      - bm'
# field_txt_3D += '      - RelativeHumidity'
# field_txt_3D += '      - rad_heating_pdel'


hist_opts_2D_10min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.10min
averaging_type: instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 10
   frequency_units: nmins
restart:
   force_new_file: true
'''



hist_opts_3D_10min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.10min
averaging_type: instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:{field_txt_3D}
output_control:
   frequency: 10
   frequency_units: nmins
restart:
   force_new_file: true
'''


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
