#!/usr/bin/env python3
import os, subprocess as sp, glob, datetime, sys
#---------------------------------------------------------------------------------------------------
'''
NE=256; SRC_GRID=ne${NE}pg2
DST_NY=180; DST_NX=360
DST_GRID=${DST_NY}x${DST_NX}

GRID_ROOT=/lustre/orion/cli115/proj-shared/hannah6/files_grid
MAPS_ROOT=/lustre/orion/cli115/proj-shared/hannah6/files_map

SRC_GRID_FILE=${GRID_ROOT}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_ROOT}/${DST_GRID}_scrip.nc
MAP_FILE=${MAPS_ROOT}/map_${SRC_GRID}_to_${DST_GRID}_traave.nc

# generate model grid file
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc

# generate lat/lon grid file
ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst

# generate map file
ncremap -6 --alg_typ=traave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

'''
#---------------------------------------------------------------------------------------------------
''' Moving history files after short-term archive step

ROOT=/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch
# CASE=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP
CASE=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6
# CASE=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6.phys_order_swap_1

mkdir -p ${ROOT}/${CASE}/archive/atm/hist
mkdir -p ${ROOT}/${CASE}/archive/atm/hist_ne30
mkdir -p ${ROOT}/${CASE}/archive/rest/rhist
mv  ${ROOT}/${CASE}/run/*rhist*          ${ROOT}/${CASE}/archive/rest/rhist/
mv  ${ROOT}/${CASE}/run/output.ne30pg2*  ${ROOT}/${CASE}/archive/atm/hist_ne30/
mv  ${ROOT}/${CASE}/run/output.*         ${ROOT}/${CASE}/archive/atm/hist/

mkdir -p ${ROOT}/${CASE}/archive/atm/yr0001
mv  ${ROOT}/${CASE}/archive/atm/hist*/*.0001-*  ${ROOT}/${CASE}/archive/atm/yr0001/

#-------------------------------------------------------------------------------

ROOT=/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch
MAP_FILE=~/maps/map_ne30pg2_to_90x180_traave.nc
REGRID_ARGS="--map=${MAP_FILE} --root=${ROOT} --sub=archive/atm/hist_ne30 --prefix=output.ne30pg2.1da.AVERAGE.nhours_x24"

python ~/E3SM_analysis/regrid.eamxx.py ${REGRID_ARGS} --case=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP
python ~/E3SM_analysis/regrid.eamxx.py ${REGRID_ARGS} --case=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6
python ~/E3SM_analysis/regrid.eamxx.py ${REGRID_ARGS} --case=E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6.phys_order_swap_1

'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line(): print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
st_archive, clear_zppy_status, check_zppy_status, run_zppy_chk, run_zppy = False, False, False, False, False
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
# run_zppy_chk      = True
# run_zppy          = True

zppy_climo_active    = False
zppy_ts_active       = True
zppy_diags_active    = True
#---------------------------------------------------------------------------------------------------
# # NERSC
# acct = 'e3sm'
# username = 'whannah'
# unified_env     = f'/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh'
# obs_path        = f'/lcrc/group/e3sm/diagnostics/observations/Atm/'
# test_data_path  = f'/lcrc/soft/climate/e3sm_diags_data/test_model_data_for_acme_diags/'
# html_path       = f'/lcrc/group/e3sm/public_html/diagnostic_output/{username}/'
# web_address     = f'https://web.lcrc.anl.gov/public/e3sm/diagnostic_output/{username}/'
#---------------------------------------------------------------------------------------------------
# OLCF
acct = 'cli115'
username = 'hannah6'
unified_env     = f'/ccs/proj/cli115/software/e3sm-unified/load_latest_e3sm_unified_andes.sh'
obs_path        = f'/ccs/proj/cli115/e3sm_diags/obs_for_e3sm_diags'
test_data_path  = f'???/test_model_data_for_acme_diags/'
html_path       = f'???/public_html/diagnostic_output/{username}/'
web_address     = f'https://???/public/e3sm/diagnostic_output/{username}/'
#---------------------------------------------------------------------------------------------------

scratch_path='/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch'
map_file = '/lustre/orion/cli115/proj-shared/hannah6/files_map/map_ne256pg2_to_180x360_traave.nc'

# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010-SCREAMv1',          root=scratch_path,yr1='0001',yr2='0005',map_file=map_file)
# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE',         root=scratch_path,yr1='0001',yr2='0005',map_file=map_file)
# add_case(name='E3SM.2026-ZM-BASE-00.ne256pg2.NN_128.F2010xx-ZM-CICE.L128v3.6',root=scratch_path,yr1='0001',yr2='0005',map_file=map_file)

kwargs = {'root':scratch_path,'yr1':'0001','yr2':'0005','map_file':map_file}
# add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP')
add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6')
# add_case(**kwargs,name='E3SM.2026-ZM-BASE-01.ne256pg2.NN_256.F2010xx-ZM-CICE.COSP.L128v3.6.phys_order_swap_1')

#---------------------------------------------------------------------------------------------------
# common zppy stuff
data_sub = 'archive/atm/hist'
file_prefix_1ma = 'monthly.AVERAGE.nmonths_x1'
file_prefix_1da = 'daily.AVERAGE.nhours_x24'
# dst_grid = '90x180'
dst_grid = '180x360'
#---------------------------------------------------------------------------------------------------
def main(opts):
    case_root = f"{opts['root']}/{opts['name']}"
    #-----------------------------------------------------------------------------------------------
    # diags_script = 'run_e3sm_diags.py'
    # run_cmd(f'python {diags_script}')
    #-----------------------------------------------------------------------------------------------
    if st_archive:
        os.chdir(f'{case_root}/case_scripts')
        run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
        run_cmd('./case.st_archive')
    #-----------------------------------------------------------------------------------------------
    if clear_zppy_status:
        status_files = glob.glob(f'{case_root}/post/scripts/*status')
        for file_name in status_files:
            os.remove(file_name)
    #-----------------------------------------------------------------------------------------------
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
                log_file_name = log_file.replace(f'{status_path}/','')
                proc = sp.run(['tail',log_file], capture_output=True, text=True, universal_newlines=True)
                msg, err = proc.stdout, proc.stderr
                msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
                print(' '*6+f'{clr.CYAN}{log_file_name}{clr.END} : \n')
                print(' '*8+'...')
                for line in msg.split('\n'): print(' '*8+line)
    #-----------------------------------------------------------------------------------------------
    # preliminary check to ensure all file variables are there
    if run_zppy_chk:
        import netCDF4
        diag_var_list_list = get_diag_vars(opts)
        file_prefix_list = [ file_prefix_1ma, file_prefix_1da ]
        if len(diag_var_list_list)!=len(file_prefix_list): raise ValueError('var and prefix list lengths must match!')
        for f,file_prefix in enumerate(file_prefix_list):
            diag_var_list = diag_var_list_list[f].split(',')
            test_file = sorted(glob.glob(f'{case_root}/{data_sub}/*{file_prefix}*'))[0]
            with netCDF4.Dataset(test_file) as ds:
                file_var_list = list(ds.variables)
                for diag_var in diag_var_list:
                    if diag_var not in file_var_list:
                        raise ValueError(f'variable {diag_var} not found in {file_prefix} output stream!')
    #-----------------------------------------------------------------------------------------------
    if run_zppy:
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

        print(f'  zppy cfg => {zppy_file_name}')

        # submit the zppy job
        run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
#---------------------------------------------------------------------------------------------------
def get_diag_sets(opts):
    diag_set_list = []
    diag_set_list.append('lat_lon'); diag_set_list.append('zonal_mean_xy')
    diag_set_list.append('zonal_mean_2d'); diag_set_list.append('meridional_mean_2d')
    diag_set_list.append('zonal_mean_2d_stratosphere')
    # diag_set_list.append('lat_lon_native'); # diag_set_list.append('polar')
    # diag_set_list.append('cosp_histogram')
    # diag_set_list.append('enso_diags')
    diag_set_list.append('qbo')
    diag_set_list.append('tropical_subseasonal')
    # diag_set_list.append('tc_analysis')
    # diag_set_list.append('streamflow')
    # diag_set_list.append('diurnal_cycle')
    # diag_set_list.append('annual_cycle_zonal_mean')
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
    # vars_1ma_list.append('precip_liq_surf_mass_flux')
    # vars_1ma_list.append('precip_ice_surf_mass_flux')
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
    # vars_1ma_list.append('surf_sens_flux')
    # vars_1ma_list.append('surf_evap')
    vars_1ma_list.append('wind_speed_10m')
    # vars_1ma_list.append('U_at_10m_above_surface')
    # vars_1ma_list.append('V_at_10m_above_surface')
    vars_1ma_list.append('SW_flux_up_at_model_top')
    vars_1ma_list.append('SW_flux_dn_at_model_top')
    vars_1ma_list.append('LW_flux_up_at_model_top')
    # vars_1ma_list.append('SW_flux_up_at_model_bot')
    # vars_1ma_list.append('SW_flux_dn_at_model_bot')
    # vars_1ma_list.append('LW_flux_up_at_model_bot')
    # vars_1ma_list.append('LW_flux_dn_at_model_bot')
    vars_1ma_list.append('LW_clrsky_flux_up_at_model_top')
    vars_1ma_list.append('SW_clrsky_flux_up_at_model_top')
    vars_1ma_list.append('SW_clrsky_flux_dn_at_model_top')
    # vars_1ma_list.append('ShortwaveCloudForcing')
    # vars_1ma_list.append('LongwaveCloudForcing')
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
    return vars_1ma, vars_1da
#---------------------------------------------------------------------------------------------------
def get_zppy_config(opts,run_ts=True):
    case_name = opts['name']
    case_root = f"{opts['root']}/{opts['name']}"
    vars_1ma, vars_1da = get_diag_vars(opts)
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
# www = {html_path}
machine = "chrysalis"
partition = compute
environment_commands = "source {unified_env}"

[climo]
active = {zppy_climo_active}
walltime = "1:00:00"
years = "{yr1}:{yr2}:{nyr}",

  [[ atm_monthly_{dst_grid}_aave ]]
  case = "output"
  input_subdir = "{data_sub}"
  input_files = "{file_prefix_1ma}"
  input_component = "eamxx"
  mapping_file = "{map_file}"
  grid = "{dst_grid}"
  frequency = "monthly"
  vars = "{vars_1ma}"

[ts]
active = {zppy_ts_active}
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
active = {zppy_diags_active}
years = "{yr1}:{yr2}:{nyr}",
{(f'ts_num_years = {ts_nyr}' if run_ts else '')}
ref_start_yr = 1979
ref_final_yr = 2016
walltime = "24:00:00"

  [[ atm_monthly_{dst_grid}_aave ]]
  short_name = '{short_name}'
  grid = '{dst_grid}'
  sets = {get_diag_sets(opts)}
  ts_daily_subsection = "atm_daily_{dst_grid}_aave"
  ts_subsection = "atm_monthly_{dst_grid}_aave" 
  reference_data_path = '{obs_path}/climatology'
  obs_ts = '{obs_path}/time-series'
  # dc_obs_climo = '{test_data_path}/climatology/'
  # output_format_subplot = "png"

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