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
# interpolating land IC
LND_IC_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata
LND_IC_SRC=${LND_IC_ROOT}/20240104.I2010CRUELM.ne256pg2.elm.r.2016-08-01-00000.nc
LND_IC_DST=${LND_IC_ROOT}/20240104.I2010CRUELM.ne128pg2.elm.r.2016-08-01-00000.nc
interpinic -i 

#-------------------------------------------------------------------------------
# vertical remap
DST_VERT=/lustre/orion/cli115/proj-shared/hannah6/files_vert/SCREAM_L128_v3.6_c20251112.cdf5.nc
INIT_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init
SRC_FILE=${INIT_ROOT}/screami_ne256np4L128_ifs-20200120_20220914.nc
DST_FILE=${INIT_ROOT}/screami_ne256np4L128_ifs-20200120_20220914.L128_v3.6.nc

ncremap -4 --ps_nm=ps --vrt_fl=${DST_VERT} --in_fl=${SRC_FILE} --out_fl=${DST_FILE}

# # This doesn't work - same error as above without the -4 option
# ncatted -O -a _FillValue,,o,d,1.0e36 ${DST_FILE} ${DST_FILE}.tmp
# ncks -5 ${DST_FILE}.tmp ${DST_FILE}.tmp.cdf5
# mv ${DST_FILE}.cdf5 ${DST_FILE}

ncatted -O -a _FillValue,ps,d,, ${DST_FILE} ${DST_FILE}.tmp
ncks -5 ${DST_FILE}.tmp ${DST_FILE}.tmp.cdf5
mv ${DST_FILE}.tmp.cdf5 ${DST_FILE}
rm ${DST_FILE}.tmp

'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => master @ Jul 21 2026 - 656bc155a9f990052e4b60b7f73a786ad978cdea

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'nmonths',6,5*2-1,'6:00:00' # 5-years / ne256 / 128-nodes - DID NOT WORK!
# stop_opt,stop_n,resub,walltime = 'nmonths',4,5*3-1,'6:00:00' # 5-years / ne256 / 128-nodes
stop_opt,stop_n,resub,walltime = 'nmonths',4,5*3+2-1,'6:00:00' # 5-years + aug init / ne256 / 128-nodes
# stop_opt,stop_n,resub,walltime = 'nmonths',4,2-1,'6:00:00' # extra time to finish year 6
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'5:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx ZM process testing

vert_root = '/lustre/orion/cli115/proj-shared/hannah6/files_vert'
init_root = '/lustre/orion/cli115/proj-shared/hannah6/files_init'

kwargs_L128v36 = {'vgrid_name':'L128v3.6'}
kwargs_L128v36['vgrid_file'] = f'{vert_root}/SCREAM_L128_v3.6_c20251112.nc'
kwargs_L128v36['init_file']  = f'{init_root}/screami_ne256np4L128_ifs-20200120_20220914.L128_v3.6.nc'

# add_case(prefix='2026-ZM-BASE-00', grid='ne256pg2_ne256pg2', num_nodes=128, compset='F2010-SCREAMv1' )
# add_case(prefix='2026-ZM-BASE-00', grid='ne256pg2_ne256pg2', num_nodes=128, compset='F2010xx-ZM-CICE' )

add_case(prefix='2026-ZM-BASE-00', grid='ne256pg2_ne256pg2', num_nodes=128, compset='F2010xx-ZM-CICE', **kwargs_L128v36 )

# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
# add_case(prefix='2026-ZM-BASE-00', grid='ne4pg2_ne4pg2', num_nodes=1, compset='F2010xx-ZM-CICE' )

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   for ne in [4,30,32,64,128,256,512,1024]:
      if f'ne{ne}pg2_' in opts['grid']:
         grid_name = f'ne{ne}pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: case_list.append(f'NN_{val}')
      elif key in ['num_tasks']: case_list.append(f'NT_{val}')
      elif key in ['cosp'] and opts.get('cosp'):  case_list.append('COSP')
      elif key in ['vgrid_name']:      case_list.append(f'{val}')
      elif key in ['vgrid_file']:      continue
      elif key in ['init_file']:       continue
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
   machine,compiler = 'frontier','craygnu-mphipcc'
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
   atm_ntasks = 8*opts['num_nodes'] # 8 GPU per node
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
      cmd += f' --pecount {atm_ntasks}x1 --machine={machine} --compiler={compiler} '
      run_cmd(cmd)
      #-------------------------------------------------------------------------
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
      # Enable COSP
      if opts.get('cosp',False):
         run_cmd(f'./atmchange physics::atm_procs_list+=cosp')
      #-------------------------------------------------------------------------
      # Enable tendency calculation for output
      if not opts.get('debug',False):
         run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
         run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
         run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
         run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
         if 'F2010xx-ZM' in opts['compset']:
            run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv')
            run_cmd(f'./atmchange -b zm::use_fortran_bridge=false')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      # use updated SPA data file - first baseline pair missed this
      DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
      run_cmd(f'./atmchange spa_data_file="{DIN_LOC_ROOT}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      #-------------------------------------------------------------------------
      if 'ne4pg2_' in opts.get('grid'):
         init_root = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init'
         init_file = f'{init_root}/screami_ne4np4L128_20241022.nc'
         run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
         run_cmd(f'./xmlchange --file env_run.xml  RUN_STARTDATE=0001-01-01')
      if 'ne256pg2_' in opts.get('grid'):
         init_root = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init'
         # init_file = f'{init_root}/screami_ne256np4L128_ifs-20200120_20220914.nc' # default
         init_file = f'{init_root}/screami_ne256np4L128_era5-20190801-topoadjx6t_20230620.nc'
         run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
         run_cmd(f'./xmlchange --file env_run.xml  RUN_STARTDATE=0001-08-01')
         # run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_yr}')
      #-------------------------------------------------------------------------
      if 'ne256pg2_' in opts.get('grid'):
         lnd_init_root = '/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata'
         lnd_init_file = '20240104.I2010CRUELM.ne256pg2.elm.r.2016-08-01-00000.nc'
         # lnd_init_file = '20240104.I2010CRUELM.ne256pg2.elm.r.1994-10-01-00000.nc'
         # lnd_init_file = '20230522.I2010CRUELM.ne256pg2.elm.r.2013-08-01-00000.nc'
         file=open('user_nl_elm','w')
         file.write(f' finidat = \'{lnd_init_root}/{lnd_init_file}\' \n')
         # default fsurdat => lnd/clm2/surfdata_map/surfdata_ne256pg2_simyr2010_c230207.nc
         # file.write(f' fsurdat = \'{lnd_data_root}/{lnd_data_file}\' \n')
         file.close()
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      if not opts.get('debug',False):
         if 'ne4pg2_' in opts.get('grid'):
            add_hist_file('scream_output_1da_debug.yaml', get_hist_opts_1da_debug(opts) )
         if 'ne256pg2_' in opts.get('grid'):
            add_hist_file('scream_output_3hi.yaml',      get_hist_opts_3hi(opts) )
            add_hist_file('scream_output_1da.yaml',      get_hist_opts_1da(opts) )
            add_hist_file('scream_output_1ma.yaml',      get_hist_opts_1ma(opts) )
            add_hist_file('scream_output_3ha_ne30.yaml', get_hist_opts_3ha_ne30(opts) )
            add_hist_file('scream_output_1da_ne30.yaml', get_hist_opts_1da_ne30(opts) )
            add_hist_file('scream_output_1ma_ne30.yaml', get_hist_opts_1ma_ne30(opts) )
         hist_file_list_str = ','.join(hist_file_list)
         run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
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
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 

#---------------------------------------------------------------------------------------------------
fields_1da_main = f'''
         - ps
         - SeaLevelPressure
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - T_2m
         - wind_speed_10m
         - snow_depth_land
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
         - U_at_850hPa
         - U_at_200hPa
         # - omega_at_500hPa
         # - omega_at_700hPa
         # - omega_at_850hPa
         # - U_at_model_bot
         # - V_at_model_bot
'''
fields_1da_zm = f'''
         - zm_prec
         - zm_activity
'''
#---------------------------------------------------------------------------------------------------
fields_1ma_main = f'''
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
         # - LiqNumberPath
         # - IceNumberPath
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
         # - eff_radius_qc
         # - eff_radius_qi
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
         - U_at_850hPa
         - U_at_200hPa
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
         - homme_T_mid_tend
         - homme_qv_tend
         - rrtmgp_T_mid_tend
'''
fields_1ma_zm = f'''
         - zm_T_mid_tend
         - zm_qv_tend
         - zm_detr_qc
         - zm_detr_qi
         - mcsp_ds_out
         - mcsp_freq
         - mcsp_shear
         - zm_depth
         - evap_ds_out
         - evap_dq_out
         - zm_cape
         - zm_dcape
         - zm_prec
         - zm_activity
'''
fields_1ma_cosp = f'''
         # COSP
         - isccp_ctptau
         - isccp_cldtot
'''
#---------------------------------------------------------------------------------------------------

# map_file = '/global/cfs/cdirs/e3sm/inputdata/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc'
map_file = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc'

#------------------------------------------------
# 3-hr instant output for storm tracking - native grid
def get_hist_opts_3hi(opts):
   return f'''
filename_prefix: output.3hi
averaging_type: instant
max_snapshots_per_file: 40
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         - T_mid_at_200hPa
         - T_mid_at_500hPa
         - U_at_model_bot
         - V_at_model_bot
         - U_at_850hPa
         - V_at_850hPa
         - ZonalVapFlux
         - MeridionalVapFlux
         - T_2m
         - wind_speed_10m
         - LW_flux_up_at_model_top
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
output_control:
   frequency: 3
   frequency_units: nhours
'''
#------------------------------------------------
# 3-hr average output for diurnal cycle - ne30pg2
def get_hist_opts_3ha_ne30(opts):
   return f'''
filename_prefix: output.ne30pg2.1ha
horiz_remap_file: {map_file}
averaging_type: average
max_snapshots_per_file: 120
fields:
   physics_pg2:
      field_names:
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - LW_flux_up_at_model_top
         - T_2m
         - wind_speed_10m
output_control:
   frequency: 1
   frequency_units: nhours
'''
#------------------------------------------------
# daily mean output - native grid
def get_hist_opts_1da(opts):
   return f'''
filename_prefix: output.1da
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:{fields_1da_main + (fields_1da_zm if 'F2010xx-ZM' in opts['compset'] else '')}
output_control:
   frequency: 24
   frequency_units: nhours
'''
#------------------------------------------------
# daily mean output - ne30pg2
def get_hist_opts_1da_ne30(opts):
   return f'''
filename_prefix: output.ne30pg2.1da
horiz_remap_file: {map_file}
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:{fields_1da_main+(fields_1da_zm if 'F2010xx-ZM' in opts['compset'] else '')}
output_control:
   frequency: 24
   frequency_units: nhours
'''
#------------------------------------------------
# monthly mean output - native grid
def get_hist_opts_1da_debug(opts):
   return f'''
filename_prefix: output.debug.1da
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:{fields_1ma_main
                  +(fields_1ma_zm if 'F2010xx-ZM' in opts['compset'] else '')
                  +(fields_1ma_cosp if opts.get('cosp',False) else '')}
output_control:
   frequency: 24
   frequency_units: nhours
'''
#------------------------------------------------
# monthly mean output - native grid
def get_hist_opts_1ma(opts):
   return f'''
filename_prefix: output.1ma
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{fields_1ma_main
                  +(fields_1ma_zm if 'F2010xx-ZM' in opts['compset'] else '')
                  +(fields_1ma_cosp if opts.get('cosp',False) else '')}
output_control:
   frequency: 1
   frequency_units: nmonths
'''
#------------------------------------------------
# monthly mean output - ne30pg2
def get_hist_opts_1ma_ne30(opts):
   return f'''
filename_prefix: output.ne30pg2.1ma
horiz_remap_file: {map_file}
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{fields_1ma_main
                  +(fields_1ma_zm if 'F2010xx-ZM' in opts['compset'] else '')
                  +(fields_1ma_cosp if opts.get('cosp',False) else '')}
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
