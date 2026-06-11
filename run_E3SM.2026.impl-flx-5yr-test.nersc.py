#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
'''
scontrol update qos=debug jobid=
'''
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
# https://docs.alcf.anl.gov/aurora/running-jobs-aurora/#queues
#---------------------------------------------------------------------------------------------------
'''
components/elm/src/biogeophys/BareGroundFluxesMod.F90
components/elm/src/biogeophys/CanopyFluxesMod.F90
components/elm/src/biogeophys/LakeFluxesMod.F90
components/elm/src/biogeophys/UrbanFluxesMod.F90
driver-mct/main/seq_flux_mct.F90
share/util/shr_flux_mod.F90
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
home = os.getenv('HOME')
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => quantheory/implicit-momentum-flux-eamxx-rebase-new-diag

acct = 'e3sm' # e3sm / m4842 (sohip) / m4310 (scidac)

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
continue_run = True

queue = 'regular'

stop_opt,stop_n,resub,walltime = 'ndays',32,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,6-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',182,0,'7:00:00' # July 1
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'14:00:00' # 1-yr
# stop_opt,stop_n,resub,walltime = 'ndays',73,5*5-1,'4:00:00' # 5-yr
# stop_opt,stop_n,resub,walltime = 'ndays',365,5-1,'12:00:00' # 5-yr

#---------------------------------------------------------------------------------------------------
# build list of cases to run

# test to investigate how to disable implici fluxes

# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne4', num_nodes=1, imp_flux=False )

# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, imp_flux=False )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, imp_flux=True )

# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, iflx=False, gust=False, debug=True )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, iflx=True,  gust=False, debug=True )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, iflx=False, gust=True,  debug=True )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne30', num_nodes=8, iflx=True,  gust=True,  debug=True )


# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=False, gust=False )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=True,  gust=True )
# add_case(prefix='2026-impflx-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=True,  gust=False )

### new cases with special source code changes to understand instability issues

# this run makes 4 additional changes:
# - use itmax in UrbanFluxesMod / LakeFluxesMod / BareGroundFluxesMod
# - flux_max_iteration = 30 in driver-mct/main/seq_flux_mct.F90
add_case(prefix='2026-impflx-debug-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=False,  gust=False )
# add_case(prefix='2026-impflx-debug-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=False,  gust=False, vtheta_thresh=0, theta_advect_form=2 )
# add_case(prefix='2026-impflx-debug-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=False,  gust=False, vtheta_thresh=100, theta_advect_form=2 )

# new test with larger value of tau_diff_fac to make crash happen faster
# add_case(prefix='2026-impflx-debug-01', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=128, iflx=True,  gust=True )

#---------------------------------------------------------------------------------------------------
def get_grid(opts):
   grid_short,grid = opts['grid'],None
   if grid_short=='ne256': grid = 'ne256pg2_ne256pg2'
   if grid_short=='ne30': grid = 'ne30pg2_ne30pg2'
   if grid_short=='ne4' : grid = 'ne4pg2_ne4pg2'
   if grid is None: raise ValueError('grid cannot be None!')
   return grid
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   #----------------------------------------------------------------------------
   debug_mode = opts.get('debug', False)
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:                  case_list.append(get_grid(opts))
      elif key in ['debug']:                 continue
      elif key in ['num_nodes']:             case_list.append(f'NN_{val}')
      elif key in ['num_tasks']:             case_list.append(f'NT_{val}')
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
   #----------------------------------------------------------------------------
   
   # src_dir = None
   # if opts.get('imp_flux') is not None:
   #    src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => quantheory/implicit-momentum-flux-eamxx-rebase-new-diag
   # else:
   #    src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/eamxx/composable-diag-update-rebase
   
   if src_dir is None:  raise ValueError('src_dir cannot be None!')
   #----------------------------------------------------------------------------
   debug_mode = opts.get('debug', False)
   arch       = opts.get('arch','CPU')
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts: raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts: raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   case = get_case_name(opts)
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # return
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts:
      if arch=='GPU': max_mpi_per_node,atm_nthrds =   4,1
      if arch=='CPU': max_mpi_per_node,atm_nthrds = 128,1
      if arch=='CPU' and opts['grid']=='ne4': max_mpi_per_node,atm_nthrds = 96,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #----------------------------------------------------------------------------
   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {opts["compset"]}'
      cmd += f' --res {get_grid(opts)} '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
      # Copy this run script into the case directory
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'cp {os.path.realpath(__file__)} {case_root}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      if opts.get('iflx'): run_cmd('./xmlchange ATM_FLUX_INTEGRATION_METHOD=implicit_stress')
      if opts.get('gust'): run_cmd('./xmlchange ATM_SUPPLIES_GUSTINESS=TRUE')
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
      if opts.get('theta_advect_form') is not None:
         taf = opts['theta_advect_form']
         run_cmd(f'./atmchange -b ctl_nl::theta_advect_form={taf}')
         if taf==1: run_cmd(f'./atmchange -b ctl_nl::pgrad_correction=1')
         if taf==2: run_cmd(f'./atmchange -b ctl_nl::pgrad_correction=0')
      #-------------------------------------------------------------------------
      if opts.get('vtheta_thresh') is not None:
         tmp_vtheta_thresh = opts['vtheta_thresh']
         run_cmd(f'./atmchange vtheta_thresh={tmp_vtheta_thresh}')
      #-------------------------------------------------------------------------
      run_cmd('./atmchange homme::compute_tendencies=T_mid,qv,horiz_winds')
      run_cmd('./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd('./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd('./atmchange physics::rrtmgp::compute_tendencies=T_mid')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('scream_output_1dy_avg.yaml', hist_opts_1dy_avg)
      add_hist_file('scream_output_1mo_avg.yaml', hist_opts_1mo_avg)

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

      # monthly restarts for debugging only!
      # print(clr.RED+'WARNING - monthly restarts enabled for debugging!'+clr.END)
      # run_cmd('./xmlchange REST_OPTION=nmonths REST_N=1')
      # run_cmd(f'./xmlchange REST_OPTION={stop_opt} REST_N={stop_n}')
   


      # Submit the run
      run_cmd('./case.submit')

   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 

   # print()
   # print(clr.RED+'WARNING - history output is disabled!'+clr.END)
   # print(clr.RED+'WARNING - restart output is disabled!'+clr.END)
   # print()
#---------------------------------------------------------------------------------------------------

hist_opts_1dy_avg = f'''
%YAML 1.1
---
filename_prefix: output.2D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:
         - ps
         - precip_total_surf_mass_flux
         - LW_flux_up_at_model_top
         - VapWaterPath
         - LiqWaterPath
         - RainWaterPath
         - IceWaterPath
         - wind_speed_10m
         - U_at_model_bot
         - V_at_model_bot
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - surf_mom_flux
output_control:
   frequency: 1
   frequency_units: ndays
restart:
   force_new_file: false
'''

# monthly mean output
hist_opts_1mo_avg = f'''
%YAML 1.1
---
filename_prefix: output.1ma
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      aliases:
         - T_2m_bt1:=T_2m_minus_T_2m_prev
         - surf_sens_flux_bt1:=surf_sens_flux_minus_surf_sens_flux_prev
         - wind_speed_10m_bt1:=wind_speed_10m_minus_wind_speed_10m_prev
      field_names:
         # 2D fields
         - ps
         - SeaLevelPressure
         - T_2m
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - RainWaterPath
         - IceWaterPath
         - wind_speed_10m
         - U_at_model_bot
         - V_at_model_bot
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - surf_mom_flux
         - ZonalVapFlux
         - MeridionalVapFlux
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
         - SW_clrsky_flux_up_at_model_top
         - SW_clrsky_flux_dn_at_model_top
         - LW_clrsky_flux_up_at_model_top
         - SW_flux_up_at_model_bot
         - SW_flux_dn_at_model_bot
         - LW_flux_up_at_model_bot
         - LW_flux_dn_at_model_bot
         - SW_clrsky_flux_up_at_model_bot
         - SW_clrsky_flux_dn_at_model_bot
         - LW_clrsky_flux_dn_at_model_bot
         - ShortwaveCloudForcing
         - LongwaveCloudForcing
         # 3D fields
         - T_mid
         - z_mid
         - qv
         - qc
         - qi
         - qr
         - qm
         - nc
         - ni
         - nr
         - tke
         - U
         - V
         - omega
         - cldfrac_tot_for_analysis
         - cldfrac_liq
         - cldfrac_ice_for_analysis
         - RelativeHumidity
         # surface oscillation diagnostics
         - T_2m_btp:=T_2m_bt1_times_T_2m_bt1_prev
         - surf_sens_flux_btp:=surf_sens_flux_bt1_times_surf_sens_flux_bt1_prev
         - wind_speed_10m_btp:=wind_speed_10m_bt1_times_wind_speed_10m_bt1_prev
         # extra diags diags
         - shoc_T_mid_tend
         - shoc_qv_tend
         - shoc_horiz_winds_tend
         - homme_T_mid_tend
         - homme_qv_tend
         - homme_horiz_winds_tend
output_control:
   frequency: 1
   frequency_units: nmonths
restart:
   force_new_file: false
'''

# - p3_T_mid_tend
# - p3_qv_tend
# - rrtmgp_T_mid_tend
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
