#!/usr/bin/env python3
import os, subprocess as sp, glob, datetime, sys
#---------------------------------------------------------------------------------------------------
'''NOTES
cd /pscratch/sd/w/whannah/e3sm_scratch/from_olcf/E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE.L128v3.6
mkdir -p archive/atm
mv ./hist* archive/atm/

cd /pscratch/sd/w/whannah/e3sm_scratch/from_olcf/E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010-SCREAMv1
mkdir -p archive/atm
mv ./hist* archive/atm/
cd /pscratch/sd/w/whannah/e3sm_scratch/from_olcf/E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE
mkdir -p archive/atm
mv ./hist* archive/atm/
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line(): print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
flags = {
    # 'st_archive'        : False,
    # 'clear_zppy_status' : False,
    # 'check_zppy_status' : False,
    # 'run_zppy_chk'      : True,
    'run_zppy'          : True,
    ### zppy config flags
    'zppy_climo_active'         : True,
    'zppy_climo_diurnal_active' : True,
    'zppy_ts_active'            : True,
    'zppy_diags_active'         : True,
    'zppy_diags_monthly_active' : True,
    # 'zppy_diags_tc_active'      : True, # < this doesn't work - need diags update
}
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
    case_opts = {}
    for k, val in kwargs.items(): case_opts[k] = val
    opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--chk',action='store_true', dest='chk_flag', default=False,help='enable check_zppy_status and disable all other flags')
(opts, args) = parser.parse_args()

if opts.chk_flag:
    flags = { k: False for k in flags }
    flags['check_zppy_status'] = True
#---------------------------------------------------------------------------------------------------
# NERSC
acct = 'e3sm'
username = 'whannah'
unified_env     = f'/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
obs_path        = f'/global/cfs/cdirs/e3sm/diagnostics/observations/Atm'
test_data_path  = f'/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags'
html_path       = f'/global/cfs/cdirs/e3sm/www/{username}/2026-ZM-baseline-ne256'
web_address     = f'http://portal.nersc.gov/cfs/e3sm/{username}'
scratch_path    = f'/pscratch/sd/w/whannah/e3sm_scratch/from_olcf'
machine         = f'pm-cpu'
partition       = f'regular'
conda_env_run   = f'conda run -p /global/homes/w/whannah/.conda/envs/zppy_env'
#---------------------------------------------------------------------------------------------------

# map_file,,dst_grid = os.getenv('HOME')+f'/maps/map_ne30pg2_to_90x180_aave.nc','90x180'
map_file,dst_grid = os.getenv('HOME')+f'/maps/map_ne30pg2_to_180x360_aave.nc','180x360'

# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010-SCREAMv1',          root=scratch_path,yr1='0002',yr2='0006',map_file=map_file)
# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE',         root=scratch_path,yr1='0002',yr2='0006',map_file=map_file)
# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE.L128v3.6',root=scratch_path,yr1='0002',yr2='0006',map_file=map_file)

kwargs = {'root':scratch_path,'yr1':'0002','yr2':'0006','map_file':map_file}
add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP')
add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6')
add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6.phys_order_swap_1')


#---------------------------------------------------------------------------------------------------
# common zppy stuff
data_sub        = 'archive/atm/hist_ne30'
data_sub_native = 'archive/atm/hist'
file_prefix_1ma = 'ne30pg2.1ma.AVERAGE.nmonths_x1'
file_prefix_1da = 'ne30pg2.1da.AVERAGE.nhours_x24'
file_prefix_1ha = 'ne30pg2.1ha.AVERAGE.nhours_x1'
#---------------------------------------------------------------------------------------------------
def main(opts):
    case_root = f"{opts['root']}/{opts['name']}"
    #-----------------------------------------------------------------------------------------------
    # diags_script = 'run_e3sm_diags.py'
    # run_cmd(f'python {diags_script}')
    #-----------------------------------------------------------------------------------------------
    if flags.get('st_archive',False):
        os.chdir(f'{case_root}/case_scripts')
        run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
        run_cmd('./case.st_archive')
    #-----------------------------------------------------------------------------------------------
    if flags.get('clear_zppy_status',False):
        status_files = glob.glob(f'{case_root}/post/scripts/*status')
        for file_name in status_files:
            os.remove(file_name)
    #-----------------------------------------------------------------------------------------------
    if flags.get('check_zppy_status',False):
        status_path = f'{case_root}/post/scripts'
        print(' '*4+clr.END+status_path+clr.END)
        status_files = glob.glob(f'{status_path}/*status')
        max_len = 0
        for file_path in status_files:
            file_name = file_path.replace(f'{status_path}/','')
            max_len = max(len(file_name),max_len)
        for file_path in status_files:
            file_name = file_path.replace(f'{status_path}/','')
            proc = sp.run(['tail',file_path], capture_output=True, text=True, universal_newlines=True)
            msg, err = proc.stdout, proc.stderr
            msg = msg.strip()
            msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
            msg = msg.replace('WAITING',f'{clr.YELLOW}WAITING{clr.END}')
            msg = msg.replace('RUNNING',f'{clr.YELLOW}RUNNING{clr.END}')
            msg = msg.replace('OK',f'{clr.GREEN}OK{clr.END}')
            print(' '*6+f'{clr.CYAN}{file_name:{max_len}}{clr.END} : {msg}')
            if 'ERROR' in msg:
                # print(f'{status_path}/{file_name}')
                file_prefix = file_name.replace('status','')
                tmp_files = glob.glob(f'{status_path}/{file_prefix}*')
                tmp_files.remove(f'{status_path}/{file_name}')
                tmp_files = sorted(tmp_files, key=os.path.getmtime, reverse=True)
                log_file = tmp_files[0]
                log_file_name = log_file#.replace(f'{status_path}/','')
                proc = sp.run(['tail',log_file], capture_output=True, text=True, universal_newlines=True)
                msg, err = proc.stdout, proc.stderr
                msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
                print()
                print(' '*6+f'{clr.CYAN}{log_file_name}{clr.END} : \n')
                print(' '*8+'...')
                for line in msg.split('\n'): print(' '*8+line)
    #-----------------------------------------------------------------------------------------------
    # preliminary check to ensure all file variables are there
    if flags.get('run_zppy_chk',False):
        import netCDF4
        print('  starting pre-zppy file check')
        diag_var_list_list = get_diag_vars(opts)
        file_prefix_list = [ file_prefix_1ma, file_prefix_1da, file_prefix_1ha ]
        if len(diag_var_list_list)!=len(file_prefix_list):
            len_var = len(diag_var_list_list)
            len_pfx = len(file_prefix_list)
            raise ValueError(f'list lengths for var ({len_var}) and prefix ({len_pfx}) lists must match!')
        file_cnt = 0
        for f,file_prefix in enumerate(file_prefix_list):
            diag_var_list = diag_var_list_list[f].split(',')
            test_file_list = sorted(glob.glob(f'{case_root}/{data_sub}/*{file_prefix}*'))
            file_cnt += len(test_file_list)
            if len(test_file_list)==0:
                msg = f'file list is empty!'
                msg += f'\nsearch str: {case_root}/{data_sub}/*{file_prefix}*'
                raise ValueError(msg)
            test_file = test_file_list[0]
            with netCDF4.Dataset(test_file) as ds:
                file_var_list = list(ds.variables)
                for diag_var in diag_var_list:
                    if diag_var not in file_var_list:
                        raise ValueError(f'variable {diag_var} not found in {file_prefix} output stream!')
        print(f'    # file types    : {len(file_prefix_list)} ')
        print(f'    # files present : {file_cnt}')
        print(f'  file check complete!')
    #-----------------------------------------------------------------------------------------------
    if flags.get('run_zppy',False):
        # Clear status files that don't indicate "OK"
        status_files = glob.glob(f'{case_root}/post/scripts/*status')
        for file_name in status_files:
            file_ptr = open(file_name)
            contents = file_ptr.read().split()
            if contents[0]!='OK': os.remove(file_name)

        # dynamically create the zppy config file
        zppy_file_name = f'{case_root}/zppy.cfg'
        # zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
        file = open(zppy_file_name,'w')
        file.write(get_zppy_config(opts))
        file.close()

        print(f'zppy cfg => {zppy_file_name}')

        # submit the zppy job
        # run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
        run_cmd(f'{conda_env_run} zppy -c {zppy_file_name}')
        
#---------------------------------------------------------------------------------------------------
def get_diag_sets(opts):
    diag_set_list = []
    diag_set_list.append('lat_lon'); diag_set_list.append('zonal_mean_xy')
    diag_set_list.append('zonal_mean_2d'); diag_set_list.append('meridional_mean_2d')
    diag_set_list.append('zonal_mean_2d_stratosphere')
    diag_set_list.append('annual_cycle_zonal_mean')
    # diag_set_list.append('lat_lon_native'); # diag_set_list.append('polar')
    # diag_set_list.append('cosp_histogram')
    # diag_set_list.append('enso_diags')
    diag_set_list.append('qbo')
    diag_set_list.append('tropical_subseasonal')
    # diag_set_list.append('tc_analysis')
    # diag_set_list.append('streamflow')
    diag_set_list.append('diurnal_cycle')
    # diag_set_list.append('area_mean_time_series'); # diag_set_list.append('arm_diags')
    # diag_set_list.append('lat_lon_land'); # diag_set_list.append('lat_lon_river')
    # diag_set_list.append('aerosol_aeronet'); # diag_set_list.append('aerosol_budget')
    return (','.join(diag_set_list))
#---------------------------------------------------------------------------------------------------
def get_diag_vars(opts):
    # return "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
    #---------------------------------------------------------------------------
    vars_1ma_list = []
    vars_1ma_list.append('ps')
    # vars_1ma_list.append('surf_radiative_T')
    vars_1ma_list.append('SeaLevelPressure')
    # vars_1ma_list.append('qv_2m')
    vars_1ma_list.append('precip_total_surf_mass_flux')
    vars_1ma_list.append('precip_liq_surf_mass_flux')
    vars_1ma_list.append('precip_ice_surf_mass_flux')
    vars_1ma_list.append('VapWaterPath')
    vars_1ma_list.append('LiqWaterPath')
    vars_1ma_list.append('IceWaterPath')
    vars_1ma_list.append('RainWaterPath')
    # vars_1ma_list.append('omega_at_500hPa')
    # vars_1ma_list.append('omega_at_700hPa')
    # vars_1ma_list.append('omega_at_850hPa')
    # vars_1ma_list.append('T_mid_at_700hPa')
    # vars_1ma_list.append('z_mid_at_700hPa')
    vars_1ma_list.append('T_2m')
    # vars_1ma_list.append('surface_upward_latent_heat_flux')
    vars_1ma_list.append('surf_sens_flux')
    vars_1ma_list.append('surf_evap')
    vars_1ma_list.append('wind_speed_10m')
    # vars_1ma_list.append('U_at_10m_above_surface')
    # vars_1ma_list.append('V_at_10m_above_surface')
    vars_1ma_list.append('SW_flux_up_at_model_top')
    vars_1ma_list.append('SW_flux_dn_at_model_top')
    vars_1ma_list.append('LW_flux_up_at_model_top')
    vars_1ma_list.append('SW_flux_up_at_model_bot')
    vars_1ma_list.append('SW_flux_dn_at_model_bot')
    vars_1ma_list.append('LW_flux_up_at_model_bot')
    vars_1ma_list.append('LW_flux_dn_at_model_bot')
    vars_1ma_list.append('LW_clrsky_flux_up_at_model_top')
    vars_1ma_list.append('SW_clrsky_flux_up_at_model_top')
    vars_1ma_list.append('SW_clrsky_flux_dn_at_model_top')
    vars_1ma_list.append('ShortwaveCloudForcing')
    vars_1ma_list.append('LongwaveCloudForcing')
    vars_1ma_list.append('cldfrac_ice_for_analysis')
    vars_1ma_list.append('cldfrac_tot_for_analysis')
    vars_1ma_list.append('U')
    vars_1ma_list.append('V')
    vars_1ma_list.append('omega')
    vars_1ma_list.append('T_mid')
    vars_1ma_list.append('z_mid')
    vars_1ma_list.append('RelativeHumidity')
    vars_1ma_list.append('qv')
    vars_1ma_list.append('qc')
    vars_1ma_list.append('qi')
    # vars_1ma_list.append('p_mid')
    # vars_1ma_list.append('isccp_cldtot')
    vars_1ma = ','.join(vars_1ma_list)
    #---------------------------------------------------------------------------
    vars_1da_list = []
    vars_1da_list.append('LW_flux_up_at_model_top')
    vars_1da_list.append('precip_total_surf_mass_flux')
    # vars_1da_list.append('precip_liq_surf_mass_flux')
    # vars_1da_list.append('precip_ice_surf_mass_flux')
    vars_1da_list.append('U_at_850hPa')
    vars_1da = ','.join(vars_1da_list)
    #---------------------------------------------------------------------------
    vars_1ha_list = []
    vars_1ha_list.append('precip_total_surf_mass_flux')
    vars_1ha_list.append('precip_liq_surf_mass_flux')
    vars_1ha_list.append('precip_ice_surf_mass_flux')
    vars_1ha_list.append('LW_flux_up_at_model_top')
    vars_1ha_list.append('T_2m')
    vars_1ha_list.append('wind_speed_10m')
    vars_1ha = ','.join(vars_1ha_list)
    #---------------------------------------------------------------------------
    return vars_1ma, vars_1da, vars_1ha
#---------------------------------------------------------------------------------------------------
def get_zppy_config(opts,run_ts=True):
    case_name = opts['name']
    case_root = f"{opts['root']}/{opts['name']}"
    vars_1ma, vars_1da, vars_1ha = get_diag_vars(opts)
    short_name = case_name
    map_file = opts['map_file']
    yr1,yr2, = int(opts['yr1']),int(opts['yr2'])
    nyr = yr2-yr1+1
    ts_nyr = nyr
    # build config file
    config_txt = f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = {html_path}/{case_name}
machine = "{machine}"
partition = {partition}
environment_commands = "source {unified_env}"
# environment_commands = "{conda_env_run}"


[climo]
active = {flags.get('zppy_climo_active',False)}
walltime = "1:00:00"
years = "{yr1}:{yr2}:{nyr}",

  [[ atm_monthly_{dst_grid}_aave ]]
  case = "output"
  input_subdir = "{data_sub}"
  input_files = "{file_prefix_1ma}"
  input_component = "eamxx"
  mapping_file = {map_file}
  grid = {dst_grid}
  frequency = "monthly"
  vars = "{vars_1ma}"

  [[atm_monthly_diurnal_24xdaily_{dst_grid}_aave]]
  active = {flags.get('zppy_climo_diurnal_active',False)}
  case = "output"
  input_files = {file_prefix_1ha}
  input_component = "eamxx"
  input_subdir = archive/atm/hist_ne30
  frequency = diurnal_24xdaily
  mapping_file = {map_file}
  grid = {dst_grid}
  vars = "{vars_1ha}"

[ts]
active = {flags.get('zppy_ts_active',False)}
walltime = "0:30:00"
years = "{yr1}:{yr2}:{ts_nyr}",

  [[ atm_daily_{dst_grid}_aave ]]
  case = "output"
  input_subdir = "{data_sub}"
  input_files = "{file_prefix_1da}"
  input_component = "eamxx"
  mapping_file = "{map_file}"
  grid = "{dst_grid}"
  frequency = "daily"
  vars = "{vars_1da}"

  [[ atm_monthly_{dst_grid}_aave ]]
  case = "output"
  input_subdir = "{data_sub}"
  input_files = "{file_prefix_1ma}"
  input_component = "eamxx"
  mapping_file = {map_file}
  grid = "{dst_grid}"
  frequency = "monthly"
  vars = "{vars_1ma}"
'''
#     config_txt += f'''
#   [[ atm_monthly_glb ]]
#   input_subdir = "{data_sub}"
#   input_files = "{file_prefix_1ma}"
#   mapping_file = "glb"
#   frequency = "monthly"
#   vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
# '''

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
active = {flags.get('zppy_diags_active',False)}
years = "{yr1}:{yr2}:{nyr}",
{(f'ts_num_years = {ts_nyr}' if run_ts else '')}
ref_start_yr = 1979
ref_final_yr = 2016
walltime = "24:00:00"

  [[ atm_monthly_{dst_grid}_aave ]]
  active = {flags.get('zppy_diags_monthly_active',False)}
  # case = "output"
  case = {case_name}
  short_name = '{short_name}'
  grid = '{dst_grid}'
  sets = {get_diag_sets(opts)}
  ts_daily_subsection = "atm_daily_{dst_grid}_aave"
  ts_subsection = "atm_monthly_{dst_grid}_aave" 
  reference_data_path = '{obs_path}/climatology'
  obs_ts = '{obs_path}/time-series'
  climo_diurnal_subsection = atm_monthly_diurnal_24xdaily_{dst_grid}_aave
  climo_diurnal_frequency = diurnal_24xdaily
  dc_obs_climo = '{test_data_path}/climatology/'
  # output_format_subplot = "png"

  [tc_analysis]
  active = {flags.get('zppy_diags_tc_active',False)}
  # case = "output"
  case = {case_name}
  input_files = 3hi
  input_subdir = "{data_sub_native}"
  input_grid = ne256pg2
  tc_vars = "SeaLevelPressure,T_mid_at_200hPa,T_mid_at_500hPa,U_at_model_bot,V_at_model_bot,U_at_850hPa,V_at_850hPa"
  years = {yr1}:{yr2}:{nyr}

'''
#     config_txt += f'''
# '''

#     if run_ts: config_txt += f'''
# [global_time_series]
# active = True
# atmosphere_only = True
# years = "{yr1}-{yr2}", 
# ts_num_years = {ts_nyr}
# figstr = "{short_name}"
# experiment_name = "{case_name}"
# ts_years = "{yr1}-{yr2}",
# climo_years = "{yr1}-{yr2}",

# '''
    return config_txt
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    for n in range(len(opt_list)):
        main( opt_list[n] )

    print_line()
   
#---------------------------------------------------------------------------------------------------