#!/usr/bin/env python
import os, datetime, subprocess as sp
from shutil import copy2
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
''' Notes '''
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
# src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => master @ Jun 29 2026
src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => whannah/eamxx/mcsp-shear-scaling (based on whannah/eamxx/mcsp-momentum-update)

# clean        = True
# newcase      = True
# config       = True
# build        = True
set_run_opts = True
submit       = True
# continue_run = True

# debug_mode = False

# queue = 'regular'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',6,0,'0:30:00' #; queue = 'debug'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00' #; queue = 'debug'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,9-1,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,12-1,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'5:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx ZM process testing

# check MCSP momentum - both should crash initially
# add_case(prefix='2026-MCSP-DEV-00', compset='F2010xx-ZM', grid='ne4pg2_oQU480', num_nodes=1, zm='f90', muc=0.3)
# add_case(prefix='2026-MCSP-DEV-00', compset='F2010xx-ZM', grid='ne4pg2_oQU480', num_nodes=1, zm='cxx', muc=0.3)


# kwargs_ne30 = {}
# kwargs_ne30['compset']     = 'F2010xx-ZM-CICE'
# kwargs_ne30['grid']        = 'ne30pg2_r05_IcoswISC30E3r5'
# kwargs_ne30['num_nodes']   = 8

# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='f90', ufs=False, muc=0.0 ) # f90 control
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='f90', ufs=True,  muc=0.0 ) # f90
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='f90', ufs=True,  muc=0.3 ) # f90
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='cxx', ufs=False, muc=0.0 ) # cxx control
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='cxx', ufs=True,  muc=0.0 ) # cxx
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='cxx', ufs=True,  muc=0.3 ) # cxx
# add_case(prefix='2026-MCSP-DEV-00', **kwargs_ne30, zm='cxx', ufs=True,  muc=-0.3 ) # cxx - downgradient

# full multi-year tests
# add_case(prefix='2026-ZM-DEV-00', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=12, zm='f90')
# add_case(prefix='2026-ZM-DEV-00', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=12, zm='cxx')

kwargs_ne30   = ({'compset':'F2010xx-ZM-CICE','num_nodes':4,'grid':'ne30pg2_ne30pg2'})

# 2026 shear scaling tests (started Oct 29)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, usm=False, mtc=0.3)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, usm=False, mtc=0.6)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, usm=True,  son=20, sox=60, mtc=0.3)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, usm=True,  son=20, sox=60, mtc=0.6)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, use=True,  evn=2.0e-6, evx=4.0e-6)
add_case(prefix='2026-MCSP-SS-00', **kwargs_ne30, ufs=True, use=True,  evn=0.1e-6, evx=6.0e-6)

#---------------------------------------------------------------------------------------------------
'''
usm - use_shear_scaling_mcsp    default: false
use - use_shear_scaling_evap    default: false
shn - mcsp_shear_min            default: 3
son - mcsp_shear_optimal_min    default: 0
sox - mcsp_shear_optimal_max    default: 0
shx - mcsp_shear_max            default: 200
evn - evap_efficiency_min       default: 2.5e-6
evx - evap_efficiency_max       default: 2.5e-6
esn - evap_shear_min            default: 5
esx - evap_shear_max            default: 20
'''
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
      run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      for key in ('dcape', 'ull'):
         if key in opts:
            run_cmd(f'./atmchange -b physics::zm::trig_{key}={str(opts[key]).lower()}')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      # run_cmd('./xmlchange CICE_CPPDEFS="-DCCSMCOUPLED -Dcoupled -Dncdf -DNCAT=1 -DNXGLOB=1791 -DNYGLOB=1 -DNTR_AERO=0 -DMODAL_AER"')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
      # run_cmd('./case.build --clean ice  && ./case.build')
   #------------------------------------------------------------------------------------------------
   if set_run_opts :
      #-------------------------------------------------------------------------
      if opts.get('zm') is not None:
         # if opts.get('zm')=='f90': run_cmd(f'./atmchange -b zm::use_fortran_bridge=true')
         # if opts.get('zm')=='cxx': run_cmd(f'./atmchange -b zm::use_fortran_bridge=false')
         # if opts.get('zm_detr')==0:run_cmd(f'./atmchange -b zm::apply_detr_tend=false')
         # if opts.get('zm_detr')==1:run_cmd(f'./atmchange -b zm::apply_detr_tend=true')
         # run_cmd(f'./atmchange physics::atm_procs_list=gw,mac_aero_mic,rrtmgp')
         # # run_cmd(f'./atmchange mac_aero_mic::atm_procs_list+=gw')
         # # run_cmd(f'./atmchange -b use_gw_convect=True')
         # # run_cmd(f'./atmchange -b use_gw_frontal=True')
         # run_cmd(f'./atmchange -b use_gw_orographic=True')

         
         if 'mtc' in opts: run_cmd(f'./atmchange -b zm::mcsp_t_coeff='+str(opts['mtc']))
         if 'mqc' in opts: run_cmd(f'./atmchange -b zm::mcsp_q_coeff='+str(opts['mqc']))
         if 'muc' in opts: run_cmd(f'./atmchange -b zm::mcsp_mom_coeff='+str(opts['muc']))
         
         if opts.get('ufs'):
            if     opts['ufs']: run_cmd(f'./atmchange -b zm::mcsp_use_full_shear=true')
            if not opts['ufs']: run_cmd(f'./atmchange -b zm::mcsp_use_full_shear=false')

         if 'usm' in opts: run_cmd(f'./atmchange -b zm::use_shear_scaling_mcsp={opts['usm']}')  # default: false
         if 'use' in opts: run_cmd(f'./atmchange -b zm::use_shear_scaling_evap={opts['use']}')  # default: false
         if 'shn' in opts: run_cmd(f'./atmchange -b zm::mcsp_shear_min={opts['shn']}')          # default: 3
         if 'son' in opts: run_cmd(f'./atmchange -b zm::mcsp_shear_optimal_min={opts['son']}')  # default: 0
         if 'sox' in opts: run_cmd(f'./atmchange -b zm::mcsp_shear_optimal_max={opts['sox']}')  # default: 0
         if 'shx' in opts: run_cmd(f'./atmchange -b zm::mcsp_shear_max={opts['shx']}')          # default: 200
         if 'evn' in opts: run_cmd(f'./atmchange -b zm::evap_efficiency_min={opts['evn']}')     # default: 2.5e-6
         if 'evx' in opts: run_cmd(f'./atmchange -b zm::evap_efficiency_max={opts['evx']}')     # default: 2.5e-6
         if 'esn' in opts: run_cmd(f'./atmchange -b zm::evap_shear_min={opts['esn']}')          # default: 5
         if 'esx' in opts: run_cmd(f'./atmchange -b zm::evap_shear_max={opts['esx']}')          # default: 20

         # # test if DCAPE is causing divergence on second time step
         # if 'ne4pg2_' in opts['grid']:
         #    # print(f'\n{clr.RED}WARNING - disabling DCAPE for ne4 test!{clr.END}')
         #    # run_cmd(f'./atmchange -b zm::trig_dcape=false')
         #    run_cmd(f'./atmchange -b zm::trig_dcape=true')

         # if opts.get('ts_output'):
            # print(f'\n{clr.RED}WARNING - disabling apply_detr_tend for test!{clr.END}')
            # run_cmd(f'./atmchange -b zm::apply_detr_tend=true')
      #-------------------------------------------------------------------------
      # if 'SCREAM' in opts['compset']:
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('output_1ma.yaml', get_hist_opts_1ma(opts) )
      # add_hist_file('output_1da.yaml', get_hist_opts_1da(opts) )
      # add_hist_file('output_1si.yaml', get_hist_opts_1si(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      # # disable history output
      # run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      # print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
   #------------------------------------------------------------------------------------------------
   if submit :
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
# daily mean output - native grid
def get_hist_opts_1da(opts):
   return f'''
filename_prefix: output.1da
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:
         # precipitation
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - zm_prec
         # water paths
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - LW_flux_up_at_model_top
         - T_2m
         - U_at_850hPa
         - U_at_200hPa
         - U_at_50hPa
         - U_at_20hPa
         - U_at_10hPa
         - U_at_model_top
         - T_mid_at_10hPa
output_control:
   frequency: 1
   frequency_units: ndays
'''
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
         # ---------------------------------------------------------------------
         # precipitation
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         # ---------------------------------------------------------------------
         # water paths
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         # ---------------------------------------------------------------------
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
         # ---------------------------------------------------------------------
         # 3D variables
         - T_mid
         - z_mid
         - U
         - V
         - omega
         # - pseudo_density
         # - RelativeHumidity
         # - qv
         # - qc
         # - qr
         # - qi
         # - qm
         # - nc
         # - ni
         # - nr
         # ---------------------------------------------------------------------
         # misc 2D fields
         - T_2m
         - surf_radiative_T
         - wind_speed_10m
         - surf_sens_flux
         - surf_evap
         - surf_mom_flux
         - cldfrac_liq
         - cldfrac_ice_for_analysis
         - cldfrac_tot_for_analysis
         # ---------------------------------------------------------------------
         # process stendencies
         # - p3_T_mid_tend
         # - p3_qv_tend
         # - shoc_T_mid_tend
         # - shoc_qv_tend
         # - shoc_horiz_winds_tend
         # - homme_T_mid_tend
         # - homme_qv_tend
         # - rrtmgp_T_mid_tend
         - zm_T_mid_tend
         - zm_qv_tend
         # - zm_horiz_winds_tend
         # - gw_horiz_winds_tend
         # - gw_oro_tend_u
         # - gw_conv_tend_u
         - zm_detr_qc
         - zm_detr_qi
         # ---------------------------------------------------------------------
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
         - evap_ds_out
         - evap_dq_out
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
