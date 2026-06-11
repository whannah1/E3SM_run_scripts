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
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'12:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx ZM process testing

# add_case(prefix='2026-ZM-DEV-01', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=4, zm='f90')
# add_case(prefix='2026-ZM-DEV-01', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=4, zm='cxx')

# add_case(prefix='2026-ZM-DEV-01', compset='F2010xx-ZM', grid='ne256pg2_r025_RRSwISC6to18E3r5', num_nodes=64, zm='f90')
add_case(prefix='2026-ZM-DEV-01', compset='F2010xx-ZM', grid='ne256pg2_r025_RRSwISC6to18E3r5', num_nodes=64, zm='cxx')

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'   in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'  in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_' in opts['grid']: grid_name = 'ne120pg2'
   if 'ne256pg2_' in opts['grid']: grid_name = 'ne256pg2'
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
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   # arch       = opts['arch']  if opts.get('arch')  else 'CPU'
   # enable_zm  = True
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
      #-------------------------------------------------------------------------
      # if 'use_gw' in opts:
      #    if opts['use_gw']:
      #       run_cmd(f'./atmchange physics::atm_procs_list=gw,mac_aero_mic,rrtmgp')
      #       # run_cmd(f'./atmchange mac_aero_mic::atm_procs_list+=gw')
      #       # run_cmd(f'./atmchange -b use_gw_convect=True')
      #       # run_cmd(f'./atmchange -b use_gw_frontal=True')
      #       run_cmd(f'./atmchange -b use_gw_orographic=True')
      #-------------------------------------------------------------------------
      # # Allow for the computation of tendencies for output purposes
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
      # if enable_zm:
      #    run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      # run_cmd('./xmlchange CICE_CPPDEFS="-DCCSMCOUPLED -Dcoupled -Dncdf -DNCAT=1 -DNXGLOB=1791 -DNYGLOB=1 -DNTR_AERO=0 -DMODAL_AER"')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
      # run_cmd('./case.build --clean ice  && ./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if opts.get('zm') is not None:
         if opts.get('zm')=='f90': run_cmd(f'./atmchange -b zm::use_fortran_bridge=true')
         if opts.get('zm')=='cxx': run_cmd(f'./atmchange -b zm::use_fortran_bridge=false')
         if opts.get('zm_detr')==0:run_cmd(f'./atmchange -b zm::apply_detr_tend=false')
         if opts.get('zm_detr')==1:run_cmd(f'./atmchange -b zm::apply_detr_tend=true')
         # run_cmd(f'./atmchange physics::atm_procs_list=gw,mac_aero_mic,rrtmgp')
         # # run_cmd(f'./atmchange mac_aero_mic::atm_procs_list+=gw')
         # # run_cmd(f'./atmchange -b use_gw_convect=True')
         # # run_cmd(f'./atmchange -b use_gw_frontal=True')
         # run_cmd(f'./atmchange -b use_gw_orographic=True')

         if opts.get('mcsp_mod')==1:
            run_cmd(f'./atmchange -b zm::mcsp_t_coeff=0.5')
            run_cmd(f'./atmchange -b zm::mcsp_q_coeff=0.5')
            run_cmd(f'./atmchange -b zm::mcsp_u_coeff=0.0')
            run_cmd(f'./atmchange -b zm::mcsp_v_coeff=0.0')
         
         
      #-------------------------------------------------------------------------
      # if 'SCREAM' in opts['compset']:
      if True:
         hist_file_list = []
         def add_hist_file(hist_file,txt):
            file=open(hist_file,'w'); file.write(txt); file.close()
            hist_file_list.append(hist_file)
         #----------------------------------------------------------------------
         # add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D_inst)
         # add_hist_file('scream_output_3D_1step_inst.yaml',hist_opts_3D_inst)
         add_hist_file('scream_output_daily_mean.yaml',hist_opts_daily_mean)
         add_hist_file('scream_output_monthly_mean.yaml',hist_opts_monthly_mean)
         
         hist_file_list_str = ','.join(hist_file_list)
         run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
         #----------------------------------------------------------------------
         # print(f'\n{clr.RED}WARNING - all output is disabled for debugging!{clr.END}')
         #----------------------------------------------------------------------
      # else:
      #    # EAM namelist options
      #    nfile = 'user_nl_eam'
      #    file = open(nfile,'w') 
      #    file.write(eam_opts)
      #    file.close()
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
eam_opts = f'''
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-24
 mfilt  = 1,1
 fincl1 = 'PRECT','Z3','CLOUD','CLDLIQ','CLDICE'
'''
#---------------------------------------------------------------------------------------------------
field_txt_2D = '\n'
field_txt_2D += '      - ps\n'
field_txt_2D += '      - SeaLevelPressure\n'
field_txt_2D += '      - precip_total_surf_mass_flux\n'
field_txt_2D += '      - VapWaterPath\n'
field_txt_2D += '      - LiqWaterPath\n'
field_txt_2D += '      - IceWaterPath\n'
field_txt_2D += '      - RainWaterPath\n'
field_txt_2D += '      - T_2m\n'
field_txt_2D += '      - wind_speed_10m\n'
field_txt_2D += '      - SW_flux_up_at_model_top\n'
field_txt_2D += '      - SW_flux_dn_at_model_top\n'
field_txt_2D += '      - LW_flux_up_at_model_top\n'
# field_txt_2D += '      - U_at_model_bot\n'
# field_txt_2D += '      - V_at_model_bot\n'
field_txt_2D += '      - zm_prec\n'
field_txt_2D += '      - zm_cape\n'
# field_txt_2D += '      - zm_dcape\n'
field_txt_2D += '      - zm_activity\n'
field_txt_2D += '      - U_at_850hPa\n'
# field_txt_2D += '      - U_at_200hPa\n'
# field_txt_2D += '      - omega_at_500hPa\n'

field_txt_3D = field_txt_2D
field_txt_3D+='      - T_mid\n'
field_txt_3D+='      - z_mid\n'
field_txt_3D+='      - omega\n'
field_txt_3D+='      - qv\n'
field_txt_3D+='      - qc\n'
field_txt_3D+='      - qr\n'
field_txt_3D+='      - qi\n'
field_txt_3D+='      - RelativeHumidity\n'

# field_txt_3D+='      - p3_T_mid_tend\n'
# field_txt_3D+='      - shoc_T_mid_tend\n'
# field_txt_3D+='      - rrtmgp_T_mid_tend\n'
# field_txt_3D+='      - homme_T_mid_tend\n'
# field_txt_3D+='      - p3_qv_tend\n'
# field_txt_3D+='      - shoc_qv_tend\n'
# field_txt_3D+='      - homme_qv_tend\n' 
# field_txt_3D+='      - zm_T_mid_tend\n'
# field_txt_3D+='      - zm_qv_tend\n'

field_txt_ma = field_txt_3D
field_txt_ma+='      - surf_sens_flux\n'
field_txt_ma+='      - surf_evap\n'
field_txt_ma+='      - surf_mom_flux\n'
field_txt_ma+='      - cldfrac_tot_for_analysis\n'
field_txt_ma+='      - cldfrac_liq\n'
field_txt_ma+='      - cldfrac_ice_for_analysis\n'
field_txt_ma+='      - U\n'
field_txt_ma+='      - V\n'
field_txt_ma+='      - zm_detr_qc\n'
field_txt_ma+='      - zm_detr_qi\n'

# hist_opts_3D_inst = f'''
# %YAML 1.1
# ---
# filename_prefix: output.3D
# averaging_type: instant
# max_snapshots_per_file: 48
# fields:
#    physics_pg2:
#       field_names:{field_txt_3D}
# output_control:
#    frequency: 1
#    frequency_units: nsteps
# '''

hist_opts_daily_mean = f'''
%YAML 1.1
---
filename_prefix: output.daily
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 24
   frequency_units: nhours
'''

hist_opts_2D_inst = f'''
%YAML 1.1
---
filename_prefix: output.2D
averaging_type: instant
max_snapshots_per_file: 48
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 1
   frequency_units: nsteps
'''

# horiz_remap_file = f'{horiz_remap_root}/map_dpxx_x{domain_len}m_y{domain_len}m_nex{ne}_ney{ne}_to_1x1.nc'
# hist_opts_1D_1hr_mean = f'''
# %YAML 1.1
# ---
# filename_prefix: output.1D.1hr
# averaging_type: average
# max_snapshots_per_file: 24
# horiz_remap_file: {horiz_remap_file}
# fields:
#    physics_pg2:
#       field_names:{get_field_txt_1D(opts)}
# output_control:
#    frequency: 1
#    frequency_units: nhours
# restart:
#    force_new_file: true
# '''


# monthly mean output
hist_opts_monthly_mean = f'''
%YAML 1.1
---
filename_prefix: output.monthly
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_ma}
output_control:
   frequency: 1
   frequency_units: nmonths
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
