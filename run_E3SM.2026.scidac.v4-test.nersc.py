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

nohup python -u run_E3SM.2026.scidac.v4-test.nersc.py > run_E3SM.2026.scidac.v4-test.nersc.py.out &
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC2' # branch => whannah/scidac-2026-v4-tuning

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'

#---------------------------------------------------------------------------------------------------

kwargs = {'prefix':'2026-SCIDAC-V4-00','compset':'F2010xx-ZM-CICE'}
kwargs.update({'arch':'GPU','num_nodes':64,'grid':'ne256pg2_ne256pg2'})

add_case(**kwargs,gw='oc',cpt=0,gcc=10,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=0,gcc= 6,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=0,gcc= 2,gce=0.35,gch=0.50,gcm=2.5)

# add_case(**kwargs,gw='oc',cpt=200,gcc=10,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=200,gcc= 6,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=200,gcc= 2,gce=0.35,gch=0.50,gcm=2.5)

# add_case(**kwargs,gw='oc',cpt=400,gcc=10,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=400,gcc= 6,gce=0.35,gch=0.50,gcm=2.5)
# add_case(**kwargs,gw='oc',cpt=400,gcc= 2,gce=0.35,gch=0.50,gcm=2.5)

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
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      #-------------------------------------------------------------------------
      init_root = '/global/cfs/cdirs/e3sm/inputdata/atm/scream/init'
      run_cmd(f'./atmchange -b initial_conditions::filename=\"{init_root}/eamxxi_ne128np4L128v4_ERA5-20190101_c20260922.nc\"')
      run_cmd(f'./atmchange -b vertical_coordinate_filename=\"{init_root}/vertical_coordinates_L128_20220927.nc\"')
      # sponge layer
      run_cmd(f'./atmchange -b tom_sponge_start=15 ')
      run_cmd(f'./atmchange -b laplace_scaling=1 ')
      run_cmd(f'./atmchange -b nu_top=5e-7 ')
      # split form
      run_cmd(f'./atmchange -b theta_advect_form=2 ')
      run_cmd(f'./atmchange -b pgrad_correction=0 ')
      #-------------------------------------------------------------------------
      if opts.get('gw') is not None:  run_cmd(f'./atmchange -b physics::atm_procs_list=zm,gw,mac_aero_mic,rrtmgp')
      if 'o' in opts.get('gw'):       run_cmd(f'./atmchange -b physics::gw::use_gw_convect=True')
      if 'c' in opts.get('gw'):       run_cmd(f'./atmchange -b physics::gw::use_gw_orographic=True')
      if opts.get('gcc') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hcf={opts.get('gcc')}')
      if opts.get('gce') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_eff={opts.get('gce')}')
      if opts.get('gch') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hdepth_scale={opts.get('gch')}')
      if opts.get('gcm') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_hdepth_min={opts.get('gcm')}')
      # if opts.get('gcs') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_storm_speed_min={opts.get('gcs')}')
      # if opts.get('gcp') is not None: run_cmd(f'./atmchange -b physics::gw::gw_convect_plev_src_wind={opts.get('gcp')}')
      #-------------------------------------------------------------------------
      if opts.get('cpt') is not None: run_cmd(f'./atmchange -b physics::zm::cape_threshold={opts.get('cpt')}')
      if opts.get('dct') is not None: run_cmd(f'./atmchange -b physics::zm::dcape_threshold={opts.get('dct')}')
      if opts.get('msh')=='new':      run_cmd(f'./atmchange -b physics::zm::mcsp_use_full_shear=true ')
      if opts.get('msh')=='old':      run_cmd(f'./atmchange -b physics::zm::mcsp_use_full_shear=false ')
      if opts.get('mct') is not None: run_cmd(f'./atmchange -b physics::zm::mcsp_t_coeff={opts.get('mct')}')
      if opts.get('mcq') is not None: run_cmd(f'./atmchange -b physics::zm::mcsp_q_coeff={opts.get('mcq')}')
      if opts.get('mcu') is not None: run_cmd(f'./atmchange -b physics::zm::mcsp_mom_coeff={opts.get('mcu')}')
      #-------------------------------------------------------------------------
      # Enable process tendencies for output
      run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv,horiz_winds')
      run_cmd(f'./atmchange -b physics::gw::compute_tendencies=horiz_winds')
      run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
      run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('output_1ma.yaml', get_hist_opts_1ma(opts) )
      add_hist_file('output_1da.yaml', get_hist_opts_1da(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # # disable history output
      # run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      # print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
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
         - LW_flux_up_at_model_bot
         - T_2m
         - U_at_850hPa
         - U_at_200hPa
         - U_at_50hPa
         - U_at_20hPa
         - U_at_10hPa
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
