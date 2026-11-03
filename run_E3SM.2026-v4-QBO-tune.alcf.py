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
  bundle_dir/cases/<case>/  case directories - every case here with a bundle_status file is a member
     bundle_status          active / running / done / failed / hold
     bundle_order           time the case was added (cases are packed onto nodes in this order)
  bundle_dir/logs/          driver log and per-case segment logs for each job
  bundle_dir/hostfiles/     node list for each case and job

Since all cases live inside the bundle, a case is removed by deleting its directory and the
whole bundle can be started over by deleting bundle_dir (cancel the bundle job first).
The shared executable cases (*.EXE) stay in scratch_root, so this doesn't require a rebuild.
Cases with use_bundle=False are created in scratch_root as usual.

To add a new batch at any time: add new add_case() lines, comment out the old ones,
and re-run this script with newcase/config/build/set_run_opts/submit = True.
The new cases are marked active and get picked up by the next bundle job, while the
older cases keep going from their restarts (CONTINUE_RUN is tracked per case).
If no bundle job is queued/running a new one is submitted.

To extend a case that is "done": re-run with only submit + continue_run = True (and a new resub)

  python3 <bundle_dir>/bundle.job --status              => quick status table
  python3 <bundle_dir>/bundle.job --submit              => manually (re)start the bundle
  python3 <bundle_dir>/bundle.job --hold     <pattern>  => skip matching cases until re-activated
  python3 <bundle_dir>/bundle.job --activate <pattern>  => (re)activate matching cases
  python3 <bundle_dir>/bundle.job --remove   <pattern>  => delete matching case directories
  python3 <bundle_dir>/bundle.job --purge               => cancel the bundle job and delete the bundle
  (<pattern> is a shell-style wildcard matched against the case name, e.g. "*.cape_*")

A case can still be submitted normally (use_bundle=False) - the hostfile mpiexec arg
added to env_mach_specific.xml is empty unless the bundle driver sets BUNDLE_HOSTFILE.

Notes
- all cases in a bundle should use a STOP_N that fits in bundle_walltime - if the walltime is hit
  the unfinished members are reset to "active" and the bundle is resubmitted, but only if at least
  one segment finished (to avoid an endless chain of jobs that all hit the walltime)
- members can use different node counts and grids, but node packing is "first come first served"
- don't rebuild the shared .EXE case while a bundle is running - bump exe_prefix instead
'''
#---------------------------------------------------------------------------------------------------
import os, sys, json, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'E3SM_Dec'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC0' # branch => master @ Nov 2 + whannah/eamxx/add-rayleigh-friction
scratch_root = '/lus/flare/projects/E3SM_Dec/whannah/scratch'
din_loc_root = '/lus/flare/projects/E3SMinput/data'

# cases with the same exe_prefix/grid/num_nodes/debug share an executable
# => bump this whenever src_dir changes (i.e. after merging in PR branches)


# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True

#---------------------------------------------------------------------------------------------------
# job bundling settings - NOTE: queue/walltime are only used when use_bundle=False

use_bundle = True

grid = 'ne256' # ne30 / ne256

bundle_name = f'E3SM.2026-v4-QBO-TUNE-00.{grid}'

#---------------------------------------------------------------------------------------------------
kwargs_common = {'prefix':bundle_name,'compset':'F2010xx-ZM-CICE','arch':'GPU'}
if grid=='ne30':
   kwargs_grid = ({'num_nodes':8, 'grid':'ne30pg2_ne30pg2'})
   bundle_min_nodes,bundle_max_nodes = 2,256
   bundle_queue,stop_opt,stop_n,resub,bundle_walltime = 'prod','nmonths',1,0,'2:00:00' # initial timing test
   # bundle_queue,stop_opt,stop_n,resub,bundle_walltime = 'prod','nmonths',3,4*5-1,'???:00:00'  # 5-yr
if grid=='ne256':
   kwargs_grid = ({'num_nodes':128,'grid':'ne256pg2_ne256pg2'})
   bundle_min_nodes,bundle_max_nodes = 256,4096
   bundle_queue,stop_opt,stop_n,resub,bundle_walltime = 'prod','nmonths',1,0,'2:00:00' # initial timing test
   # bundle_queue,stop_opt,stop_n,resub,bundle_walltime = 'prod','nmonths',3,4*5-1,'1:00:00'  # 5-yr

add_case(**kwargs_common, **kwargs_grid, member='000', EF=0.35, CF=10, HD=0.50, HM=2.5)
add_case(**kwargs_common, **kwargs_grid, member='001', EF=0.15, CF=18, HD=0.45, HM=2.5)
add_case(**kwargs_common, **kwargs_grid, member='002', EF=0.16, CF=19, HD=0.35, HM=2.4)
add_case(**kwargs_common, **kwargs_grid, member='003', EF=0.30, CF=14, HD=0.90, HM=4.2)
add_case(**kwargs_common, **kwargs_grid, member='004', EF=0.24, CF=15, HD=0.72, HM=4.3)
add_case(**kwargs_common, **kwargs_grid, member='005', EF=0.10, CF=20, HD=0.60, HM=1.9)
add_case(**kwargs_common, **kwargs_grid, member='006', EF=0.56, CF=15, HD=0.38, HM=3.5)
add_case(**kwargs_common, **kwargs_grid, member='007', EF=0.08, CF=20, HD=0.80, HM=1.7)

# add_case(**kwargs_common, **kwargs_grid, member='008', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='009', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='010', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='011', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='012', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='013', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='014', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='015', EF=0.35, CF=10, HD=0.50, HM=2.5)

# add_case(**kwargs_common, **kwargs_grid, member='016', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='017', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='018', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='019', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='020', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='021', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='022', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='023', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='024', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='025', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='026', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='027', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='028', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='029', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='030', EF=0.35, CF=10, HD=0.50, HM=2.5)
# add_case(**kwargs_common, **kwargs_grid, member='031', EF=0.35, CF=10, HD=0.50, HM=2.5)

exe_prefix = bundle_name


# # good cases identified by Luis
# add_case(**kwargs,member='039',EF= 0.142968750000000, CF=17.556641964889899, HD= 0.445792085645316, HM= 2.493509896390510, PS=863.150577718101999, FT=20.833472850226599, FE= 0.110156250000000, OB= 0.000242893932735, OE= 0.230468750000000)
# add_case(**kwargs,member='009',EF= 0.164843750000000, CF=19.193538680590699, HD= 0.352532554817429, HM= 2.411288756633150, PS=817.813700810827982, FT=49.403949714643403, FE= 0.317968750000000, OB= 0.006339913511725, OE= 0.689843750000000)
# add_case(**kwargs,member='051',EF= 0.296093750000000, CF=13.708507471031799, HD= 0.901429425850955, HM= 4.192954600844350, PS=796.870914683721026, FT=14.193679823793801, FE= 0.132031250000000, OB= 0.005490138914342, OE= 0.536718750000000)
# add_case(**kwargs,member='005',EF= 0.241406250000000, CF=14.933664082088701, HD= 0.712850740772644, HM= 4.263841945628070, PS=645.068240509100974, FT=14.891153405782500, FE= 0.667968750000000, OB= 0.005759922853514, OE= 0.383593750000000)
# add_case(**kwargs,member='091',EF= 0.099218750000000, CF=20.579969782533698, HD= 0.602822189158288, HM= 1.939085831333460, PS=680.281772274135960, FT=11.715522730913600, FE= 0.416406250000000, OB= 0.000732121790783, OE= 0.077343750000000)
# add_case(**kwargs,member='069',EF= 0.558593750000000, CF=14.764867154273100, HD= 0.376984052351372, HM= 3.486822558994610, PS=531.277381873821014, FT= 6.130722673118020, FE= 0.842968750000000, OB= 0.000411702338030, OE= 0.667968750000000)
# add_case(**kwargs,member='013',EF= 0.077343750000000, CF=21.180185561431401, HD= 0.801613768576933, HM= 1.724370046364960, PS=796.870914683721026, FT=19.857672216242900, FE= 1.083593750000000, OB= 0.000182144753640, OE= 0.919531250000000)


#---------------------------------------------------------------------------------------------------
# short option names for ZM parameters => zm::<param>
gw_param_map = {}
# gw_param_map['ugc'] = 'use_gw_convect'             # default: true
# gw_param_map['ugo'] = 'use_gw_orographic'          # default: true
# gw_param_map['oef'] = 'gw_orographic_eff'          # default: 0.375
# gw_param_map['cef'] = 'gw_convect_eff'             # default: 0.35
# gw_param_map['hcf'] = 'gw_convect_hcf'             # default: 10.0
# gw_param_map['hds'] = 'gw_convect_hdepth_scale'    # default: 0.50
# gw_param_map['hdn'] = 'gw_convect_hdepth_min'      # default: 2.5    [km]
# gw_param_map['ssn'] = 'gw_convect_storm_speed_min' # default: 10.0   [m/s]
# gw_param_map['cps'] = 'gw_convect_plev_src_wind'   # default: 70000  [Pa]

gw_param_map['GC'] = 'use_gw_convect'             # default: true
gw_param_map['GO'] = 'use_gw_orographic'          # default: true
gw_param_map['OE'] = 'gw_orographic_eff'          # default: 0.375
gw_param_map['EF'] = 'gw_convect_eff'             # default: 0.35
gw_param_map['CF'] = 'gw_convect_hcf'             # default: 10.0
gw_param_map['HD'] = 'gw_convect_hdepth_scale'    # default: 0.50
gw_param_map['HM'] = 'gw_convect_hdepth_min'      # default: 2.5    [km]
gw_param_map['SS'] = 'gw_convect_storm_speed_min' # default: 10.0   [m/s]
gw_param_map['PS'] = 'gw_convect_plev_src_wind'   # default: 70000  [Pa]

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts): return opts['grid'].split('_')[0]
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = []
   for key,val in opts.items():
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      continue # case_list.append(get_grid_name(opts))
      elif key in ['compset']:   case_list.append(val)
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
   # exe_case = f'{exe_prefix}.{opts["compset"]}.{get_grid_name(opts)}.NN_{opts["num_nodes"]}'
   exe_case = f'{exe_prefix}.{opts["compset"]}.NN_{opts["num_nodes"]}'
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
   os.makedirs(os.path.dirname(case_root),exist_ok=True)
   cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
   cmd += f' --pecount {atm_ntasks}x1 --machine aurora --compiler {compiler} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
exe_built_list = []
def build_exe(opts):
   '''
   create and build a separate case that only provides the executable for all
   cases with the same exe_prefix/compset/grid/num_nodes/debug
   '''
   exe_case = get_exe_case_name(opts)
   exe_root = f'{scratch_root}/{exe_case}'
   if exe_root in exe_built_list: return exe_root # only build once per invocation, even with clean=True
   exe_built_list.append(exe_root)
   if os.path.isfile(f'{exe_root}/bld/e3sm.exe') and not clean:
      print(f'\n  using existing executable: {exe_root}/bld/e3sm.exe\n')
      return exe_root
   print(f'\n  building shared executable: {exe_root}\n')
   if not os.path.isdir(f'{exe_root}/case_scripts'): create_newcase(exe_case,exe_root,opts)
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
   case_root = get_case_root(case)
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
      # run_cmd(f'./xmlchange RUN_STARTDATE=2010-01-01')
      run_cmd(f'./xmlchange RUN_STARTDATE=0001-01-01')
      #-------------------------------------------------------------------------
      # # v4 prototype settings
      run_cmd(f'./atmchange -b physics::atm_procs_list=rayleigh_friction,zm,gw,mac_aero_mic,rrtmgp')
      # run_cmd(f'./atmchange -b physics::atm_procs_list="zm,mac_aero_mic,gw,rrtmgp,cosp"')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list="shoc,cld_fraction,spa,p3"')
      # # GHG levels more appropriate for sim - average from 19940101 - 20150101
      # run_cmd(f'./atmchange -b co2vmr=377.2e-6')
      # run_cmd(f'./atmchange -b ch4vmr=1786.6e-9')
      # run_cmd(f'./atmchange -b n2ovmr=318.6e-9')
      # run_cmd(f'./atmchange -b orbital_year=-9999')
      # run_cmd(f'./xmlchange CCSM_CO2_PPMV=377.2') # use same CO2 in land model
      # # split form
      # run_cmd(f'./atmchange -b theta_advect_form=2')
      # run_cmd(f'./atmchange -b pgrad_correction=0')
      # # aerosol / cloud tuning
      # run_cmd(f'./atmchange -b spa_data_file="{din_loc_root}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      # run_cmd(f'./atmchange -b spa_ccn_to_nc_factor=750.0')
      # run_cmd(f'./atmchange -b length_fac=0.51')
      # run_cmd(f'./atmchange -b autoconversion_prefactor=2960.0')
      # run_cmd(f'./atmchange -b autoconversion_qc_exponent=2.42')
      # # gravity waves
      # run_cmd(f'./atmchange -b use_gw_orographic=true')
      # run_cmd(f'./atmchange -b use_gw_convect=true')
      # run_cmd(f'./atmchange -b gw_convect_hcf=10')
      #-------------------------------------------------------------------------
      # if opts.get('rfl') is not None: run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_vertical_level={opts.get('rfl')}')
      # if opts.get('rfr') is not None: run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_range={opts.get('rfr')}')
      # if opts.get('rft') is not None: run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_decay_time={opts.get('rft')}')
      # increase Rayleigh friction strength
      run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_vertical_level=6')
      run_cmd(f'./atmchange -b physics::rayleigh_friction::rayleigh_friction_decay_time=2')
      #-------------------------------------------------------------------------
      # # ZM tuning parameters
      # for key,param in zm_param_map.items():
      #    if opts.get(key) is not None:
      #       val = opts[key]
      #       if isinstance(val,bool): val = 'true' if val else 'false'
      #       run_cmd(f'./atmchange -b zm::{param}={val}')
      #-------------------------------------------------------------------------
      # GW tuning parameters
      for key,param in gw_param_map.items():
         if opts.get(key) is not None:
            val = opts[key]
            if isinstance(val,bool): val = 'true' if val else 'false'
            run_cmd(f'./atmchange -b gw::{param}={val}')
      #-------------------------------------------------------------------------
      # # Enable process tendencies for output
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
      #-------------------------------------------------------------------------
      # disable CICE output and coupler budgets
      with open('user_nl_cice','w') as f: f.write(" histfreq = 'x','x','x','x','x'\n histfreq_n = 0,0,0,0,0\n")
      run_cmd(f'./xmlchange HIST_OPTION=never,HIST_N=1')
      run_cmd(f'./xmlchange BUDGETS=FALSE')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if use_bundle and get_bundle_status(case_root)=='running' and bundle_job_is_active():
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
         - RelativeHumidity
         - qv
         - qc
         - qr
         - qi
         - qm
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
         # - zm_T_mid_tend
         # - zm_qv_tend
         # - zm_horiz_winds_tend
         # - zm_detr_qc
         # - zm_detr_qi
         # - gw_horiz_winds_tend
         # - gw_oro_tend_u
         # - gw_conv_tend_u
         # ---------------------------------------------------------------------
         # ZM diagnostic fields
         - zm_prec
         - zm_activity
         - zm_cape
         - zm_depth
         - mcsp_ds_out
         - mcsp_dq_out
         - mcsp_du_out
         - mcsp_freq
         - mcsp_shear
         - evap_ds_out
         - evap_dq_out
         # ---------------------------------------------------------------------
         # # cosp
         # - isccp_ctptau
         # - modis_ctptau
         # - misr_cthtau
         # - isccp_cldtot
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
def get_case_root(case):
   # bundle members live inside the bundle directory so they can be removed together
   if use_bundle: return f'{get_bundle_dir()}/cases/{case}'
   return f'{scratch_root}/{case}'
#---------------------------------------------------------------------------------------------------
def get_bundle_status(case_root):
   status_file = f'{case_root}/bundle_status'
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
   for d in ['cases','logs','hostfiles']: os.makedirs(f'{bundle_dir}/{d}',exist_ok=True)
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
   # only written once so the case keeps its place in the node packing order
   if not os.path.isfile(f'{case_root}/bundle_order'):
      with open(f'{case_root}/bundle_order','w') as f: f.write(f'{datetime.datetime.now().timestamp():.6f}\n')
   with open(f'{case_root}/bundle_status','w') as f: f.write('active\n')
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
#   python3 bundle.job --status              => print status of bundle members
#   python3 bundle.job --submit              => submit a bundle job unless one is already queued/running
#   python3 bundle.job --hold     <pattern>  => skip matching members until re-activated
#   python3 bundle.job --activate <pattern>  => (re)activate matching members
#   python3 bundle.job --remove   <pattern>  => delete matching case directories
#   python3 bundle.job --purge               => cancel the bundle job and delete the whole bundle
#   (no arguments)                           => inside the PBS job: run one segment of each active member
#
# <pattern> is a shell-style wildcard matched against the case name - an exact case name
# only matches that case, and a pattern without wildcards matches any case containing it
#
# members are the case directories in cases/ that have a bundle_status file:
#   active  => will run a segment in the next bundle job
#   running => currently running a segment
#   done    => RESUBMIT exhausted
#   failed  => last segment failed - fix the case and set back to "active"
#   hold    => skipped until set back to "active"
#
# NOTE: keep this compatible with the system python3 (3.6) on the compute nodes
#-------------------------------------------------------------------------------
import os, sys, re, json, glob, time, signal, shutil, fnmatch, subprocess as sp
bundle_dir = '@@BUNDLE_DIR@@'
cases_dir  = os.path.join(bundle_dir,'cases')
job_script = os.path.join(bundle_dir,'bundle.job')
jobid_file = os.path.join(bundle_dir,'jobid')
this_jobid = os.getenv('PBS_JOBID','')
poll_interval   = 30  # seconds between checks for finished segments
walltime_margin = 300 # a SIGTERM this close to the walltime [s] is treated as a walltime kill
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
   # members are packed onto nodes in the order they were added (see bundle_order)
   roots = [os.path.dirname(f) for f in glob.glob(os.path.join(cases_dir,'*','bundle_status'))]
   def order(root):
      try:
         return float(read_file(os.path.join(root,'bundle_order'),'inf'))
      except ValueError:
         return float('inf')
   return sorted(roots,key=lambda r:(order(r),case_name(r)))
def get_status(root): return read_file(os.path.join(root,'bundle_status'),'removed')
def set_status(root,status):
   # the case directory may have been deleted by hand while the job was running
   if os.path.isdir(root): write_file(os.path.join(root,'bundle_status'),status)
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
def walltime_seconds(walltime):
   sec = 0
   for v in walltime.split(':'): sec = sec*60 + int(v)
   return sec
def match_members(pattern):
   members = get_members()
   exact = [r for r in members if case_name(r)==pattern]
   if len(exact)>0: return exact
   if not any(c in pattern for c in '*?['): pattern = '*'+pattern+'*'
   return [r for r in members if fnmatch.fnmatchcase(case_name(r),pattern)]
def confirm(msg):
   return input(msg+' [y/N] ').strip().lower() in ['y','yes']
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
def get_target_members(pattern):
   # members that are running in an active job can't be changed or removed
   roots = match_members(pattern)
   if len(roots)==0: sys.exit('no bundle members match: {}'.format(pattern))
   if job_is_active(read_file(jobid_file)):
      for r in [r for r in roots if get_status(r)=='running']:
         print('  skipping member that is currently running: {}'.format(case_name(r)))
      roots = [r for r in roots if get_status(r)!='running']
   return roots
def set_member_status(pattern,status):
   for root in get_target_members(pattern):
      set_status(root,status)
      print('  {:<8} {}'.format(status,case_name(root)))
def remove_members(pattern):
   roots = get_target_members(pattern)
   if len(roots)==0: return
   print('\n  case directories to delete:')
   for root in roots: print('    '+root)
   if not confirm('\n  delete {} case directories?'.format(len(roots))): return
   for root in roots:
      shutil.rmtree(root)
      print('  removed: '+case_name(root))
def purge():
   jobid = read_file(jobid_file)
   active = job_is_active(jobid)
   print('\n  bundle  : '+bundle_dir)
   print('  members : {}'.format(len(get_members())))
   if active: print('  job     : {} (will be cancelled)'.format(jobid))
   if not confirm('\n  delete the whole bundle directory?'): return
   if active:
      sp.call(['qdel',jobid])
      # wait for the job to go away so nothing writes into the case directories while deleting
      for i in range(60):
         if not job_is_active(jobid): break
         time.sleep(5)
      else:
         sys.exit('ERROR: bundle job {} is still active - try again later'.format(jobid))
   shutil.rmtree(bundle_dir)
   print('  removed: '+bundle_dir)
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
def finish_segment(root,rc,jid):
   # update the member status after a segment exits - returns True if the segment succeeded
   case = case_name(root)
   if not os.path.isdir(root):
      log('member was removed while running: {}'.format(case))
      return False
   if rc!=0:
      set_status(root,'failed')
      log('FAILED: {} (exit code {}) - see logs/{}.{}.log'.format(case,rc,case,jid))
      return False
   try:
      resub = int(xmlquery(root,'RESUBMIT'))
      if resub > 0:
         xmlchange(root,'RESUBMIT={}'.format(resub-1))
         set_status(root,'active')
         log('finished segment: {} (model date: {}, RESUBMIT={})'.format(case,model_date(root),resub-1))
      else:
         set_status(root,'done')
         log('finished: {} (model date: {})'.format(case,model_date(root)))
   except Exception as e:
      set_status(root,'failed')
      log('ERROR: could not update {} after its segment finished: {}'.format(case,e))
      return False
   return True
#-------------------------------------------------------------------------------
def run_bundle():
   global logfile
   cfg = load_cfg()
   start_time = time.time()
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
   if len(launched)==0:
      # avoid an endless chain of empty jobs
      log('ERROR: no members were launched - not resubmitting')
      logfile.close()
      return
   nsuccess = 0
   pending = list(launched)
   #----------------------------------------------------------------------------
   # PBS sends SIGTERM when the walltime is reached (and for qdel) - reset unfinished members
   # so the next job reruns their segment, and only resubmit if this was a walltime kill
   # (NOTE: the walltime is taken from bundle.json, so this assumes it hasn't changed since submission)
   def on_sigterm(signum,frame):
      nonlocal nsuccess
      elapsed = time.time()-start_time
      hit_walltime = elapsed > walltime_seconds(cfg['walltime'])-walltime_margin
      log('received SIGTERM after {:.0f}s ({})'.format(elapsed,'walltime limit' if hit_walltime else 'job cancelled'))
      try:
         # segments that finished cleanly but haven't been processed yet
         for item in list(pending):
            root,proc,out = item
            if proc.poll()==0:
               pending.remove(item)
               if finish_segment(root,0,jid): nsuccess += 1
         for root,proc,out in launched:
            if get_status(root)=='running':
               set_status(root,'active')
               log('segment did not finish - reset to "active": {}'.format(case_name(root)))
         if not hit_walltime:
            log('not resubmitting')
         elif nsuccess==0:
            # avoid an endless chain of jobs where every segment hits the walltime
            log('ERROR: no segments finished before the walltime - not resubmitting (reduce STOP_N or increase walltime)')
         else:
            submit()
      except Exception as e:
         log('ERROR in SIGTERM handler: {}'.format(e))
      sys.exit(1)
   signal.signal(signal.SIGTERM,on_sigterm)
   #----------------------------------------------------------------------------
   # update each member's status as soon as its segment finishes
   while len(pending)>0:
      time.sleep(poll_interval)
      for item in list(pending):
         root,proc,out = item
         rc = proc.poll()
         if rc is None: continue
         pending.remove(item)
         out.close()
         if finish_segment(root,rc,jid): nsuccess += 1
   signal.signal(signal.SIGTERM,signal.SIG_DFL)
   submit()
   logfile.close()
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   def get_pattern():
      if len(sys.argv)<3: sys.exit('ERROR: {} requires a case name pattern'.format(sys.argv[1]))
      return sys.argv[2]
   if '--status' in sys.argv:
      print_status()
   elif '--submit' in sys.argv:
      submit()
   elif '--hold' in sys.argv[1:2]:
      set_member_status(get_pattern(),'hold')
   elif '--activate' in sys.argv[1:2]:
      set_member_status(get_pattern(),'active')
   elif '--remove' in sys.argv[1:2]:
      remove_members(get_pattern())
   elif '--purge' in sys.argv:
      purge()
   else:
      if this_jobid=='': sys.exit('ERROR: bundle.job should only be run without arguments inside a PBS job')
      run_bundle()
'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   #-------------------------------------------------------------------------------
   print(); print('  case list:')
   max_len = 0
   for n in range(len(opt_list)):
      max_len = max(max_len,len(get_case_name(opt_list[n])))
   for n in range(len(opt_list)):
      print(f'    {get_case_name(opt_list[n]):{max_len}}   => {get_exe_case_name(opt_list[n])}')
   print()
   # exit()
   #-------------------------------------------------------------------------------
   for n in range(len(opt_list)):
      main( opt_list[n] )
   if use_bundle and submit:
      write_bundle_files()
      run_cmd(f'python3 {get_bundle_dir()}/bundle.job --submit')
   if use_bundle and os.path.isfile(f'{get_bundle_dir()}/bundle.job'):
      run_cmd(f'python3 {get_bundle_dir()}/bundle.job --status')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
