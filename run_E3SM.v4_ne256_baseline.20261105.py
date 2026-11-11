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
Frontier version of the NERSC production script:
   v4_dev_scripts/run.test.ne256.20260909.ZM.splitform.newL128.Recipe2_updated.GWD.sh
   (NERSC case => ne256pg2_ne256pg2.F2010xx-ZM-CICE.20260924.splitform_TMSoff_Recipe2_updated_GWD)

whannah/eamxx/conv-gw-fix (PR #8764) is already merged into master,
so it is included in all of the current E3SM_SRC* checkouts

differences from the NERSC script:
- PE layout uses 8 GCDs per node (NERSC used 128 nodes x 4 GPUs = 512 ranks)
- vertical levels are set via EAMXX_VGRID=L128v4 instead of SCREAM_NUM_VERTICAL_LEV
  (buildlib_cmake now errors if SCREAM_NUM_VERTICAL_LEV is in SCREAM_CMAKE_OPTIONS)
- NTHRDS_LND/ICE=16 is not used (only 56 cores per Frontier node w/ 8 ranks per node)
- Frontier walltime limit is 12 hours, so the run is split into 6-month segments
- the land IC (finidat) was not on Frontier when this script was written,
  but it is on the E3SM inputdata server, so check_input_data should download it

nohup python -u v4_dev_scripts/run.ne256_baseline.20261105.py > v4_dev_scripts/run.ne256_baseline.20261105.py.out &

whannah/eamxx/v4-baseline-20261105 is made up of these branches merged in order
  - master @ Nov 5 c289f3dd986f3e0579e999f8b3445902afe315eb
  - whannah/eamxx/enable-weak-tms
  - whannah/eamxx/update-gwd-wind-check
  - whannah/eamxx/add-rayleigh-friction
  - whannah/whannah/eamxx/cosp-cxx-port (whannah => git@github.com:whannah1/E3SM.git)
extra additions
  - add F2010xx-BETA / F2010xx-BETA-CICE compsets
  - enable gw process
  - enable cxx COSP
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'cli217' # cli115 / cli217
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC0' # branch => whannah/eamxx/v4-baseline-20261105



# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True

# stop_opt,stop_n,resub,walltime = 'nsteps',12,0,'0:30:00' # short test
stop_opt,stop_n,resub,walltime = 'nmonths',3,4*5-1,'6:00:00' # 5 years in 3-month segments

#---------------------------------------------------------------------------------------------------
DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'

add_case( prefix='2026-v4-baseline-00',
          compset='F2010xx-BETA-CICE',
          num_nodes=128,
          grid='ne256pg2_ne256pg2',
          datestamp='20261105' )

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items():
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      case_list.append(val.split('_')[0])
      elif key in ['tuning']:    case_list.append(val)
      elif key in ['datestamp']: case_list.append(val)
      elif key in ['compset']:   continue
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

   print(f'{case}')
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
   #------------------------------------------------------------------------------------------------
   machine,compiler = 'frontier','craygnu-mphipcc'
   if 'num_nodes' in opts:
      max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
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
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      run_cmd(f'./xmlchange DOUT_S=FALSE')
      run_cmd('./case.setup --reset')
      # save provenance info
      githash = sp.check_output(f'git -C {src_dir} rev-parse HEAD',shell=True,universal_newlines=True).strip()
      with open('GIT_INFO.txt','w') as f: f.write(f'branch hash for EAMxx: {githash}\n')
   #------------------------------------------------------------------------------------------------
   if build :
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if set_run_opts:
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange RUN_STARTDATE=2010-01-01')
      #-------------------------------------------------------------------------
      # GHG levels more appropriate for sim - Average from 19940101 - 20150101
      run_cmd(f'./atmchange -b co2vmr=377.2e-6')
      run_cmd(f'./atmchange -b ch4vmr=1786.6e-9')
      run_cmd(f'./atmchange -b n2ovmr=318.6e-9')
      run_cmd(f'./atmchange -b orbital_year=-9999')
      run_cmd(f'./xmlchange CCSM_CO2_PPMV=377.2') # use same CO2 in land model
      #-------------------------------------------------------------------------
      # aerosol / microphysics tuning ("Recipe2_updated")
      run_cmd(f'./atmchange -b spa_data_file="{DIN_LOC_ROOT}/atm/scream/init/spa_from_v3LRamip_CMIP6_2010_clim_ne30pg2_c20260928.nc"')
      run_cmd(f'./atmchange -b spa_ccn_to_nc_factor=750.0')
      run_cmd(f'./atmchange -b length_fac=0.51')
      run_cmd(f'./atmchange -b autoconversion_prefactor=2960.0')
      run_cmd(f'./atmchange -b autoconversion_qc_exponent=2.42')
      #-------------------------------------------------------------------------
      # land settings
      lnd_init_file = f'{DIN_LOC_ROOT}/lnd/clm2/initdata/20240305.I2010CRUELM.ne256pg2.elm.r.2020-01-20-00000.nc'
      file=open('user_nl_elm','w')
      file.write(f''' finidat = '{lnd_init_file}'
 hist_dov2xy = .true.,.true.
 hist_mfilt = 1,1
 hist_nhtfrq = 0,-24
 hist_avgflag_pertape = 'A','A'
 hist_fincl1 = 'FIRE', 'FPSN', 'QDRAI', 'QRUNOFF', 'ZWT', 'FSAT', 'H2OSOI', 'EFLX_LH_TOT',
               'QVEGT', 'QVEGE', 'FSH', 'ALBD', 'ALBI', 'TBOT', 'QBOT', 'RAIN', 'SNOW',
               'FSDS', 'FSDSND', 'FSDSNI', 'FSDSVD', 'FSDSVI', 'FLDS'
 hist_fincl2 = 'H2OSNO','SOILWATER_10CM','TG'
''')
      file.close()
      #-------------------------------------------------------------------------
      # turn off CICE history output
      file=open('user_nl_cice','w')
      file.write(" histfreq = 'x','x','x','x','x'\n")
      file.write(" histfreq_n = 0,0,0,0,0\n")
      file.close()
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('output_1ma_ne30.yaml', get_hist_opts_1ma_ne30(opts) )
      add_hist_file('output_1da_ne30.yaml', get_hist_opts_1da_ne30(opts) )
      add_hist_file('output_1hi.yaml',      get_hist_opts_1hi(opts) )
      add_hist_file('output_3hi.yaml',      get_hist_opts_3hi(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange REST_OPTION=nmonths,REST_N=3')
      run_cmd(f'./xmlchange HIST_OPTION=never,HIST_N=1')
      run_cmd(f'./xmlchange BUDGETS=TRUE')
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
      if not continue_run: run_cmd('./xmlchange --file env_run.xml RUN_TYPE=startup,CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
# monthly mean output - remapped to ne30pg2
def get_hist_opts_1ma_ne30(opts):
   return f'''
filename_prefix: output.1ma_ne30pg2
averaging_type: average
max_snapshots_per_file: 1
horiz_remap_file: {DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc
iotype: pnetcdf
fields:
   physics_pg2:
      field_names:
         # ---------------------------------------------------------------------
         # 3D fields
         - T_mid
         - qv
         - RelativeHumidity
         - qc
         - qi
         - qr
         - qm
         - nc
         - ni
         - nr
         - cldfrac_tot_for_analysis
         - cldfrac_ice_for_analysis
         - cldfrac_liq
         - omega
         - U
         - V
         - z_mid
         - p_mid
         - tke
         # ---------------------------------------------------------------------
         # radiation
         - SW_flux_up_at_model_top := SW_flux_up.isel(lev=0)
         - SW_flux_dn_at_model_top := SW_flux_dn.isel(lev=0)
         - LW_flux_up_at_model_top := LW_flux_up.isel(lev=0)
         - SW_clrsky_flux_up_at_model_top := SW_clrsky_flux_up.isel(lev=0)
         - SW_clrsky_flux_dn_at_model_top := SW_clrsky_flux_dn.isel(lev=0)
         - LW_clrsky_flux_up_at_model_top := LW_clrsky_flux_up.isel(lev=0)
         - SW_flux_up_at_model_bot := SW_flux_up.isel(lev=-1)
         - SW_flux_dn_at_model_bot := SW_flux_dn.isel(lev=-1)
         - LW_flux_up_at_model_bot := LW_flux_up.isel(lev=-1)
         - LW_flux_dn_at_model_bot := LW_flux_dn.isel(lev=-1)
         - SW_clrsky_flux_up_at_model_bot := SW_clrsky_flux_up.isel(lev=-1)
         - SW_clrsky_flux_dn_at_model_bot := SW_clrsky_flux_dn.isel(lev=-1)
         - LW_clrsky_flux_dn_at_model_bot := LW_clrsky_flux_dn.isel(lev=-1)
         - ShortwaveCloudForcing
         - LongwaveCloudForcing
         # ---------------------------------------------------------------------
         # misc 2D fields
         - ps
         - SeaLevelPressure
         - T_2m
         - qv_2m
         - surf_radiative_T
         - VapWaterPath
         - IceWaterPath
         - LiqWaterPath
         - RainWaterPath
         - ZonalVapFlux
         - MeridionalVapFlux
         - surf_evap
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - landfrac
         - ocnfrac
         - PotentialTemperature_at_700hPa := PotentialTemperature.interp(p_mid=700,units='hPa')
         - PotentialTemperature_at_850hPa := PotentialTemperature.interp(p_mid=850,units='hPa')
         - PotentialTemperature_at_1000hPa := PotentialTemperature.interp(p_mid=1000,units='hPa')
         - PotentialTemperature_at_2m_above_surface := PotentialTemperature.interp(z_mid=2,reference='surface')
         - omega_at_500hPa := omega.interp(p_mid=500,units='hPa')
         - omega_at_700hPa := omega.interp(p_mid=700,units='hPa')
         - omega_at_850hPa := omega.interp(p_mid=850,units='hPa')
         - RelativeHumidity_at_700hPa := RelativeHumidity.interp(p_mid=700,units='hPa')
         - RelativeHumidity_at_1000hPa := RelativeHumidity.interp(p_mid=1000,units='hPa')
         - RelativeHumidity_at_2m_above_surface := RelativeHumidity.interp(z_mid=2,reference='surface')
         - wind_speed_10m
         - z_mid_at_700hPa := z_mid.interp(p_mid=700,units='hPa')
         - z_mid_at_1000hPa := z_mid.interp(p_mid=1000,units='hPa')
         - T_mid_at_850hPa := T_mid.interp(p_mid=850,units='hPa')
         - T_mid_at_700hPa := T_mid.interp(p_mid=700,units='hPa')
         # for SST advection
         - U_at_10m_above_surface := U.interp(z_mid=10,reference='surface')
         - V_at_10m_above_surface := V.interp(z_mid=10,reference='surface')
         # ---------------------------------------------------------------------
         # COSP
         - isccp_ctptau
         - modis_ctptau
         - misr_cthtau
         - isccp_cldtot
output_control:
   frequency: 1
   frequency_units: nmonths
restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
# daily mean output - remapped to ne30pg2
def get_hist_opts_1da_ne30(opts):
   return f'''
filename_prefix: output.1da_ne30pg2
averaging_type: average
max_snapshots_per_file: 30
horiz_remap_file: {DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc
iotype: pnetcdf
fields:
   physics_pg2:
      field_names:
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
         - SW_flux_up_at_model_top := SW_flux_up.isel(lev=0)
         - SW_flux_dn_at_model_top := SW_flux_dn.isel(lev=0)
         - LW_flux_up_at_model_top := LW_flux_up.isel(lev=0)
         - U_at_850hPa := U.interp(p_mid=850,units='hPa')
         - U_at_200hPa := U.interp(p_mid=200,units='hPa')
output_control:
   frequency: 1
   frequency_units: ndays
restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
# hourly instantaneous output - native grid
def get_hist_opts_1hi(opts):
   return f'''
filename_prefix: output.1hi
averaging_type: instant
max_snapshots_per_file: 240
iotype: pnetcdf
fields:
   physics_pg2:
      field_names:
         - LW_flux_up_at_model_top := LW_flux_up.isel(lev=0)
         - precip_total_surf_mass_flux
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
# 3-hourly instantaneous output - native grid
def get_hist_opts_3hi(opts):
   return f'''
filename_prefix: output.3hi
averaging_type: instant
max_snapshots_per_file: 80
iotype: pnetcdf
fields:
   physics_pg2:
      field_names:
         - SeaLevelPressure
         - wind_speed_10m
         - z_mid_at_500hPa := z_mid.interp(p_mid=500,units='hPa')
         - z_mid_at_200hPa := z_mid.interp(p_mid=200,units='hPa')
         - wind_speed_at_100m_above_surface := wind_speed.interp(z_mid=100,reference='surface')
         - ZonalVapFlux
         - MeridionalVapFlux
         - omega_at_500hPa := omega.interp(p_mid=500,units='hPa')
         - omega_at_850hPa := omega.interp(p_mid=850,units='hPa')
         - surf_sens_flux
         - surf_evap
         - surface_upward_latent_heat_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - SW_flux_up_at_model_top := SW_flux_up.isel(lev=0)
         - SW_flux_dn_at_model_top := SW_flux_dn.isel(lev=0)
         - LW_flux_up_at_model_top := LW_flux_up.isel(lev=0)
         - SW_clrsky_flux_up_at_model_top := SW_clrsky_flux_up.isel(lev=0)
         - SW_clrsky_flux_dn_at_model_top := SW_clrsky_flux_dn.isel(lev=0)
         - LW_clrsky_flux_up_at_model_top := LW_clrsky_flux_up.isel(lev=0)
         - LiqWaterPath
         - LiqNumberPath
         - IceWaterPath
output_control:
   frequency: 3
   frequency_units: nhours
restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
