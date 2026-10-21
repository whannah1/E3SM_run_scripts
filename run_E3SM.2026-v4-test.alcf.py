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
# https://docs.alcf.anl.gov/aurora/running-jobs-aurora/#queues
#---------------------------------------------------------------------------------------------------
'''NOTES
E3SMv4 prototype ZM tuning runs on Aurora - multi-year runs to look at MJO/QBO sensitivity
baseline config follows v4_dev_scripts/run.test.ne256.20260909.ZM.splitform.newL128.Recipe2_updated.GWD.sh

src_dir = E3SM_SRC0 => master @ Oct 9 (34d78535b7)

nohup python -u run_E3SM.2026-v4-test.alcf.py > run_E3SM.2026-v4-test.alcf.py.out &

JOB BUNDLING
------------
Why not the built-in multi-instance (NINST_ATM) capability?
  - EAMxx restart files are named {CASE}.scream.r.* and the pointer file is hardcoded
    to "rpointer.atm" (no instance suffix), so instances clobber each other's restarts
    => multi-year runs with resubmissions are not possible without code changes
  - all instances share one case "clock", so a new batch can't be started next to
    an existing batch that has already done several submissions

Instead, each tuning run is a normal standalone case (all sharing one executable) and a
small "bundle driver" runs one segment of every active case side-by-side in one PBS job,
with each case's mpiexec restricted to its own subset of nodes. After all segments finish
the driver decrements RESUBMIT for each case and resubmits itself if any case is still active.

  bundle_dir/bundle.job     driver (python) - also the PBS job script
  bundle_dir/bundle.json    queue / walltime / node limits (re-read at every resubmission)
  bundle_dir/members.txt    case roots in the bundle (cases are packed onto nodes in this order)
  bundle_dir/status/<case>  active / running / done / failed / hold
  bundle_dir/logs/          driver log and per-case segment logs for each job

To add a new batch at any time: add new add_case() lines, comment out the old ones,
and re-run this script with newcase/config/build/set_run_opts/submit = True.
The new cases are marked active and get picked up by the next bundle job, while the
older cases keep going from their restarts (CONTINUE_RUN is tracked per case).
If no bundle job is queued/running a new one is submitted.

To extend a case that is "done": re-run with only submit + continue_run = True (and a new resub)

  python3 <bundle_dir>/bundle.job --status   => quick status table
  python3 <bundle_dir>/bundle.job --submit   => manually (re)start the bundle

A case can still be submitted normally (use_bundle=False) - the hostfile mpiexec arg
added to env_mach_specific.xml is empty unless the bundle driver sets BUNDLE_HOSTFILE.

Notes
- all cases in a bundle should use a STOP_N that fits in bundle_walltime, otherwise PBS kills
  every member at once (stale "running" status is reset to "active" by the next bundle job)
- members can use different node counts and grids, but node packing is "first come first served"
- don't rebuild the shared .EXE case while a bundle is running - bump build_tag instead
'''
#---------------------------------------------------------------------------------------------------
import os, sys, json, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'E3SM_Dec'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC0' # branch => master @ Oct 9 (34d78535b7)
scratch_root = '/lus/flare/projects/E3SM_Dec/whannah/scratch'
din_loc_root = '/lus/flare/projects/E3SMinput/data'

# cases with the same build_tag/grid/num_nodes/debug share an executable
# => bump this whenever src_dir changes (i.e. after merging in PR branches)
build_tag = 'v4-SRC0-20261009'

# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True

#---------------------------------------------------------------------------------------------------
# job bundling settings

use_bundle = True

# bundle_name = '2026-v4-ZM-TUNE-00'
# bundle_queue,bundle_walltime,bundle_min_nodes,bundle_max_nodes = 'prod','12:00:00',256,512

# ne30 test of the bundling mechanics in the debug-scaling queue (3-255 nodes, 1 hour)
bundle_name = '2026-v4-BUNDLE-TEST-00'
bundle_queue,bundle_walltime,bundle_min_nodes,bundle_max_nodes = 'debug-scaling','1:00:00',3,16

#---------------------------------------------------------------------------------------------------
# queue/walltime are only used when use_bundle=False

# stop_opt,stop_n,resub,walltime,queue = 'ndays',5,0,'1:00:00','debug-scaling'
stop_opt,stop_n,resub = 'ndays',5,2 # bundle test
# stop_opt,stop_n,resub = 'nmonths',3,4*5-1 # 5-yr ne256 - check throughput before trusting this!

#---------------------------------------------------------------------------------------------------
kwargs_ne256 = ({'num_nodes':64,'grid':'ne256pg2_ne256pg2'})
kwargs_ne30  = ({'num_nodes':4, 'grid':'ne30pg2_ne30pg2'})

### test of bundling mechanics
kwargs_common = {'prefix':'2026-v4-BUNDLE-TEST-00','compset':'F2010xx-ZM-CICE','arch':'GPU'}
add_case(**kwargs_common, **kwargs_ne30) # control
add_case(**kwargs_common, **kwargs_ne30, tau=7200)
# add_case(**kwargs_common, **kwargs_ne30, dmpdz=-1.0e-3) # 2nd batch - add after 1st batch has run a segment
# add_case(**kwargs_common, **kwargs_ne30, alfa=0.2)

### ZM tuning - batch 1
# kwargs_common = {'prefix':'2026-v4-ZM-TUNE-00','compset':'F2010xx-ZM-CICE','arch':'GPU'}
# add_case(**kwargs_common, **kwargs_ne256) # control - v4 prototype
# add_case(**kwargs_common, **kwargs_ne256, tau=7200)
# add_case(**kwargs_common, **kwargs_ne256, dmpdz=-1.0e-3)
# add_case(**kwargs_common, **kwargs_ne256, alfa=0.2)

#---------------------------------------------------------------------------------------------------
# short option names for ZM parameters => zm::<param>
zm_param_map = {}
zm_param_map['tau']   = 'tau'               # convective adjustment time scale [s]       (default 3600)
zm_param_map['dmpdz'] = 'dmpdz'             # fractional mass entrainment rate [1/m]     (default -0.7e-3)
zm_param_map['alfa']  = 'alfa'              # max downdraft mass flux fraction           (default 0.14)
zm_param_map['ke']    = 'ke'                # evaporation efficiency                     (default 2.5e-6)
zm_param_map['c0l']   = 'c0_lnd'            # autoconversion coefficient over land       (default 0.002)
zm_param_map['c0o']   = 'c0_ocn'            # autoconversion coefficient over ocean      (default 0.002)
zm_param_map['tpf']   = 'tpert_fac'         # temperature perturbation factor            (default 2.0)
zm_param_map['tka']   = 'tiedke_add'        # temperature perturbation                   (default 0.8)
zm_param_map['cape']  = 'cape_threshold'    # CAPE threshold [J/kg]                      (default 0)
zm_param_map['dcape'] = 'dcape_threshold'   # DCAPE threshold [J/kg/s]                   (default 0)
zm_param_map['upl']   = 'upper_limit_pref'  # upper pressure limit for convection [Pa]   (default 40e2)
zm_param_map['cda']   = 'clos_dyn_adj'      # dynamic closure adjustment                 (default false)
zm_param_map['mtc']   = 'mcsp_t_coeff'      # MCSP temperature coefficient               (default 0.3)
zm_param_map['mqc']   = 'mcsp_q_coeff'      # MCSP humidity coefficient                  (default 0.0)
zm_param_map['muc']   = 'mcsp_u_coeff'      # MCSP U-wind coefficient                    (default 0.0)
zm_param_map['mvc']   = 'mcsp_v_coeff'      # MCSP V-wind coefficient                    (default 0.0)
#---------------------------------------------------------------------------------------------------
def get_grid_name(opts): return opts['grid'].split('_')[0]
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items():
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['compset']:   continue
      elif key in ['arch']:      continue
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: continue
      elif key in ['num_tasks']: continue
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if opts.get('debug',False): case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   for i in range(1,9+1): case = case.replace(f'e-0{i}',f'e-{i}')
   return case
#---------------------------------------------------------------------------------------------------
def get_exe_case_name(opts):
   exe_case = f'E3SM.{build_tag}.{opts["compset"]}.{get_grid_name(opts)}.NN_{opts["num_nodes"]}'
   if opts.get('debug',False): exe_case += '.debug'
   return f'{exe_case}.EXE'
#---------------------------------------------------------------------------------------------------
def get_init_files(opts):
   grid_name = get_grid_name(opts)
   atm_init_file,lnd_init_file = None,None
   if grid_name=='ne30pg2':
      atm_init_file = f'{din_loc_root}/atm/scream/init/eamxxi_ne30np4L128v4_ERA5-20190101_c20260922.nc'
   if grid_name=='ne256pg2':
      # neither of these files is on Aurora yet - copy from NERSC first
      # (only eamxxi_ne256np4L128v4_ERA5-20121001_c20260922.nc is currently available)
      atm_init_file = f'{din_loc_root}/atm/scream/init/eamxxi_ne256np4L128v4_ERA5-20190101_c20260922.nc'
      lnd_init_file = f'{din_loc_root}/lnd/clm2/initdata/20240305.I2010CRUELM.ne256pg2.elm.r.2020-01-20-00000.nc'
   if atm_init_file is None: raise ValueError(f'no atm initial condition file set for grid: {grid_name}')
   return atm_init_file,lnd_init_file
#---------------------------------------------------------------------------------------------------
def get_pe_opts(opts):
   arch = opts.get('arch','CPU')
   if arch=='GPU': compiler,max_mpi_per_node = 'intelgpu', 12
   if arch=='CPU': compiler,max_mpi_per_node = 'intel',   102
   atm_ntasks = max_mpi_per_node*opts['num_nodes']
   return compiler,atm_ntasks
#---------------------------------------------------------------------------------------------------
def create_newcase(case,case_root,opts):
   compiler,atm_ntasks = get_pe_opts(opts)
   cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
   cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
   cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
   cmd += f' --pecount {atm_ntasks}x1 --machine aurora --compiler {compiler} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
exe_built_list = []
def build_exe(opts):
   '''
   create and build a separate case that only provides the executable for all
   cases with the same build_tag/compset/grid/num_nodes/debug
   '''
   exe_case = get_exe_case_name(opts)
   exe_root = f'{scratch_root}/{exe_case}'
   if exe_root in exe_built_list: return exe_root # only build once per invocation, even with clean=True
   exe_built_list.append(exe_root)
   if os.path.isfile(f'{exe_root}/bld/e3sm.exe') and not clean:
      print(f'\n  using existing executable: {exe_root}/bld/e3sm.exe\n')
      return exe_root
   print(f'\n  building shared executable: {exe_root}\n')
   if not os.path.isdir(exe_root): create_newcase(exe_case,exe_root,opts)
   cwd = os.getcwd()
   os.chdir(f'{exe_root}/case_scripts')
   run_cmd(f'./xmlchange EXEROOT={exe_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={exe_root}/run ')
   run_cmd(f'./xmlchange EAMXX_VGRID=L128v4')
   if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   run_cmd('./case.setup --reset')
   if clean : run_cmd('./case.build --clean-all')
   run_cmd('./case.build')
   os.chdir(cwd)
   if not os.path.isfile(f'{exe_root}/bld/e3sm.exe'):
      exit(f'\n{clr.RED}build failed for shared executable: {exe_root}{clr.END}\n')
   return exe_root
#---------------------------------------------------------------------------------------------------
def add_bundle_hostfile_arg():
   '''
   add an mpiexec argument to restrict the case to a subset of nodes when run by the
   bundle driver. BUNDLE_HOSTFILE is only set by the driver, so for a normal case.submit
   this evaluates to an empty string and has no effect.
   '''
   emsx = 'env_mach_specific.xml'
   with open(emsx) as f: txt = f.read()
   if 'bundle_hostfile' in txt: return
   if txt.count('</arguments>')!=1: exit(f'\n{clr.RED}unexpected mpirun block in {emsx} - cannot add hostfile arg{clr.END}\n')
   arg = '<arg name="bundle_hostfile">$SHELL{if [ -n "$BUNDLE_HOSTFILE" ]; then echo "--hostfile $BUNDLE_HOSTFILE"; fi}</arg>'
   txt = txt.replace('</arguments>',f'  {arg}\n      </arguments>')
   with open(emsx,'w') as f: f.write(txt)
   print(f'\n  added bundle_hostfile mpiexec arg to {emsx}')
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
   print(f' set_run_opts : {set_run_opts}')
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   print(f' use_bundle   : {use_bundle}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' not in opts: raise ValueError('you must specify num_nodes!')
   #------------------------------------------------------------------------------------------------
   case_root = f'{scratch_root}/{case}'
   exe_root  = f'{scratch_root}/{get_exe_case_name(opts)}'
   atm_init_file,lnd_init_file = get_init_files(opts)
   if newcase or set_run_opts:
      for f in [atm_init_file,lnd_init_file]:
         if f is not None and not os.path.isfile(f): exit(f'\n{clr.RED}missing initial condition file: {f}{clr.END}\n')
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      create_newcase(case,case_root,opts)
      # Copy this run script into the case directory
      timestamp = datetime.datetime.now().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'cp {os.path.realpath(__file__)} {case_root}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={exe_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd(f'./xmlchange EAMXX_VGRID=L128v4')
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      run_cmd(f'./xmlchange DOUT_S=FALSE')
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      run_cmd('./case.setup --reset')
      add_bundle_hostfile_arg()
   #------------------------------------------------------------------------------------------------
   if build :
      build_exe(opts)
      run_cmd('./xmlchange BUILD_COMPLETE=TRUE ')
   #------------------------------------------------------------------------------------------------
   if set_run_opts:
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      run_cmd(f'./xmlchange RUN_STARTDATE=2010-01-01')
      #-------------------------------------------------------------------------
      # v4 prototype settings
      run_cmd(f'./atmchange -b physics::atm_procs_list="zm,mac_aero_mic,gw,rrtmgp,cosp"')
      run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list="shoc,cld_fraction,spa,p3"')
      run_cmd(f'./atmchange -b physics::cosp::cosp_frequency_units="hours"')
      run_cmd(f'./atmchange -b physics::cosp::cosp_frequency=1')
      # GHG levels more appropriate for sim - average from 19940101 - 20150101
      run_cmd(f'./atmchange -b co2vmr=377.2e-6')
      run_cmd(f'./atmchange -b ch4vmr=1786.6e-9')
      run_cmd(f'./atmchange -b n2ovmr=318.6e-9')
      run_cmd(f'./atmchange -b orbital_year=-9999')
      run_cmd(f'./xmlchange CCSM_CO2_PPMV=377.2') # use same CO2 in land model
      # sponge layer
      run_cmd(f'./atmchange -b tom_sponge_start=15')
      run_cmd(f'./atmchange -b laplace_scaling=1')
      run_cmd(f'./atmchange -b nu_top=5e-7')
      # split form
      run_cmd(f'./atmchange -b theta_advect_form=2')
      run_cmd(f'./atmchange -b pgrad_correction=0')
      # aerosol / cloud tuning
      run_cmd(f'./atmchange -b spa_data_file="{din_loc_root}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      run_cmd(f'./atmchange -b spa_ccn_to_nc_factor=750.0')
      run_cmd(f'./atmchange -b length_fac=0.51')
      run_cmd(f'./atmchange -b autoconversion_prefactor=2960.0')
      run_cmd(f'./atmchange -b autoconversion_qc_exponent=2.42')
      # gravity waves
      run_cmd(f'./atmchange -b use_gw_orographic=true')
      run_cmd(f'./atmchange -b use_gw_convect=true')
      run_cmd(f'./atmchange -b gw_convect_hcf=10')
      # initial conditions
      run_cmd(f'./atmchange -b vertical_coordinate_filename="{din_loc_root}/atm/scream/init/vertical_coordinates_L128v4_c20260820.nc"')
      run_cmd(f'./atmchange -b initial_conditions::filename="{atm_init_file}"')
      #-------------------------------------------------------------------------
      # ZM tuning parameters
      for key,param in zm_param_map.items():
         if opts.get(key) is not None:
            val = opts[key]
            if isinstance(val,bool): val = 'true' if val else 'false'
            run_cmd(f'./atmchange -b zm::{param}={val}')
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
      #-------------------------------------------------------------------------
      # land / sea ice / coupler settings
      elm_nl = ''
      if lnd_init_file is not None: elm_nl += f" finidat='{lnd_init_file}'\n"
      elm_nl += " hist_dov2xy = .true.,.true.\n"
      elm_nl += " hist_mfilt = 1,1\n"
      elm_nl += " hist_nhtfrq = 0,-24\n"
      elm_nl += " hist_avgflag_pertape = 'A','A'\n"
      elm_nl += " hist_fincl1 = 'FIRE','FPSN','QDRAI','QRUNOFF','ZWT','FSAT','H2OSOI','EFLX_LH_TOT',\n"
      elm_nl += "               'QVEGT','QVEGE','FSH','ALBD','ALBI','TBOT','QBOT','RAIN','SNOW',\n"
      elm_nl += "               'FSDS','FSDSND','FSDSNI','FSDSVD','FSDSVI','FLDS'\n"
      elm_nl += " hist_fincl2 = 'H2OSNO','SOILWATER_10CM','TG'\n"
      with open('user_nl_elm','w') as f: f.write(elm_nl)
      # disable CICE output
      with open('user_nl_cice','w') as f: f.write(" histfreq = 'x','x','x','x','x'\n histfreq_n = 0,0,0,0,0\n")
      run_cmd(f'./xmlchange HIST_OPTION=never,HIST_N=1')
      run_cmd(f'./xmlchange BUDGETS=TRUE')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if use_bundle and get_bundle_status(case)=='running' and bundle_job_is_active():
         print(f'\n{clr.RED}WARNING - case is currently running in bundle {bundle_name} - skipping submit{clr.END}\n')
         return
      #-------------------------------------------------------------------------
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      add_bundle_hostfile_arg()
      #-------------------------------------------------------------------------
      if use_bundle:
         # case.submit normally does these checks - the bundle driver calls .case.run directly
         run_cmd('./preview_namelists')
         run_cmd('./check_input_data --download')
         add_bundle_member(case,case_root)
      else:
         if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
         if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
         run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
def get_remap_line(opts):
   if get_grid_name(opts)=='ne256pg2':
      return f'horiz_remap_file: {din_loc_root}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc'
   return ''
#---------------------------------------------------------------------------------------------------
# daily mean output - remapped to ne30pg2 for MJO / QBO analysis
def get_hist_opts_1da(opts):
   return f'''
filename_prefix: output.1da
averaging_type: average
max_snapshots_per_file: 30
iotype: pnetcdf
{get_remap_line(opts)}
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - zm_prec
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - T_2m
         - wind_speed_10m
         - surf_evap
         - surf_sens_flux
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
         - U_at_850hPa
         - V_at_850hPa
         - U_at_200hPa
         - V_at_200hPa
         - omega_at_500hPa
         - U_at_100hPa
         - U_at_50hPa
         - U_at_30hPa
         - U_at_20hPa
         - U_at_10hPa
         - T_mid_at_100hPa
         - T_mid_at_50hPa
         - T_mid_at_10hPa
output_control:
   frequency: 1
   frequency_units: ndays
restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
# monthly mean output - remapped to ne30pg2
def get_hist_opts_1ma(opts):
   return f'''
filename_prefix: output.1ma
averaging_type: average
max_snapshots_per_file: 1
iotype: pnetcdf
{get_remap_line(opts)}
fields:
   physics_pg2:
      field_names:
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
         - zm_T_mid_tend
         - zm_qv_tend
         # 2D fields
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
         - surf_mom_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - landfrac
         - ocnfrac
         - wind_speed_10m
         # ZM diagnostics
         - zm_prec
         - zm_activity
         - zm_cape
         - zm_depth
         - mcsp_freq
         # cosp
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
# job bundling utilities
#---------------------------------------------------------------------------------------------------
def get_bundle_dir(): return f'{scratch_root}/bundles/{bundle_name}'
#---------------------------------------------------------------------------------------------------
def get_bundle_status(case):
   status_file = f'{get_bundle_dir()}/status/{case}'
   if not os.path.isfile(status_file): return None
   with open(status_file) as f: return f.read().strip()
#---------------------------------------------------------------------------------------------------
def bundle_job_is_active():
   jobid_file = f'{get_bundle_dir()}/jobid'
   if not os.path.isfile(jobid_file): return False
   with open(jobid_file) as f: jobid = f.read().strip()
   return sp.call(['qstat',jobid],stdout=sp.DEVNULL,stderr=sp.DEVNULL)==0
#---------------------------------------------------------------------------------------------------
def write_bundle_files():
   bundle_dir = get_bundle_dir()
   for d in ['status','logs','hostfiles']: os.makedirs(f'{bundle_dir}/{d}',exist_ok=True)
   cfg = {'name':bundle_name, 'acct':acct, 'queue':bundle_queue, 'walltime':bundle_walltime,
          'min_nodes':bundle_min_nodes, 'max_nodes':bundle_max_nodes, 'qsub':'qsub'}
   with open(f'{bundle_dir}/bundle.json','w') as f: json.dump(cfg,f,indent=3)
   # the PBS server spools a copy of the job script, so overwriting this during a job is safe
   driver = bundle_driver_template.replace('@@BUNDLE_DIR@@',bundle_dir)
   driver = driver.replace('@@RUN_SCRIPT@@',os.path.realpath(__file__))
   with open(f'{bundle_dir}/bundle.job','w') as f: f.write(driver)
   os.chmod(f'{bundle_dir}/bundle.job',0o755)
#---------------------------------------------------------------------------------------------------
def add_bundle_member(case,case_root):
   write_bundle_files()
   bundle_dir = get_bundle_dir()
   members_file = f'{bundle_dir}/members.txt'
   members = []
   if os.path.isfile(members_file):
      with open(members_file) as f: members = [l.strip() for l in f if l.strip()!='']
   if case_root not in members:
      with open(members_file,'a') as f: f.write(case_root+'\n')
   with open(f'{bundle_dir}/status/{case}','w') as f: f.write('active\n')
   print(f'\n  {clr.CYAN}added to bundle {bundle_name} as active member{clr.END}')
#---------------------------------------------------------------------------------------------------
bundle_driver_template = r'''#!/usr/bin/env python3
#PBS -l filesystems=home:flare
#PBS -j oe
#PBS -o @@BUNDLE_DIR@@/logs/pbs.out
#-------------------------------------------------------------------------------
# E3SM job bundle driver - generated by:
#   @@RUN_SCRIPT@@
# account/queue/walltime/select are set on the qsub command line from bundle.json
#
#   python3 bundle.job --status   => print status of bundle members
#   python3 bundle.job --submit   => submit a bundle job unless one is already queued/running
#   (no arguments)                => inside the PBS job: run one segment of each active member
#
# member status (status/<case>) - can be edited by hand:
#   active  => will run a segment in the next bundle job
#   running => currently running a segment
#   done    => RESUBMIT exhausted
#   failed  => last segment failed - fix the case and set back to "active"
#   hold    => skipped until set back to "active"
#
# NOTE: keep this compatible with the system python3 (3.6) on the compute nodes
#-------------------------------------------------------------------------------
import os, sys, re, json, glob, time, subprocess as sp
bundle_dir = '@@BUNDLE_DIR@@'
job_script = os.path.join(bundle_dir,'bundle.job')
jobid_file = os.path.join(bundle_dir,'jobid')
this_jobid = os.getenv('PBS_JOBID','')
logfile = None
#-------------------------------------------------------------------------------
def log(msg):
   line = '{}  {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'),msg)
   print(line,flush=True)
   if logfile is not None: logfile.write(line+'\n'); logfile.flush()
def read_file(path,default=''):
   try:
      with open(path) as f: return f.read().strip()
   except IOError:
      return default
def write_file(path,txt):
   with open(path+'.tmp','w') as f: f.write(txt+'\n')
   os.replace(path+'.tmp',path)
def load_cfg():
   with open(os.path.join(bundle_dir,'bundle.json')) as f: return json.load(f)
def case_name(root): return os.path.basename(root.rstrip('/'))
def get_members():
   members = []
   for line in read_file(os.path.join(bundle_dir,'members.txt')).split('\n'):
      line = line.strip()
      if line!='' and line not in members: members.append(line)
   return members
def get_status(root): return read_file(os.path.join(bundle_dir,'status',case_name(root)),'unknown')
def set_status(root,status): write_file(os.path.join(bundle_dir,'status',case_name(root)),status)
def xmlquery(root,var):
   cmd = ['./xmlquery','--value',var]
   return sp.check_output(cmd,cwd=os.path.join(root,'case_scripts'),universal_newlines=True).strip()
def xmlchange(root,setting):
   sp.check_call(['./xmlchange',setting],cwd=os.path.join(root,'case_scripts'),stdout=sp.DEVNULL)
def model_date(root):
   for rp in sorted(glob.glob(os.path.join(root,'run','rpointer.drv*'))):
      m = re.search(r'\.r\.(\d+-\d+-\d+)-\d+\.nc',read_file(rp))
      if m: return m.group(1)
   return '-'
def same_job(a,b): return a.split('.')[0]==b.split('.')[0]
def job_is_active(jobid):
   if jobid=='': return False
   return sp.call(['qstat',jobid],stdout=sp.DEVNULL,stderr=sp.DEVNULL)==0
#-------------------------------------------------------------------------------
def print_status():
   cfg = load_cfg()
   jobid = read_file(jobid_file)
   state = 'queued/running' if job_is_active(jobid) else 'not active'
   print('\n  bundle: {}  queue: {}  walltime: {}  nodes: {}-{}'.format(
         cfg['name'],cfg['queue'],cfg['walltime'],cfg['min_nodes'],cfg['max_nodes']))
   print('  last job: {} ({})\n'.format(jobid if jobid else '-',state))
   fmt = '  {:<8} {:>5} {:>8} {:>8} {:>11}  {}'
   print(fmt.format('status','nodes','resub','continue','model date','case'))
   for root in get_members():
      try:
         nn,rs,cr = [xmlquery(root,v) for v in ['NUM_NODES','RESUBMIT','CONTINUE_RUN']]
      except Exception:
         nn,rs,cr = '?','?','?'
      print(fmt.format(get_status(root),nn,rs,cr,model_date(root),case_name(root)))
   print()
#-------------------------------------------------------------------------------
def submit():
   cfg = load_cfg()
   jobid = read_file(jobid_file)
   if job_is_active(jobid) and not same_job(jobid,this_jobid):
      log('bundle job {} is already queued/running - new members will be picked up by the next job'.format(jobid))
      return
   active,need = [],0
   for root in get_members():
      if get_status(root) not in ['active','running']: continue
      nn = int(xmlquery(root,'NUM_NODES'))
      if nn > cfg['max_nodes']:
         log('WARNING: {} needs {} nodes > max_nodes={} - ignoring it'.format(case_name(root),nn,cfg['max_nodes']))
         continue
      active.append(root)
      need += nn
   if len(active)==0:
      log('no active members - not submitting a new bundle job')
      return
   select = max(cfg['min_nodes'],min(cfg['max_nodes'],need))
   cmd = [cfg['qsub'],'-A',cfg['acct'],'-q',cfg['queue'],'-N','bundle.'+cfg['name'],
          '-l','walltime={}'.format(cfg['walltime']),'-l','select={}'.format(select),job_script]
   log('submitting: '+' '.join(cmd))
   out = sp.check_output(cmd,cwd=bundle_dir,universal_newlines=True).strip()
   m = re.search(r'\d+\.\S+',out)
   new_jobid = m.group(0) if m else out
   write_file(jobid_file,new_jobid)
   log('submitted bundle job {} ({} active members, {} nodes)'.format(new_jobid,len(active),select))
#-------------------------------------------------------------------------------
def run_bundle():
   global logfile
   jid = this_jobid.split('.')[0]
   logfile = open(os.path.join(bundle_dir,'logs','bundle.{}.log'.format(jid)),'a')
   # only one bundle job runs at a time, so any "running" members are left over from a job that was killed
   for root in get_members():
      if get_status(root)=='running':
         log('resetting stale "running" status to "active": {}'.format(case_name(root)))
         set_status(root,'active')
   # node list - remove duplicates but preserve order
   nodes = []
   with open(os.environ['PBS_NODEFILE']) as f:
      for line in f:
         if line.strip()!='' and line.strip() not in nodes: nodes.append(line.strip())
   log('bundle job {} started with {} nodes'.format(this_jobid,len(nodes)))
   # launch a segment for each active member that fits on the remaining nodes
   launched = []
   for root in get_members():
      if get_status(root)!='active': continue
      case = case_name(root)
      try:
         nn = int(xmlquery(root,'NUM_NODES'))
      except Exception as e:
         log('ERROR: xmlquery failed for {} - marking as failed: {}'.format(case,e))
         set_status(root,'failed')
         continue
      if nn > len(nodes):
         log('not enough nodes for {} (needs {}, {} free) - waiting for next job'.format(case,nn,len(nodes)))
         continue
      hosts,nodes = nodes[:nn],nodes[nn:]
      hostfile = os.path.join(bundle_dir,'hostfiles','{}.{}'.format(case,jid))
      write_file(hostfile,'\n'.join(hosts))
      env = dict(os.environ)
      env['BUNDLE_HOSTFILE'] = hostfile
      env.pop('ARGS_FOR_SCRIPT',None)
      out = open(os.path.join(bundle_dir,'logs','{}.{}.log'.format(case,jid)),'w')
      cmd = ['./.case.run','--completion-sets-continue-run']
      proc = sp.Popen(cmd,cwd=os.path.join(root,'case_scripts'),env=env,stdout=out,stderr=sp.STDOUT)
      set_status(root,'running')
      log('launched {} on {} nodes (start date: {})'.format(case,nn,model_date(root)))
      launched.append((root,proc,out))
   if len(nodes)>0: log('{} nodes left idle'.format(len(nodes)))
   # wait for all segments and update the member status
   for root,proc,out in launched:
      rc = proc.wait()
      out.close()
      case = case_name(root)
      if rc!=0:
         set_status(root,'failed')
         log('FAILED: {} (exit code {}) - see logs/{}.{}.log'.format(case,rc,case,jid))
         continue
      resub = int(xmlquery(root,'RESUBMIT'))
      if resub > 0:
         xmlchange(root,'RESUBMIT={}'.format(resub-1))
         set_status(root,'active')
         log('finished segment: {} (model date: {}, RESUBMIT={})'.format(case,model_date(root),resub-1))
      else:
         set_status(root,'done')
         log('finished: {} (model date: {})'.format(case,model_date(root)))
   # avoid an endless chain of empty jobs
   if len(launched)==0:
      log('ERROR: no members were launched - not resubmitting')
   else:
      submit()
   logfile.close()
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   if '--status' in sys.argv:
      print_status()
   elif '--submit' in sys.argv:
      submit()
   else:
      if this_jobid=='': sys.exit('ERROR: bundle.job should only be run without arguments inside a PBS job')
      run_bundle()
'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
   if use_bundle and submit:
      write_bundle_files()
      run_cmd(f'python3 {get_bundle_dir()}/bundle.job --submit')
   if use_bundle and os.path.isfile(f'{get_bundle_dir()}/bundle.job'):
      run_cmd(f'python3 {get_bundle_dir()}/bundle.job --status')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
