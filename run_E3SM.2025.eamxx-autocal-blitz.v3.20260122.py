#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import os, sys, datetime, subprocess as sp, hashlib, json
from shutil import copy2
from optparse import OptionParser
#-------------------------------------------------------------------------------
# # command line options
# parser = OptionParser()
# parser.add_option("-u", "--user",action="store", type="string", dest="user")
# (opts, args) = parser.parse_args()
#---------------------------------------------------------------------------------------------------
''' ne30 grid for history map files
NE=30
GRID_ROOT=/lus/flare/projects/E3SM_Dec/whannah/files_grid
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
'''
#---------------------------------------------------------------------------------------------------
''' history map files
NE=128
GRID_ROOT=/lus/flare/projects/E3SM_Dec/whannah/files_grid
SRC_GRID=${GRID_ROOT}/ne${NE}pg2_scrip.nc
DST_GRID=${GRID_ROOT}/ne30pg2_scrip.nc
MAP_FILE=${DIN_LOC_ROOT}/atm/scream/maps/map_ne${NE}pg2_to_ne30pg2_traave.20260128.nc
ncremap --alg_typ=traave --grd_src=${SRC_GRID} --grd_dst=${DST_GRID} --map=${MAP_FILE}
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
ens_opt_list,exe_opt_list = [],[]
def add_case( exe=False, **kwargs):
   global cnt
   case_opts = {}
   for key,val in kwargs.items(): case_opts[key] = val
   if     exe: exe_opt_list.append(case_opts)
   if not exe: ens_opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
def set_tuning_params(LHS_parameter_values):
   tuning_params = {}
   tuning_params['thl2tune']                               = LHS_parameter_values[0]
   tuning_params['qw2tune']                                = LHS_parameter_values[1]
   tuning_params['length_fac']                             = LHS_parameter_values[2]
   tuning_params['c_diag_3rd_mom']                         = LHS_parameter_values[3]
   tuning_params['coeff_kh']                               = LHS_parameter_values[4]
   tuning_params['coeff_km']                               = LHS_parameter_values[5]
   tuning_params['lambda_low']                             = LHS_parameter_values[6]
   tuning_params['lambda_high']                            = LHS_parameter_values[7]
   tuning_params['spa_ccn_to_nc_factor']                   = LHS_parameter_values[8]
   tuning_params['cldliq_to_ice_collection_factor']        = LHS_parameter_values[9]
   tuning_params['rain_to_ice_collection_factor']          = LHS_parameter_values[10]
   tuning_params['accretion_prefactor']                    = LHS_parameter_values[11]
   tuning_params['deposition_nucleation_exponent']         = LHS_parameter_values[12]
   tuning_params['max_total_ni']                           = LHS_parameter_values[13]
   tuning_params['ice_sedimentation_factor']               = LHS_parameter_values[14]
   tuning_params['rain_selfcollection_breakup_diameter']   = LHS_parameter_values[15]
   tuning_params['autoconversion_prefactor']               = LHS_parameter_values[16] # added Nov 2025
   tuning_params['autoconversion_qc_exponent']             = LHS_parameter_values[17] # added Nov 2025
   tuning_params['autoconversion_radius']                  = LHS_parameter_values[18] # added Nov 2025
   return tuning_params
#---------------------------------------------------------------------------------------------------
# load JSON file with parameter values
with open('/lus/flare/projects/E3SM_Dec/prod/ppe-20251106/normranked_LH_sampling_base10.json', 'r') as file:
   LHS_parameter_values = json.load(file)
   num_param = len(LHS_parameter_values)
   if 'num_case' not in globals(): num_case  = len(LHS_parameter_values)
#---------------------------------------------------------------------------------------------------
clean_exe,create_exe,config_exe,build_exe,print_case_list = False,False,False,False,False
newcase,config,set_params,set_timestep,set_output,set_runopt,submit,continue_run = False,False,False,False,False,False,False,False

create_exe   = True
config_exe   = True
build_exe    = True
# clean_exe    = True

# print_case_list = True

newcase        = True # create the case via create_newcase
config         = True # configure the case via case.setup
set_params     = True # set tuning parameter values
set_timestep   = True # set time step parameters according to grid
set_output     = True # set history output specs
set_runopt     = True # update run-time parameters - including run length
submit         = True # only runs case.submit
# continue_run   = True

# disable_bfb = False
# num_case = 1 # uncomment to override and use small number of cases for testing

acct = 'E3SM_Dec'
queue = 'prod' # debug / prod

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',122,3,'06:00:00' # 122*3=366 model-days
stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'04:00:00' # 73*5=365 model-days
# stop_opt,stop_n,resub,walltime = 'nyears',1,0,'24:00:00' # 1 myear in 24 wall-hrs

# prefix = '2025-EACB-v3'
prefix = '2025-EACB-v4' # alt time step settings - see set_timestep section

src_dir = '/lus/flare/projects/E3SM_Dec/whannah/e3sm_src' # branch => whannah/2025-eamxx-autocal-blitz
# src_dir = '/lus/flare/projects/E3SM_Dec/prod/ppe-20251106/E3SM-20251219' # branch => whannah/2025-eamxx-autocal-blitz

ens_case_root = '/lus/flare/projects/E3SM_Dec/whannah/scratch'
# ens_case_root = '/lus/flare/projects/E3SM_Dec/prod/ppe-20251106/casedirs20251223'

#---------------------------------------------------------------------------------------------------
# num_case = 1 ; print(f'\n{clr.RED}WARNING - num_case has been reset to {num_case} for testing  - WARNING{clr.END}\n')
# case_beg,case_end = 0,num_case
# case_beg,case_end = 0,32
case_beg,case_end = 0,1

if (case_end-case_beg+1)<num_case:
   print(f'\n{clr.RED}WARNING - only running cases {case_beg}-{(case_end-1)} - WARNING{clr.END}\n')
#---------------------------------------------------------------------------------------------------
# add_case(exe=True,prefix=prefix,grid='ne256',num_nodes=128)
# add_case(exe=True,prefix=prefix,grid='ne128',num_nodes=32)
# add_case(exe=True,prefix=prefix,grid='ne64', num_nodes=16)
add_case(exe=True,prefix=prefix,grid='ne32', num_nodes=4)
#---------------------------------------------------------------------------------------------------
cnt_beg = 111
cnt = 0
# for c in range(num_case):
for c in range(case_beg,case_end):
   tuning_params = set_tuning_params(LHS_parameter_values[c])
   # add_case(prefix=prefix,member=f'{(cnt_beg+cnt):03}',grid='ne256',num_nodes=128,tuning_params=tuning_params)
   # add_case(prefix=prefix,member=f'{(cnt_beg+cnt):03}',grid='ne128',num_nodes=32, tuning_params=tuning_params)
   # add_case(prefix=prefix,member=f'{(cnt_beg+cnt):03}',grid='ne64', num_nodes=16, tuning_params=tuning_params)
   add_case(prefix=prefix,member=f'{(cnt_beg+cnt):03}',grid='ne32', num_nodes=4,  tuning_params=tuning_params)
   cnt += 1

#---------------------------------------------------------------------------------------------------
# commmon settings for all runs
RUN_START_DATE = '2019-08-01'
din_loc_root   = '/lus/flare/projects/E3SMinput/data'
lnd_init_file, lnd_data_file, lnd_luse_file  = None, None, None
#---------------------------------------------------------------------------------------------------
def get_case_root(case): return f'{ens_case_root}/{case}'
#---------------------------------------------------------------------------------------------------
def get_case_name(opts,exe=False):
   case_list = []
   loc_prefix = opts['prefix']
   loc_prefix += '.000' if exe else '.'+opts['member']
   for key,val in opts.items():
      if key in ['prefix']:            case_list.append(loc_prefix)
      if key in ['grid']:              case_list.append(val)
      if key=='num_nodes':             case_list.append(f'NN_{val}')
      # if key=='nyr' and not exe:       case_list.append(f'nyr_{val}')
   case = '.'.join(case_list)
   if exe:
      case = f'{case}.EXE'
   else:
      param_str = '_'.join( [str(val) for val in opts['tuning_params'].values()] ) # only use values
      suffix_hash = hashlib.md5(param_str.encode('utf-8')).hexdigest()
      case = f'{case}.{suffix_hash[:12]}' # truncate the hash to 12 characters
   return case
#---------------------------------------------------------------------------------------------------
# def get_compset(): return 'F20TR-SCREAMv1' # we can't use this until we have new files for flanduse_timeseries
def get_compset(): return 'F2010-SCREAMv1'
#---------------------------------------------------------------------------------------------------
def get_pe_layout(opts):
   num_nodes = opts['num_nodes']
   max_mpi_per_node,atm_nthrds  = 12,1
   atm_ntasks = max_mpi_per_node*num_nodes
   return f'{atm_ntasks}x1'
#---------------------------------------------------------------------------------------------------
def get_grid(opts):
   grid_short,grid = opts['grid'],None
   # if grid_short=='ne256': grid = 'ne256pg2_r025_RRSwISC6to18E3r5'
   # if grid_short=='ne128': grid = 'ne128pg2_r025_RRSwISC6to18E3r5'
   # if grid_short=='ne64' : grid = 'ne64pg2_r025_RRSwISC6to18E3r5'
   # if grid_short=='ne32' : grid = 'ne32pg2_r025_RRSwISC6to18E3r5'
   if grid_short=='ne256': grid = 'ne256pg2_ne256pg2'
   if grid_short=='ne128': grid = 'ne128pg2_ne128pg2'
   if grid_short=='ne64' : grid = 'ne64pg2_ne64pg2'
   if grid_short=='ne32' : grid = 'ne32pg2_ne32pg2'
   if grid is None: raise ValueError('grid cannot be None!')
   return grid
#---------------------------------------------------------------------------------------------------
def get_atm_init_file(opts):
   global din_loc_root
   atm_init_root = '/lus/flare/projects/E3SM_Dec/whannah/HICCUP'
   grid_short,atm_init_file = opts['grid'],None
   # if grid_short=='ne256': atm_init_file = f'{atm_init_root}/HICCUP.atm_era5.2017-12-27.ne256np4.L128.nc'
   if grid_short=='ne256': atm_init_file = f'{din_loc_root}/atm/scream/init/screami_ne256np4L128_era5-20190801-topoadjx6t_20230620.nc'
   if grid_short=='ne128': atm_init_file = None
   if grid_short=='ne64' : atm_init_file = None
   if grid_short=='ne32' : atm_init_file = None
   # if atm_init_file is None: raise ValueError('atm_init_file cannot be None!')
   return atm_init_file
#---------------------------------------------------------------------------------------------------
def get_lnd_init_data_file(opts):
   global din_loc_root
   grid_short,atm_init_file = opts['grid'],None
   lnd_init_file = None
   if grid_short=='ne256': lnd_init_file = f'{din_loc_root}/lnd/clm2/initdata/20230522.I2010CRUELM.ne256pg2.elm.r.2013-08-01-00000.nc'
   if grid_short=='ne128': lnd_init_file = f'{din_loc_root}/lnd/clm2/initdata_map/ne128pg2.elm.r.2013-08-01-00000.64bit.nc'
   if grid_short=='ne64' : lnd_init_file = f'{din_loc_root}/lnd/clm2/initdata_map/ne64pg2.elm.r.2013-08-01-00000.64bit.nc'
   if grid_short=='ne32' : lnd_init_file = f'{din_loc_root}/lnd/clm2/initdata_map/ne32pg2.elm.r.2013-08-01-00000.64bit.nc'
   lnd_data_file = None
   if grid_short=='ne256': lnd_data_file = f'{din_loc_root}/lnd/clm2/surfdata_map/surfdata_ne256pg2_simyr2010_c230207.nc'
   if grid_short=='ne128': lnd_data_file = f'{din_loc_root}/lnd/clm2/surfdata_map/surfdata_ne128pg2_simyr2010_c260116.nc'
   if grid_short=='ne64' : lnd_data_file = f'{din_loc_root}/lnd/clm2/surfdata_map/surfdata_ne64pg2_simyr2010_c260116.nc'
   if grid_short=='ne32' : lnd_data_file = f'{din_loc_root}/lnd/clm2/surfdata_map/surfdata_ne32pg2_simyr2010_c260116.nc'
   # if lnd_init_file is None: raise ValueError('lnd_init_file cannot be None!')
   return lnd_init_file,lnd_data_file
#---------------------------------------------------------------------------------------------------
def create_ens_exe(opts):
   case = get_case_name(opts,exe=True); case_root = get_case_root(case)
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   if create_exe:
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --compset {get_compset()} --res {get_grid(opts)} '
      cmd += f' --mach aurora --compiler oneapi-ifxgpu  '
      cmd += f' --project {acct} --pecount {get_pe_layout(opts)} '
      run_cmd(cmd)
   #----------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #----------------------------------------------------------------------------
   if config_exe:
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld,RUNDIR={case_root}/run ')
      write_lnd_nl_opts(opts)
      run_cmd('./case.setup --reset')
   #----------------------------------------------------------------------------
   if build_exe:
      if clean_exe : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #----------------------------------------------------------------------------
   return
#---------------------------------------------------------------------------------------------------
def run_ens_member(opts):   
   #----------------------------------------------------------------------------
   case = get_case_name(opts)
   case_root = get_case_root(case)
   exe_root = get_case_root( get_case_name(opts,exe=True) )
   #----------------------------------------------------------------------------
   # print(case); return
   #----------------------------------------------------------------------------
   print(f'\n  case : {case} \n')
   print(  f'  case_root: {case_root.replace(case,"")}')
   print(  f'  exe_root : {exe_root}')
   #----------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --compset {get_compset()} --res {get_grid(opts)} '
      cmd += f' --mach aurora --compiler oneapi-ifxgpu  '
      cmd += f' --project {acct} --pecount {get_pe_layout(opts)} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={exe_root}/bld,RUNDIR={case_root}/run ')
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      write_lnd_nl_opts(opts)
      run_cmd('./case.setup --reset')
      run_cmd(f'./xmlchange BUILD_COMPLETE=TRUE ')
   #------------------------------------------------------------------------------------------------
   if set_params :
      tuning_params = opts['tuning_params']
      run_cmd(f'./atmchange -b shoc::thl2tune={tuning_params["thl2tune"]} ')
      run_cmd(f'./atmchange -b shoc::qw2tune={tuning_params["qw2tune"]} ')
      run_cmd(f'./atmchange -b shoc::length_fac={tuning_params["length_fac"]} ')
      run_cmd(f'./atmchange -b shoc::c_diag_3rd_mom={tuning_params["c_diag_3rd_mom"]} ')
      run_cmd(f'./atmchange -b shoc::coeff_kh={tuning_params["coeff_kh"]} ')
      run_cmd(f'./atmchange -b shoc::coeff_km={tuning_params["coeff_km"]} ')
      run_cmd(f'./atmchange -b shoc::lambda_low={tuning_params["lambda_low"]} ')
      run_cmd(f'./atmchange -b shoc::lambda_high={tuning_params["lambda_high"]} ')
      run_cmd(f'./atmchange -b p3::spa_ccn_to_nc_factor={tuning_params["spa_ccn_to_nc_factor"]} ')
      run_cmd(f'./atmchange -b p3::cldliq_to_ice_collection_factor={tuning_params["cldliq_to_ice_collection_factor"]} ')
      run_cmd(f'./atmchange -b p3::rain_to_ice_collection_factor={tuning_params["rain_to_ice_collection_factor"]} ')
      run_cmd(f'./atmchange -b p3::accretion_prefactor={tuning_params["accretion_prefactor"]} ')
      run_cmd(f'./atmchange -b p3::deposition_nucleation_exponent={tuning_params["deposition_nucleation_exponent"]} ')
      run_cmd(f'./atmchange -b p3::max_total_ni={tuning_params["max_total_ni"]} ')
      run_cmd(f'./atmchange -b p3::ice_sedimentation_factor={tuning_params["ice_sedimentation_factor"]} ')
      run_cmd(f'./atmchange -b p3::rain_selfcollection_breakup_diameter={tuning_params["rain_selfcollection_breakup_diameter"]} ')
      run_cmd(f'./atmchange -b p3::autoconversion_qc_exponent={tuning_params["autoconversion_qc_exponent"]} ')
      run_cmd(f'./atmchange -b p3::autoconversion_prefactor={tuning_params["autoconversion_prefactor"]} ')
      run_cmd(f'./atmchange -b p3::autoconversion_radius={tuning_params["autoconversion_radius"]} ')
   #------------------------------------------------------------------------------------------------
   if set_timestep:
      #------------------------------------------------------------------------------------------------
      ''' ne256 defaults
      ATM_NCPL: 144 <= 10 min
      ctl_nl::se_tstep: 33.33333333333
      ctl_nl::dt_remap_factor: 2
      ctl_nl::dt_tracer_factor: 6
      ctl_nl::hypervis_subcycle_q: 6
      ctl_nl::semi_lagrange_trajectory_nsubstep: 0
      '''
      #------------------------------------------------------------------------------------------------
      # New timestep for v2/v3 ensemble
      if opts['prefix']=='2025-EACB-v3':
         run_cmd(f'./xmlchange ATM_NCPL=120') # 12-min
         run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')
         run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
         run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=12')
         run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=12')
         run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
      #------------------------------------------------------------------------------------------------
      # use resolution specific time step settings for 2025-EACB-v4
      if opts['prefix']=='2025-EACB-v4':
         if opts['grid']=='ne256':
            run_cmd(f'./xmlchange ATM_NCPL=120')            # 12-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')  #  0.5-min
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=12')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=12')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
         if opts['grid']=='ne128':
            run_cmd(f'./xmlchange ATM_NCPL=120')            # 12-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=120') #  2-min
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=6')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=6')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=1')
         if opts['grid']=='ne64' :
            run_cmd(f'./xmlchange ATM_NCPL=96')             # 15-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=180') #  3-min
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=5')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=5')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=1')
         if opts['grid']=='ne32' :
            run_cmd(f'./xmlchange ATM_NCPL=72')             # 20-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=300') #  5-min
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=4')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=4')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=1')

   #------------------------------------------------------------------------------------------------
   if set_output :
      #-------------------------------------------------------------------------
      # run_cmd('./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd('./atmchange physics::mac_aero_mic::p3::compute_tendencies+=qv')
      # run_cmd('./atmchange physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd('./atmchange homme::compute_tendencies=T_mid,qv,horiz_winds')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('1ma_ne30pg2.yaml',      set_hist_map(hist_opts_1ma_ne30pg2,opts))
      add_hist_file('3ha_ne30pg2.yaml',      set_hist_map(hist_opts_3ha_ne30pg2,opts))
      add_hist_file('51hi.yaml',             hist_opts_51hi)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
   #------------------------------------------------------------------------------------------------
   if set_runopt :
      #-------------------------------------------------------------------------
      write_lnd_nl_opts(opts)
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={RUN_START_DATE}')
      run_cmd(f'./xmlchange CCSM_CO2_PPMV=407.0') # 2018
      atm_init_file = get_atm_init_file(opts)
      if atm_init_file is not None: run_cmd(f'./atmchange initial_conditions::filename=\"{atm_init_file}\"')
      # run_cmd(f'./atmchange orbital_year=2018')
      #-------------------------------------------------------------------------
      # SST data
      # sst_data_root = '/lus/flare/projects/E3SM_Dec/whannah/HICCUP'
      # run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_DATA_FILENAME --val {sst_data_root}/HICCUP.sst_noaa.2017-2018.nc')
      # run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_GRID_FILENAME --val {din_loc_root}/ocn/docn7/domain.ocn.0.25x0.25.c20190221.nc')
      # run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_ALIGN --val 2017')
      # run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_START --val 2017')
      # run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_END --val 2018')
      #-------------------------------------------------------------------------
      # SST data for Cess2 period
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_DATA_FILENAME --val "{din_loc_root}/atm/cam/sst/sst_ostia_ukmo-l4_ghrsst_3600x7200_20190731_20210309_c20240506.nc"')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_GRID_FILENAME --val "{din_loc_root}/ocn/docn7/domain.ocn.3600x7200.230522.nc"')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_ALIGN --val 2019')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_START --val 2019')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_END --val 2021')
      #-------------------------------------------------------------------------
      # COSP - currently doesn't work
      run_cmd(f'./atmchange physics::atm_procs_list="mac_aero_mic,rrtmgp,cosp"')
      run_cmd(f'./atmchange physics::cosp::cosp_frequency_units="hours"')
      run_cmd(f'./atmchange physics::cosp::cosp_frequency=1')
      #-------------------------------------------------------------------------
      # Set some other run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      # if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      # if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
   #------------------------------------------------------------------------------------------------
   if submit :
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
def set_hist_map(hist_opts,opts):
   map_file = None
   if opts['grid']=='ne32' : map_file = '${DIN_LOC_ROOT}/atm/scream/maps/map_ne32pg2_to_ne30pg2_traave.20260128.nc'
   if opts['grid']=='ne64' : map_file = '${DIN_LOC_ROOT}/atm/scream/maps/map_ne64pg2_to_ne30pg2_traave.20260128.nc'
   if opts['grid']=='ne128': map_file = '${DIN_LOC_ROOT}/atm/scream/maps/map_ne128pg2_to_ne30pg2_traave.20260128.nc'
   if opts['grid']=='ne256': map_file = '${DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc'
   if map_file is not None:
      hist_opts += f'horiz_remap_file: {map_file}\n'
   return hist_opts
#---------------------------------------------------------------------------------------------------
hist_opts_1ma_ne30pg2 = '''
averaging_type: average
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
      - precip_liq_surf_mass_flux
      - precip_ice_surf_mass_flux
      - landfrac
      - ocnfrac
      - PotentialTemperature_at_700hPa
      - PotentialTemperature_at_850hPa
      - PotentialTemperature_at_1000hPa
      - PotentialTemperature_at_2m_above_surface
      - omega_at_500hPa
      - omega_at_700hPa
      - omega_at_850hPa
      - RelativeHumidity_at_700hPa
      - RelativeHumidity_at_1000hPa
      - RelativeHumidity_at_2m_above_surface
      - wind_speed_10m
      - z_mid_at_700hPa
      - z_mid_at_1000hPa
      - T_mid_at_850hPa
      - T_mid_at_700hPa
      - U_at_10m_above_surface
      - V_at_10m_above_surface
      # COSP
      - isccp_ctptau
      - modis_ctptau
      - misr_cthtau
      - isccp_cldtot
max_snapshots_per_file: 1
filename_prefix: 1ma_ne30pg2
iotype: pnetcdf
output_control:
   frequency: 1
   frequency_units: nmonths
restart:
   force_new_file: true
'''

# horiz_remap_file: ${DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc

hist_opts_51hi = '''
averaging_type: instant
fields:
   physics_pg2:
      field_names:
      - LW_flux_up_at_model_top
      - SW_flux_up_at_model_top
      - precip_total_surf_mass_flux
      - T_2m
      - VapWaterPath
      - IceWaterPath
      - LiqWaterPath
      - RainWaterPath
max_snapshots_per_file: 8
filename_prefix: 1hi
iotype: pnetcdf
output_control:
  frequency: 51
  frequency_units: nhours
restart:
  force_new_file: true
'''

hist_opts_3ha_ne30pg2 = '''
averaging_type: average
fields:
   physics_pg2:
      field_names:
      - precip_total_surf_mass_flux
      - U_at_850hPa
      - V_at_850hPa
      - LW_flux_up_at_model_top
max_snapshots_per_file: 40
filename_prefix: 3ha_ne30pg2
iotype: pnetcdf
output_control:
   frequency: 3
   frequency_units: nhours
restart:
   force_new_file: true
'''

# horiz_remap_file: ${DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc

#---------------------------------------------------------------------------------------------------
def get_lnd_nl_opts(opts):
   global lnd_luse_file, lnd_data_file, lnd_init_file
   lnd_opts = f'''
 ! -- Reduce the size of land outputs since we dont need them --
 hist_fincl1 = 'SNOWDP'
 hist_mfilt = 1
 hist_nhtfrq = 0
 hist_avgflag_pertape = 'A'
'''
   lnd_init_file,lnd_data_file = get_lnd_init_data_file(opts)
   if lnd_luse_file is not None: lnd_opts += f' flanduse_timeseries = \'{lnd_luse_file}\' \n'
   if lnd_data_file is not None: lnd_opts += f' fsurdat             = \'{lnd_data_file}\' \n'
   if lnd_init_file is not None: lnd_opts += f' finidat             = \'{lnd_init_file}\' \n'
   lnd_opts += f' check_dynpft_consistency = .false. \n'
   # lnd_opts += f' check_finidat_year_consistency = .false. \n'
   return lnd_opts

def write_lnd_nl_opts(opts):
   file=open('user_nl_elm','w')
   file.write(get_lnd_nl_opts(opts))
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

      if any([create_exe,config_exe,build_exe]):
         for n in range(len(exe_opt_list)):
            create_ens_exe(exe_opt_list[n])

      if print_case_list:
         print()
         for n in range(len(ens_opt_list)):
            print(get_case_name(ens_opt_list[n]))
         print()
         exit()

      if any([newcase,config,set_params,set_output,set_runopt,submit]):

         for n in range(len(ens_opt_list)):
            print('-'*80)
            print(f'case #: {n+1:3} of {len(ens_opt_list)}')
            run_ens_member( ens_opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
