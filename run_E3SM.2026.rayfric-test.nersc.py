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
'''NOTES
branch whannah/scidac-2026-v4-tuning was made on Sep 29 using:
=> master @ Sep 29
=> merge whannah/eamxx/conv-gw-fix
=> merge whannah/eamxx/fix-zm-non-bfb
=> merge whannah/eamxx/mcsp-momentum-update

nohup python -u run_E3SM.2026.rayfric-test.nersc.py > run_E3SM.2026.rayfric-test.nersc.py.out &
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'm4310'
top_dir = os.getenv('HOME')+'/E3SM'
# src_dir = f'{top_dir}/E3SM_SRC0' # branch => whannah/eamxx/add-rayleigh-friction
src_dir = f'{top_dir}/E3SM_SRC0' # branch => whannah/eamxx/add-rayleigh-friction-merge-gw-fix

# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True


# stop_opt,stop_n,resub,walltime,queue = 'ndays',10,0,'1:00:00','regular'
# stop_opt,stop_n,resub,walltime,queue = 'ndays',365,4-1,'32:00:00','regular'

#---------------------------------------------------------------------------------------------------

# kwargs_common = {'prefix':'2026-RAYFRIC-TEST-00','compset':'F2010xx-ZM-CICE','arch':'GPU'}
kwargs_ne256  = ({'num_nodes':64,'grid':'ne256pg2_ne256pg2'})
kwargs_ne30   = ({'num_nodes':4,'grid':'ne30pg2_ne30pg2'})

# stop_opt,stop_n,resub,walltime,queue = 'ndays',10,0,'1:00:00','regular'
# add_case(**kwargs_common, **kwargs_ne256, gw='oc', draytau=0, praytau=0) # control - GWD enabled, rayleigh frictin disabled
# add_case(**kwargs_common, **kwargs_ne256, gw='oc', draytau=0, praytau=5)
# add_case(**kwargs_common, **kwargs_ne256, gw='oc', draytau=5, praytau=0)

# stop_opt,stop_n,resub,walltime,queue = 'ndays',32,0,'0:30:00','debug'
# add_case(**kwargs_common, **kwargs_ne30, gw='oc', draytau=0, praytau=0) # control
# add_case(**kwargs_common, **kwargs_ne30, gw='oc', draytau=0, praytau=5)
# add_case(**kwargs_common, **kwargs_ne30, gw='oc', draytau=5, praytau=0)

# stop_opt,stop_n,resub,walltime,queue = 'ndays',32,0,'0:30:00','debug'
# add_case(**kwargs_common, **kwargs_ne30, gw='oc', draytau=0, praytau=5, goe=0.1)
# add_case(**kwargs_common, **kwargs_ne30, gw='oc', draytau=5, praytau=0, goe=0.1)

# add_case(**kwargs_common, **kwargs_ne30, vgrid='L72', gw='oc', draytau=0, praytau=0)

# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=0, praytau=0) # control - retry w/o splittform
# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=0, praytau=0, goe=0)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=0, praytau=0, goe=0.1)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=0, praytau=0, goe=0.2)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=0, praytau=5)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', draytau=5, praytau=0)

# add_case(**kwargs_common, **kwargs_ne30, gw='c', draytau=0, praytau=0) # control
# add_case(**kwargs_common, **kwargs_ne30, gw='c', draytau=0, praytau=5)
# add_case(**kwargs_common, **kwargs_ne30, gw='c', draytau=5, praytau=0)

# stop_opt,stop_n,resub,walltime,queue = 'ndays',20,0,'0:30:00','debug'
# add_case(**kwargs_common, **kwargs_ne30, draytau=0, praytau=0) # control - rayleigh frictin disabled
# add_case(**kwargs_common, **kwargs_ne30, draytau=0, praytau=5)
# add_case(**kwargs_common, **kwargs_ne30, draytau=5, praytau=0)

# ,gcc=10,gce=0.35,gch=0.50,gcm=2.5


kwargs_common = {'prefix':'2026-RAYFRIC-TEST-01','compset':'F2010xx-ZM-CICE','arch':'GPU'}

stop_opt,stop_n,resub,walltime,queue = 'ndays',32,0,'0:30:00','debug'
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=2, pgc=0, rmf=2)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=0, rmf=2)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=1, rmf=2)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=2, pgc=0, rmf=1)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=0, rmf=1)
# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=1, rmf=1)

# add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=2, pgc=0, dt_rcp=1)
add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=0, dt_rcp=1)
add_case(**kwargs_common, **kwargs_ne30, gw='o', drt=0, prt=0, taf=1, pgc=1, dt_rcp=1)

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      case_list.append(val.split('_')[0])
      elif key in ['compset']:   continue
      elif key in ['arch']:      continue
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: continue # case_list.append(f'NN_{val}')
      elif key in ['num_tasks']: continue # case_list.append(f'NT_{val}')
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
      if opts.get('vgrid') is not None:
         run_cmd(f'./xmlchange EAMXX_VGRID={opts.get('vgrid')}')
      else:
         run_cmd(f'./xmlchange EAMXX_VGRID=L128v4')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if set_run_opts:
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      #-------------------------------------------------------------------------
      # init_root = '/global/cfs/cdirs/e3sm/inputdata/atm/scream/init'
      # run_cmd(f'./atmchange -b vertical_coordinate_filename=\"{init_root}/vertical_coordinates_L128_20220927.nc\"')
      # init_file = None
      # if 'ne30pg2'  in opts['grid']: init_file = f'{init_root}/eamxxi_ne30np4L128v4_ERA5-20190101_c20260922.nc'
      # if 'ne256pg2' in opts['grid']: init_file = f'{init_root}/eamxxi_ne256np4L128v4_ERA5-20190101_c20260922.nc'
      # if init_file is None: raise ValueError('forgot to set init_file?')
      # run_cmd(f'./atmchange -b initial_conditions::filename=\"{init_file}\"')
      # run_cmd(f'./atmchange -b initial_conditions::nc=0.0')
      # run_cmd(f'./atmchange -b initial_conditions::ni=0.0')
      # # sponge layer
      # run_cmd(f'./atmchange -b tom_sponge_start=15 ')
      # run_cmd(f'./atmchange -b laplace_scaling=1 ')
      # run_cmd(f'./atmchange -b nu_top=5e-7 ')
      # split form
      # run_cmd(f'./atmchange -b theta_advect_form=2 ')
      # run_cmd(f'./atmchange -b pgrad_correction=0 ')

      # run_cmd(f'./atmchange -b theta_advect_form=1 ')
      # run_cmd(f'./atmchange -b pgrad_correction=1 ')

      # run_cmd(f'./atmchange -b theta_advect_form=1 ')
      # run_cmd(f'./atmchange -b pgrad_correction=0 ')

      if opts.get('taf') is not None: run_cmd(f'./atmchange -b theta_advect_form={opts.get('taf')}')
      if opts.get('pgc') is not None: run_cmd(f'./atmchange -b pgrad_correction={opts.get('pgc')}')

      if opts.get('rmf') is not None: run_cmd(f'./atmchange -b dt_remap_factor={opts.get('rmf')}')
      #-------------------------------------------------------------------------
      if opts.get('gw') is not None:
         run_cmd(f'./atmchange -b physics::atm_procs_list=rayleigh_friction,zm,gw,mac_aero_mic,rrtmgp')
      else:
         run_cmd(f'./atmchange -b physics::atm_procs_list=rayleigh_friction,zm,mac_aero_mic,rrtmgp')
      #-------------------------------------------------------------------------
      if opts.get('gw') is not None:
         gw_cnv = 'true' if 'c' in opts.get('gw') else 'false'
         gw_oro = 'true' if 'o' in opts.get('gw') else 'false'
         run_cmd(f'./atmchange -b physics::gw::use_gw_convect={gw_cnv}')
         run_cmd(f'./atmchange -b physics::gw::use_gw_orographic={gw_oro}')
      if opts.get('goe') is not None: run_cmd(f'./atmchange -b physics::gw::gw_orographic_eff={opts.get('goe')}')
      if opts.get('gcc') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hcf={opts.get('gcc')}')
      if opts.get('gce') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_eff={opts.get('gce')}')
      if opts.get('gch') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hdepth_scale={opts.get('gch')}')
      if opts.get('gcm') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hdepth_min={opts.get('gcm')}')
      # if opts.get('gcs') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_storm_speed_min={opts.get('gcs')}')
      # if opts.get('gcp') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_plev_src_wind={opts.get('gcp')}')
      #-------------------------------------------------------------------------
      if opts.get('prt') is not None: run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_decay_time={opts.get('prt')}')
      if opts.get('drt') is not None: run_cmd(f'./atmchange -b homme::rayleigh_friction_decay_time={opts.get('drt')}')
      #-------------------------------------------------------------------------
      if opts.get('dt_rcp') is not None:
         if opts.get('dt_rcp')==1:
            run_cmd(f'./atmchange -b se_tstep=200 ')
            run_cmd(f'./atmchange -b dt_remap_factor=3 ')
            run_cmd(f'./atmchange -b dt_tracer_factor=3 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_q=3 ')
            # run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=2 ')
            # run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')
      #-------------------------------------------------------------------------
      # Enable process tendencies for output
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd(f'./atmchange -b physics::gw::compute_tendencies=horiz_winds')
      # run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      # add_hist_file('output_1ma.yaml', get_hist_opts_1ma(opts) )
      # add_hist_file('output_1da.yaml', get_hist_opts_1da(opts) )
      add_hist_file('output_1si.yaml', get_hist_opts_1si(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # # disable history output
      # run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      # print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
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
# time step instantaneous output
def get_hist_opts_1si(opts):
   return f'''
filename_prefix: output.1si
averaging_type: instant
max_snapshots_per_file: 144
fields:
   physics_pg2:
      field_names:
         - U
         - V
         - T_mid
         - ps
         - gw_oro_tend_u
         - gw_oro_tend_v
         - gw_oro_tend_t
output_control:
   frequency: 1
   frequency_units: nsteps
'''
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
         # - nc
         # - ni
         # - nr
         # misc 2D fields
         - T_2m
         # - surf_radiative_T
         - wind_speed_10m
         - surf_sens_flux
         - surf_evap
         - surf_mom_flux
         - cldfrac_liq
         - cldfrac_ice_for_analysis
         - cldfrac_tot_for_analysis
         # process stendencies
         - p3_T_mid_tend
         - p3_qv_tend
         - shoc_T_mid_tend
         - shoc_qv_tend
         - shoc_horiz_winds_tend
         - homme_T_mid_tend
         - homme_qv_tend
         - rrtmgp_T_mid_tend
         - zm_T_mid_tend
         - zm_qv_tend
         - zm_horiz_winds_tend
         - gw_horiz_winds_tend
         - gw_oro_tend_u
         - gw_conv_tend_u
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
