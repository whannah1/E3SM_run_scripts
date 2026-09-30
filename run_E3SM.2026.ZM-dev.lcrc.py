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
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

# debug_mode = False

# queue = 'debug'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:10:00'; queue='debug'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'; queue='debug'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,2-1,'1:10:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91,1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,4-1,'4:00:00'
#---------------------------------------------------------------------------------------------------

# src_dir=f'{top_dir}/E3SM_SRC2/' # branch => master @ Sep 1
# add_case(prefix='2026-ZM-DEV-00',compset='F2010xx-ZM',grid='ne4pg2_oQU480',num_nodes=1,mscp="old")

src_dir=f'{top_dir}/E3SM_SRC0/' # branch => whannah/eamxx/mcsp-momentum-update (rebased @ Sep 1)
# add_case(prefix='2026-ZM-DEV-00',compset='F2010xx-ZM',grid='ne4pg2_oQU480',num_nodes=1,mscp="new")
# add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM',grid='ne4pg2_oQU480',num_nodes=1,mscp="new") # test new momentum timescale

# test new momentum timescale
add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM-CICE',grid='ne30pg2_ne30pg2',num_nodes=4,mscp="new",mcsp_mom_coeff=-0.1)
# add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM-CICE',grid='ne30pg2_ne30pg2',num_nodes=4,mscp="new",mcsp_mom_coeff=-0.01)
add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM-CICE',grid='ne30pg2_ne30pg2',num_nodes=4,mscp="new",mcsp_mom_coeff=0.0)
# add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM-CICE',grid='ne30pg2_ne30pg2',num_nodes=4,mscp="new",mcsp_mom_coeff=0.01)
add_case(prefix='2026-ZM-DEV-01',compset='F2010xx-ZM-CICE',grid='ne30pg2_ne30pg2',num_nodes=4,mscp="new",mcsp_mom_coeff=0.1)


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
      # cmd += f' --mach bebop --compiler intel'
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean-all')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      if opts.get('mscp')=='new': run_cmd(f'./atmchange -b mcsp_use_full_shear=true ')
      if opts.get('mscp')=='old': run_cmd(f'./atmchange -b mcsp_use_full_shear=false ')
      if opts.get('mcsp_mom_coeff') is not None:
         run_cmd(f'./atmchange -b mcsp_mom_coeff={opts.get("mcsp_mom_coeff")}')
      #-------------------------------------------------------------------------
      # Enable process tendencies for output
      run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('output_1ma.yaml',      get_hist_opts_1ma(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # # disable history output
      # run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      # print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
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
# monthly mean output - native grid
def get_hist_opts_1ma(opts):
   return f'''
filename_prefix: output.1ma
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         # precipitation
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         # water paths
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         # radiation
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
         - SW_flux_up_at_model_bot
         - SW_flux_dn_at_model_bot
         - LW_flux_up_at_model_bot
         - LW_flux_dn_at_model_bot
         - LW_clrsky_flux_up_at_model_top
         - SW_clrsky_flux_up_at_model_top
         - SW_clrsky_flux_dn_at_model_top
         - ShortwaveCloudForcing
         - LongwaveCloudForcing
         # 3D variables
         - T_mid
         - z_mid
         - U
         - V
         - omega
         - pseudo_density
         - RelativeHumidity
         - qv
         - qc
         - qr
         - qi
         - qm
         - nc
         - ni
         - nr
         # misc 2D fields
         - T_2m
         # - surf_radiative_T
         - wind_speed_10m
         # - U_at_850hPa
         # - U_at_200hPa
         - surf_sens_flux
         - surf_evap
         - surf_mom_flux
         - cldfrac_liq
         - cldfrac_ice_for_analysis
         - cldfrac_tot_for_analysis
         # # process stendencies
         # - p3_T_mid_tend
         # - p3_qv_tend
         - shoc_T_mid_tend
         - shoc_qv_tend
         - shoc_horiz_winds_tend
         # - homme_T_mid_tend
         # - homme_qv_tend
         # - rrtmgp_T_mid_tend
         - zm_T_mid_tend
         - zm_qv_tend
         - zm_horiz_winds_tend
         # - zm_detr_qc
         # - zm_detr_qi
         # ZM diagnostic fields
         - zm_prec
         - zm_activity
         - zm_cape
         # - zm_dcape
         - zm_depth
         - mcsp_ds_out
         - mcsp_dq_out
         - mcsp_du_out
         - mcsp_freq
         - mcsp_shear
         # - evap_ds_out
         # - evap_dq_out
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
