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
E3SMv4 prototype ZM tuning runs on Aurora using the multi-instance (MI) capability
=> companion to run_E3SM.2026-v4-test.alcf.py, which uses a custom job bundler instead
baseline config follows v4_dev_scripts/run.test.ne256.20260909.ZM.splitform.newL128.Recipe2_updated.GWD.sh

src_dir = E3SM_SRC1 => branch whannah/eamxx/multi-instance-restart-fix (master @ Oct 9, 34d78535b7 + fix)
  - EAMxx restart/history file prefixes and rpointer.atm get the instance suffix (e.g. _0001)
  - buildnml creates data/scream_input.yaml_NNNN and data/namelist.nl_NNNN for each
    instance with a case_scripts/user_nl_eamxx_NNNN file (atmchange syntax, one change per line)

nohup python -u run_E3SM.2026-v4-MI-test.alcf.py > run_E3SM.2026-v4-MI-test.alcf.py.out &

How it works
- each add_case() is ONE case with len(members) instances (MULTI_DRIVER=TRUE, NINST=len(members))
- num_nodes is per instance, so the job uses num_nodes*len(members) nodes
- settings common to all members use atmchange as usual (=> namelist_scream.xml)
- member specific settings are written to user_nl_eamxx_NNNN
- resubmission is handled by CIME as usual (all members advance together)
- output files: output.1ma_0001.*, output.1da_0002.*, etc.
- a table of members is written to case_scripts/instance_table.txt

Limitations
- all members share one clock - new members can't be added to a case that has already run,
  so a new batch of members has to be a new case (i.e. new prefix)
- member specific changes to atm_procs_list are not supported
- members can't use different node counts or grids
'''
#---------------------------------------------------------------------------------------------------
import os, sys, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'E3SM_Dec'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC1' # branch => whannah/eamxx/multi-instance-restart-fix
scratch_root = '/lus/flare/projects/E3SM_Dec/whannah/scratch'
din_loc_root = '/lus/flare/projects/E3SMinput/data'

# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True

#---------------------------------------------------------------------------------------------------

# ne30 test of multi-instance restarts in the debug-scaling queue (3-255 nodes, 1 hour)
# stop_opt,stop_n,resub,walltime,queue = 'ndays',5,2,'1:00:00','debug-scaling'

stop_opt,stop_n,resub,walltime,queue = 'nmonths',1,0,'12:00:00','prod'
# stop_opt,stop_n,resub,walltime,queue = 'nmonths',3,4*5-1,'12:00:00','prod' # 5-yr ne256 - check throughput first!

#---------------------------------------------------------------------------------------------------
kwargs_ne256 = ({'num_nodes':64,'grid':'ne256pg2_ne256pg2'})
kwargs_ne30  = ({'num_nodes':4, 'grid':'ne30pg2_ne30pg2'})

# ### test of multi-instance mechanics - same members as the bundling test
# kwargs_common = {'prefix':'2026-v4-MI-TEST-00','compset':'F2010xx-ZM-CICE','arch':'GPU'}
# add_case(**kwargs_common,**kwargs_ne30, members=[ {},
#                                                   {'cpt':100},
#                                                   {'cpt':200},
#                                                   {'cpt':400},
#                                                   {'dct':0.01},
#                                                   {'dct':0.02},
#                                                   {'dct':0.04},
#                                                   {'dct':0.04},
#                                                   {'mct':0.2},
#                                                   {'mct':0.4},
#                                                 ])

### ZM tuning - batch 1 (4 x 64 nodes = 256 nodes)
kwargs_common = {'prefix':'2026-MI-TUNE-00','compset':'F2010xx-ZM-CICE','arch':'GPU'}
add_case(**kwargs_common,**kwargs_ne256,members=[ {},             # 0001
                                                  {'cpt':100},    # 0002
                                                  {'cpt':200},    # 0003
                                                  {'cpt':400},    # 0004
                                                  {'dct':0.01},   # 0005
                                                  {'dct':0.02},   # 0006
                                                  {'dct':0.04},   # 0007
                                                  {'dct':0.04},   # 0008
                                                  {'mct':0.2},    # 0009
                                                  {'mct':0.4},    # 0000
                                                  {'alf':0.10},   # 0011
                                                  {'alf':0.18},   # 0012
                                                  {'ke' :2.0e-6}, # 0013
                                                  {'ke' :3.0e-6}, # 0014
                                                ])

#---------------------------------------------------------------------------------------------------
# short option names for ZM parameters => zm::<param>
zm_param_map = {}
zm_param_map['tau']   = 'tau'               # convective adjustment time scale [s]       (default 3600)
zm_param_map['dmp']   = 'dmpdz'             # fractional mass entrainment rate [1/m]     (default -0.7e-3)
zm_param_map['alf']   = 'alfa'              # max downdraft mass flux fraction           (default 0.14)
zm_param_map['ke']    = 'ke'                # evaporation efficiency                     (default 2.5e-6)
zm_param_map['c0l']   = 'c0_lnd'            # autoconversion coefficient over land       (default 0.002)
zm_param_map['c0o']   = 'c0_ocn'            # autoconversion coefficient over ocean      (default 0.002)
zm_param_map['tpf']   = 'tpert_fac'         # temperature perturbation factor            (default 2.0)
zm_param_map['tka']   = 'tiedke_add'        # temperature perturbation                   (default 0.8)
zm_param_map['cpt']   = 'cape_threshold'    # CAPE threshold [J/kg]                      (default 0)
zm_param_map['dct']   = 'dcape_threshold'   # DCAPE threshold [J/kg/s]                   (default 0)
zm_param_map['upl']   = 'upper_limit_pref'  # upper pressure limit for convection [Pa]   (default 40e2)
zm_param_map['cda']   = 'clos_dyn_adj'      # dynamic closure adjustment                 (default false)
zm_param_map['mct']   = 'mcsp_t_coeff'      # MCSP temperature coefficient               (default 0.3)
zm_param_map['mcq']   = 'mcsp_q_coeff'      # MCSP humidity coefficient                  (default 0.0)
zm_param_map['mcu']   = 'mcsp_u_coeff'      # MCSP U-wind coefficient                    (default 0.0)
zm_param_map['mcv']   = 'mcsp_v_coeff'      # MCSP V-wind coefficient                    (default 0.0)
#---------------------------------------------------------------------------------------------------
def get_grid_name(opts): return opts['grid'].split('_')[0]
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items():
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['members']:   case_list.append(f'NINST_{len(val)}')
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
def get_member_name(member):
   if len(member)==0: return 'control'
   name_list = []
   for key,val in member.items():
      if isinstance(val, str):
         name_list.append(f'{key}_{val}')
      else:
         name_list.append(f'{key}_{val:g}')
   return '.'.join(name_list)
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
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' not in opts: raise ValueError('you must specify num_nodes!')
   if len(opts.get('members',[])) < 2: raise ValueError('you must specify at least 2 members!')
   for member in opts['members']:
      for key in member.keys():
         if key not in zm_param_map: raise ValueError(f'unsupported member option: {key}')
   #------------------------------------------------------------------------------------------------
   members = opts['members']
   ninst = len(members)
   case_root = f'{scratch_root}/{case}'
   atm_init_file,lnd_init_file = get_init_files(opts)
   # if newcase or set_run_opts:
   #    for f in [atm_init_file,lnd_init_file]:
   #       if f is not None and not os.path.isfile(f): exit(f'\n{clr.RED}missing initial condition file: {f}{clr.END}\n')
   #------------------------------------------------------------------------------------------------
   arch = opts.get('arch','CPU')
   if arch=='GPU': compiler,max_mpi_per_node = 'intelgpu', 12
   if arch=='CPU': compiler,max_mpi_per_node = 'intel',   102
   atm_ntasks = max_mpi_per_node*opts['num_nodes'] # tasks per instance
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
      cmd += f' --pecount {atm_ntasks}x1 --machine aurora --compiler {compiler} '
      # moab is the default, but driver-moab aborts with MULTI_DRIVER=TRUE ("does not yet support multi-driver")
      # => use mct, as in the E3SM RCS tests (RCS_Vmct_C4.*.F2010-SCREAMv1)
      cmd += f' --driver mct ' # moab / mct
      run_cmd(cmd)
      # Copy this run script into the case directory
      timestamp = datetime.datetime.now().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'cp {os.path.realpath(__file__)} {case_root}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd(f'./xmlchange EAMXX_VGRID=L128v4')
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      run_cmd(f'./xmlchange DOUT_S=FALSE')
      # each instance gets its own driver and the full PE layout
      run_cmd(f'./xmlchange MULTI_DRIVER=TRUE,NINST={ninst}')
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if set_run_opts:
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      # run_cmd(f'./xmlchange RUN_STARTDATE=2010-01-01')
      #-------------------------------------------------------------------------
      # v4 prototype settings - common to all members
      run_cmd(f'./atmchange -b physics::atm_procs_list="zm,gw,mac_aero_mic,rrtmgp"')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list="shoc,cld_fraction,spa,p3"')
      # run_cmd(f'./atmchange -b physics::cosp::cosp_frequency_units="hours"')
      # run_cmd(f'./atmchange -b physics::cosp::cosp_frequency=1')
      # split form
      run_cmd(f'./atmchange -b theta_advect_form=2')
      run_cmd(f'./atmchange -b pgrad_correction=0')
      # # aerosol / cloud tuning
      # run_cmd(f'./atmchange -b spa_data_file="{din_loc_root}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      # run_cmd(f'./atmchange -b spa_ccn_to_nc_factor=750.0')
      # run_cmd(f'./atmchange -b length_fac=0.51')
      # run_cmd(f'./atmchange -b autoconversion_prefactor=2960.0')
      # run_cmd(f'./atmchange -b autoconversion_qc_exponent=2.42')
      # gravity waves
      run_cmd(f'./atmchange -b use_gw_orographic=true')
      run_cmd(f'./atmchange -b use_gw_convect=true')
      #-------------------------------------------------------------------------
      # member specific ZM parameters => user_nl_eamxx_NNNN
      table = f'{"instance":<10} member\n'
      for m,member in enumerate(members):
         inst_suffix = f'_{m+1:04d}'
         nl_txt = f'# {get_member_name(member)}\n'
         for key,val in member.items():
            if isinstance(val,bool): val = 'true' if val else 'false'
            nl_txt += f'zm::{zm_param_map[key]}={val}\n'
         with open(f'user_nl_eamxx{inst_suffix}','w') as f: f.write(nl_txt)
         table += f'{inst_suffix:<10} {get_member_name(member)}\n'
      with open('instance_table.txt','w') as f: f.write(table)
      print(f'\n{table}')
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
      # land / sea ice / coupler settings - same for all instances
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
      cice_nl = " histfreq = 'x','x','x','x','x'\n histfreq_n = 0,0,0,0,0\n" # disable CICE output
      for m in range(ninst):
         with open(f'user_nl_elm_{m+1:04d}','w') as f: f.write(elm_nl)
         with open(f'user_nl_cice_{m+1:04d}','w') as f: f.write(cice_nl)
      run_cmd(f'./xmlchange HIST_OPTION=never,HIST_N=1')
      run_cmd(f'./xmlchange BUDGETS=TRUE')
      #-------------------------------------------------------------------------
      # make sure the per-instance input files get generated
      run_cmd('./preview_namelists')
      for m in range(ninst):
         yaml_file = f'{case_root}/run/data/scream_input.yaml_{m+1:04d}'
         if not os.path.isfile(yaml_file): exit(f'\n{clr.RED}missing {yaml_file} - is src_dir missing the multi-instance fix?{clr.END}\n')
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
         - LW_flux_up_at_model_top
         - U_at_850hPa
         - V_at_850hPa
         - U_at_200hPa
         - V_at_200hPa
         - U_at_100hPa
         - U_at_50hPa
         - U_at_30hPa
         - U_at_20hPa
         - U_at_10hPa
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
         # - zm_T_mid_tend
         # - zm_qv_tend
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
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
