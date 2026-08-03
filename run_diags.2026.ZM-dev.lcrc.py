#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
# unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
    case_opts = {}
    for k, val in kwargs.items(): case_opts[k] = val
    opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
st_archive        = True
# clear_zppy_status = True
# check_zppy_status = True
# run_zppy          = True
#---------------------------------------------------------------------------------------------------
acct = 'e3sm'
username = 'whannah'
activation_cmd  = f'source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh'
obs_path        = f'/lcrc/group/e3sm/diagnostics/observations/Atm/'
test_data_path  = f'/lcrc/soft/climate/e3sm_diags_data/test_model_data_for_acme_diags/'
html_path       = f'/lcrc/group/e3sm/public_html/diagnostic_output/{username}/'
web_address     = f'https://web.lcrc.anl.gov/public/e3sm/diagnostic_output/{username}/'
#---------------------------------------------------------------------------------------------------

scratch_path='/lcrc/group/e3sm/ac.whannah/scratch/chrys/from_olcf'
map_file = os.get_env('HOME')+f'/maps/map_ne30pg2_to_90x180_traave.nc'
add_case(name='E3SM.2026-ZM-ICW-00.F2010xx-ZM.ne30pg2.NN_4.zm_rad_0',root=scratch_path,yr1=0001,yr2=0005,map_file=map_file)
add_case(name='E3SM.2026-ZM-ICW-00.F2010xx-ZM.ne30pg2.NN_4.zm_rad_1',root=scratch_path,yr1=0001,yr2=0005,map_file=map_file)

#---------------------------------------------------------------------------------------------------
# def get_sets_to_run(opts):
#     diag_set_list = []
#     diag_set_list.append('lat_lon'); diag_set_list.append('zonal_mean_xy')
#     diag_set_list.append('zonal_mean_2d'); diag_set_list.append('meridional_mean_2d')
#     diag_set_list.append('zonal_mean_2d_stratosphere')
#     # diag_set_list.append('lat_lon_native'); # diag_set_list.append('polar')
#     # diag_set_list.append('cosp_histogram')
#     # diag_set_list.append('enso_diags')
#     diag_set_list.append('qbo')
#     diag_set_list.append('tropical_subseasonal')
#     # diag_set_list.append('tc_analysis')
#     # diag_set_list.append('streamflow')
#     # diag_set_list.append('diurnal_cycle')
#     # diag_set_list.append('annual_cycle_zonal_mean')
#     # diag_set_list.append('area_mean_time_series'); # diag_set_list.append('arm_diags')
#     # diag_set_list.append('lat_lon_land'); # diag_set_list.append('lat_lon_river')
#     # diag_set_list.append('aerosol_aeronet'); # diag_set_list.append('aerosol_budget')
#     return '['+(','.join(diag_set_list))+']'
#---------------------------------------------------------------------------------------------------
# def get_diags_script(opts):
#     root = opts['root']
#     name = opts['name']
#     return f'''
# import os
# from e3sm_diags.parameter.core_parameter import CoreParameter
# from e3sm_diags.run import runner

# param = CoreParameter()

# param.reference_data_path = '{obs_path}/climatology/'
# param.test_data_path = '{test_data_path}/climatology/'
# param.test_name = '{name}'
# # param.seasons = ["ANN","DJF", "MAM", "JJA", "SON"]
# param.seasons = ["ANN"]

# param.results_dir = '{html_path}/{name}'
# # Use the following if running in parallel:
# #param.multiprocessing = True
# #param.num_workers = 32

# # Use below to run all core sets of diags:
# # runner.sets_to_run = ['lat_lon', 'zonal_mean_xy', 'zonal_mean_2d', 'meridional_mean_2d']
# runner.sets_to_run = {get_sets_to_run(opts)}

# runner.run_diags([param])
# '''
#---------------------------------------------------------------------------------------------------
# def get_zppy_config(case_name,case_root,grid_short,nyr):
def get_zppy_config(opts):
    root = opts['root']
    name = opts['name']
    short_name = name
    dst_grid = '90x180'
    map_file = opts['map_file']
    yr1,yr2,ts_nyr = 1995,1995+nyr-1,nyr
    # header
    config_txt = f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = /global/cfs/cdirs/e3sm/www/whannah/2025-SciDAC
machine = "pm-cpu"
partition = batch
environment_commands = "source {unified_env}"
'''
    # climatology calculations
    config_txt += f'''
[climo]
active = True
walltime = "1:00:00"
years = "{yr1}:{yr2}:{nyr}",

  [[ atm_monthly_{dst_grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{dst_grid}"
  frequency = "monthly"
'''
    config_txt += f'''
[ts]
active = True
walltime = "0:30:00"
years = "{yr1}:{yr2}:{ts_nyr}",

  [[ atm_monthly_{dst_grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{dst_grid}"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

  [[ atm_monthly_glb ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = "glb"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
'''
#   [[ land_monthly ]]
#   input_subdir = "archive/lnd/hist"
#   input_files = "elm.h0"
#   mapping_file = {map_file}
#   grid = "{dst_grid}"
#   frequency = "monthly"
#   vars = "FSH,RH2M"
#   extra_vars = "landfrac"
# '''
    config_txt += f'''
[e3sm_diags]
active = True
years = "{yr1}:{yr2}:{nyr}",
ts_num_years = {ts_nyr}
ref_start_yr = 1979
ref_final_yr = 2016
walltime = "24:00:00"

  [[ atm_monthly_{dst_grid}_aave ]]
  short_name = '{short_name}'
  grid = '{dst_grid}'
  sets = 'lat_lon','zonal_mean_xy','zonal_mean_2d','polar','cosp_histogram','meridional_mean_2d','enso_diags','qbo','annual_cycle_zonal_mean','zonal_mean_2d_stratosphere'
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
  reference_data_path = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/climatology'
  obs_ts = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series'
  dc_obs_climo = '/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags/climatology/'
  output_format_subplot = "pdf",

[global_time_series]
active = True
atmosphere_only = True
years = "{yr1}-{yr2}", 
ts_num_years = {ts_nyr}
figstr = "{short_name}"
experiment_name = "{case_name}"
ts_years = "{yr1}-{yr2}",
climo_years = "{yr1}-{yr2}",

'''
   return config_txt
#---------------------------------------------------------------------------------------------------
def main(opts):
    case_root = f"{opts['root']}/{opts['name']}"
    #------------------------------------------------------------------------------------------------
    # diags_script = 'run_e3sm_diags.py'
    # run_cmd(f'python {diags_script}')
    #------------------------------------------------------------------------------------------------
    if st_archive:
        os.chdir(f'{case_root}/case_scripts')
        run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
        run_cmd('./case.st_archive')
    #------------------------------------------------------------------------------------------------
   if clear_zppy_status:
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         os.remove(file_name)
   #------------------------------------------------------------------------------------------------
    if check_zppy_status:
        status_path = f'{case_root}/post/scripts'
        print(' '*4+clr.END+status_path+clr.END)
        status_files = glob.glob(f'{status_path}/*status')
        max_len = 0
        for file_path in status_files:
            file_name = file_path.replace(f'{status_path}/','')
            max_len = max(len(file_name),max_len)
        for file_path in status_files:
            file_name = file_path.replace(f'{status_path}/','')
            cmd = f'tail {file_path} '
            proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
            (msg, err) = proc.communicate()
            msg = msg.strip()
            msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
            msg = msg.replace('WAITING',f'{clr.YELLOW}WAITING{clr.END}')
            msg = msg.replace('RUNNING',f'{clr.YELLOW}RUNNING{clr.END}')
            msg = msg.replace('OK',f'{clr.GREEN}OK{clr.END}')
            print(' '*6+f'{clr.CYAN}{file_name:{max_len}}{clr.END} : {msg}')
    #------------------------------------------------------------------------------------------------
    if run_zppy:
        # Clear status files that don't indicate "OK"
        status_files = glob.glob(f'{case_root}/post/scripts/*status')
        for file_name in status_files:
            file_ptr = open(file_name)
            contents = file_ptr.read().split()
            if contents[0]!='OK': os.remove(file_name)

        # dynamically create the zppy config file
        zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
        file = open(zppy_file_name,'w')
        file.write(get_zppy_config(case,case_root,grid_short,nyr))
        file.close()

        print(f'  zppy cfg => {zppy_file_name}')

        # submit the zppy job
        run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    for n in range(len(opt_list)):
        main( opt_list[n] )

    print_line()
   
#---------------------------------------------------------------------------------------------------