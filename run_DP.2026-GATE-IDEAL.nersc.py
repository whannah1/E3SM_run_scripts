#!/usr/bin/env python
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
# https://github.com/E3SM-Project/scmlib/blob/master/DPxx_SCREAM_SCRIPTS/run_dpxx_scream_RCE.csh
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
def xmlquery(xmlvar):
   ( value, err) = sp.Popen(f'./xmlquery {xmlvar} --value', stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   return value
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' commands to regird initial condition
SRC_FILE=/global/cfs/cdirs/e3sm/inputdata/atm/scream/init/screami_ne30np4L128_20221004.nc
DST_FILE=/global/homes/w/whannah/E3SM_grid_support/2026-INCITE-CONUS-RRM/screami_ne30np4L128_20221004.L144.nc
DST_VERT=/global/homes/w/whannah/E3SM_grid_support/2026-INCITE-CONUS-RRM/2026-INCITE-CONUS-RRM_L144_v1_c20251211.nc
ncremap --ps_nm=ps --vrt_fl=${DST_VERT} --in_fl=${SRC_FILE} --out_fl=${DST_FILE} --fl_fmt=64bit_data
'''
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

# acct = 'e3sm'
acct = 'm4310' # switching to this since e3sm hours are too low and scidac hours are too high
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # master @ Sep 24 2025

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

# queue,stop_opt,stop_n,resub,walltime = 'debug','ndays',1,0,'0:30:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'4:00:00'
queue,stop_opt,stop_n,resub,walltime = 'regular','nhours',4,6-1,'12:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',6,0,'12:00:00'

compset = 'FIOP-SCREAMv1-DP'

horiz_remap_root = '/global/homes/w/whannah/maps'

vgrid_L128 = '/global/cfs/cdirs/e3sm/inputdata/atm/scream/init/vertical_coordinates_L128_20220927.nc'
vgrid_L144 = '/global/homes/w/whannah/E3SM_grid_support/2026-INCITE-CONUS-RRM/2026-INCITE-CONUS-RRM_L144_v1_c20251211.nc'

init_L128 = '/global/cfs/cdirs/e3sm/inputdata/atm/scream/init/screami_ne30np4L128_20221004.nc'
init_L144 = '/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/screami_ne30np4L128_20221004.L144.nc'
#---------------------------------------------------------------------------------------------------
# build list of cases to run

# # 3km
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=4,ne=67,lx=600,dt=60,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  4.5 /  3.0km (ne1024)
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=4,ne=67,lx=600,dt=60,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  4.5 /  3.0km (ne1024)

# 1km
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=8,ne=200,lx=600,dt=20,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  1.5 /  1.0km
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=8,ne=200,lx=600,dt=20,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  1.5 /  1.0km

# NOTE - the current runs are an attempt to set tom_sponge_start to fix the instability

# # 15 sec is unstable - but 128 nodes seems to work
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=128,ne=1000,lx=600,dt=15,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  dx_dyn ~ 200m
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=128,ne=1000,lx=600,dt=15,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  dx_dyn ~ 200m

# 4 sec timestep is consistent with the 3km/ne67 runs
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=128,ne=1000,lx=600,dt=4,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  dx_dyn ~ 200m
# add_case(prefix='2026-GATE-IDEAL-00',num_nodes=128,ne=1000,lx=600,dt=4,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  dx_dyn ~ 200m

# add_case(prefix='2026-GATE-IDEAL-00', num_nodes=1, ne=44, lx=600, dt=60 ) #  9.0 /  6.0km ( ne512)
# add_case(prefix='2026-GATE-IDEAL-00', num_nodes=1, ne=22, lx=600, dt=60 ) # 18.2 / 12.1km ( ne256)
# add_case(prefix='2026-GATE-IDEAL-00', num_nodes=1, ne=11, lx=600, dt=60 ) # 36.4 / 24.2km ( ne256)
# add_case(prefix='2026-GATE-IDEAL-00', num_nodes=1, ne=5,  lx=600, dt=60 ) # 36.4 / 24.2km ( ne256)

# start a new group with smaller domain size to get down to smaller dx

# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=  1,ne= 22,lx=200,dt=60,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  4.5 /  3.0km (ne1024)
# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=  1,ne= 22,lx=200,dt=60,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  4.5 /  3.0km (ne1024)
# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=  8,ne= 66,lx=200,dt=20,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  1.5 /  1.0km
# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=  8,ne= 66,lx=200,dt=20,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  1.5 /  1.0km

# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=128,ne=333,lx=200,dt= 4,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  dx_dyn ~ 200m
# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=128,ne=333,lx=200,dt= 4,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  dx_dyn ~ 200m

add_case(prefix='2026-GATE-IDEAL-01',num_nodes=256,ne=333,lx=200,dt= 4,vgrid_name='L128',vgrid_file=vgrid_L128,vgrid_nlev=128,init_file=init_L128) #  dx_dyn ~ 200m
# add_case(prefix='2026-GATE-IDEAL-01',num_nodes=256,ne=333,lx=200,dt= 4,vgrid_name='L144',vgrid_file=vgrid_L144,vgrid_nlev=144,init_file=init_L144) #  dx_dyn ~ 200m

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   #----------------------------------------------------------------------------
   # required arguments
   domain_len  = int( opts['lx'] * 1e3 )
   num_nodes   = opts['num_nodes']
   ne          = opts['ne']
   dtime       = opts['dt']
   #----------------------------------------------------------------------------
   # calculate nu_top based on scaling ne1024 default
   ne1024_dx = 360*111e3/(1024*4*3)
   approx_dx = int( domain_len / (ne*3.0) )
   nu_top    = 1e4*(approx_dx/ne1024_dx)
   #----------------------------------------------------------------------------
   # print(); print(f'approx_dx: {approx_dx}')
   # print(f'nu_top   : {nu_top}')
   # return
   #----------------------------------------------------------------------------
   vgrid_name = opts['vgrid_name']
   vgrid_file = opts['vgrid_file']
   vgrid_nlev = opts['vgrid_nlev']
   init_file  = opts['init_file']
   #print(f'init_file: {init_file}')
   #exit()
   #----------------------------------------------------------------------------
   # optional arguments that still need a value
   arch        = 'GPU'
   enable_zm   = False
   if 'enable_zm' in opts: enable_zm = opts['enable_zm']
   if 'arch'      in opts: arch      = opts['arch']
   #----------------------------------------------------------------------------
   case_list = ['DP']
   for key,val in opts.items(): 
      if   key in ['prefix','compset']:case_list.append(val)
      elif key in ['vgrid_file']:      continue
      elif key in ['vgrid_nlev']:      continue
      elif key in ['init_file']:       continue
      elif key in ['vgrid_name']:      case_list.append(f'{val}')
      elif key in ['grid']:            case_list.append(val.split('_')[0])
      elif key in ['num_nodes']:       case_list.append(f'NN_{val:02}')
      elif key in ['ne']:              case_list.append(f'ne{val}')
      elif key in ['lx']:              case_list.append(f'lx_{(int(val))}km')
      elif key in ['debug']:           case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # exit()
   # return
   #----------------------------------------------------------------------------
   #----------------------------------------------------------------------------
   horiz_remap_file_1D = f'{horiz_remap_root}/map_dpxx_x{domain_len}m_y{domain_len}m_nex{ne}_ney{ne}_to_1x1.nc'
   if not os.path.exists(horiz_remap_file_1D): raise OSError(f'horiz_remap_file is missing: {horiz_remap_file_1D}')
   opts['horiz_remap_file_1D'] = horiz_remap_file_1D
   #----------------------------------------------------------------------------
   if arch=='GPU': max_mpi_per_node,atm_nthrds =   4,1
   if arch=='CPU': max_mpi_per_node,atm_nthrds = 128,1
   atm_ntasks = max_mpi_per_node*num_nodes
   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   # limit tasks to number of dycor elements
   if arch=='CPU' and (ne*ne)<atm_ntasks: atm_ntasks = ne*ne
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res ne30pg2_ne30pg2 '
      cmd += f' --project {acct} '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
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
      run_cmd(f'./xmlchange RUN_STARTDATE="1974-08-30",START_TOD="0"')
      run_cmd(f'./xmlchange PTS_MULTCOLS_MODE="TRUE",PTS_MODE="TRUE",PTS_LAT="0.0",PTS_LON="0.0"')
      #-------------------------------------------------------------------------
      num_col = ne*ne*4 # number of columns needed for component model initialization
      # run_cmd(f'./xmlchange MASK_GRID="USGS",PTS_NX="{num_col}",PTS_NY=1')
      run_cmd(f'./xmlchange PTS_NX="{num_col}",PTS_NY=1')
      run_cmd(f'./xmlchange ICE_NX="{num_col}",ICE_NY=1')
      # run_cmd(f'./xmlchange CALENDAR="GREGORIAN"')
      # run_cmd(f'./xmlchange PIO_TYPENAME="netcdf"')
      #-------------------------------------------------------------------------
      din_loc_root = xmlquery('DIN_LOC_ROOT')
      #-------------------------------------------------------------------------
      # change vertical levels
      run_cmd(f'./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NUM_VERTICAL_LEV {vgrid_nlev} SCREAM_NP 4 SCREAM_NUM_TRACERS 10"')
      #-------------------------------------------------------------------------
      if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
      #---------------------------------------------------------------------------------------------------
      # Case specific information
      run_cmd(f'./atmchange -b target_latitude=9.0 ')
      run_cmd(f'./atmchange -b target_longitude=336.0 ')
      run_cmd(f'./atmchange -b se_ne_x={ne} ')
      run_cmd(f'./atmchange -b se_ne_y={ne} ')
      run_cmd(f'./atmchange -b se_lx={domain_len} ')
      run_cmd(f'./atmchange -b se_ly={domain_len} ')
      run_cmd(f'./atmchange -b cubed_sphere_map=2 ')
      run_cmd(f'./atmchange -b iop_file={din_loc_root}/atm/cam/scam/iop/GATEIDEAL_iopfile_4scam_extended.nc ')
      run_cmd(f'./atmchange -b nu=0.216784 ')
      run_cmd(f'./atmchange -b nu_top={nu_top} ')
      # if opts['ne']== 67: run_cmd(f'./atmchange -b nu_top=1e4 ') # default
      # if opts['ne']==200: run_cmd(f'./atmchange -b nu_top=3333 ')
      run_cmd(f'./atmchange -b se_ftype=2 ')
      run_cmd(f'./atmchange -b dt_remap_factor=1 ')
      run_cmd(f'./atmchange -b se_tstep={(dtime/6)} ')
      # dp_cpl_tight = False
      # if dp_cpl_tight:
      #    run_cmd(f'./atmchange se_tstep={dtime} ')
      #    run_cmd(f'./atmchange dt_remap_factor=1 ')
      #    run_cmd(f'./atmchange dt_tracer_factor=1 ')
      #    run_cmd(f'./atmchange hypervis_subcycle_q=1 ')
      # else:
      #    run_cmd(f'./atmchange dt_remap_factor=1 ')
      #    run_cmd(f'./atmchange se_tstep={(dtime/6)} ')
      run_cmd(f'./atmchange -b rad_frequency=1 ')
      run_cmd(f'./atmchange -b iop_srf_prop=false ')
      run_cmd(f'./atmchange -b iop_nudge_uv=true ')
      run_cmd(f'./atmchange -b iop_nudge_tq=false ')
      run_cmd(f'./atmchange -b iop_coriolis=false ')
      run_cmd(f'./atmchange -b iop_dosubsidence=false ')
      # # Allow for the computation of tendencies for output purposes
      # run_cmd(f'./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd(f'./atmchange homme::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      # if enable_zm:
      #    run_cmd('./atmchange physics::atm_procs_list=iop_forcing,zm,mac_aero_mic,rrtmgp')
      #    run_cmd('./atmchange physics::zm::apply_tendencies=true')
      #    run_cmd(f'./atmchange physics::zm::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      # Allow for the computation of tendencies for output purposes
      run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
      run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
      run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      run_cmd(f'./atmchange -b vertical_coordinate_filename={vgrid_file} ')
      #-------------------------------------------------------------------------
      # p3_eci => cldliq_to_ice_collection_factor
      # p3_eri => rain_to_ice_collection_factor
   #------------------------------------------------------------------------------------------------
   if build : 
      if 'debug' in opts:
         if opts['debug']: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('scream_output_1D_1hr_mean.yaml',get_hist_opts_1D_1hr(opts))
      add_hist_file('scream_output_2D_1hr_mean.yaml',get_hist_opts_2D_1hr(opts))
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      if init_file is not None: 
         run_cmd(f'./atmchange initial_conditions::filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      # write_atm_namelist(ne,domain_len,dtime)
      #-------------------------------------------------------------------------
      # run_cmd(f'./atmchange -b homme::tom_sponge_start=')
      #-------------------------------------------------------------------------
      # avoid writing monthly cice file
      file = open('user_nl_cice','w') 
      file.write(f"histfreq='y','x','x','x','x' \n")
      file.close()

      do_turnoff_swrad = True
      constant_zenith_deg = 180 if do_turnoff_swrad else -1

      file = open('user_nl_cpl','w') 
      file.write(f' constant_zenith_deg = {constant_zenith_deg} \n')
      file.write(f' ocn_surface_flux_scheme = 2 \n')
      file.close()

      # ELM output is temporarily broken for DP-SCREAM so turn it off
      file = open('user_nl_elm','w') 
      file.write(f"hist_empty_htapes = .true. \n")
      file.close()

      #-------------------------------------------------------------------------
      # Set some run-time stuff
      run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
default_field_txt_2D = '''
      - ps
      - precip_total_surf_mass_flux
      - VapWaterPath
      - LiqWaterPath
      - RainWaterPath
      - IceWaterPath
      - surf_sens_flux
      - surf_evap
      - surface_upward_latent_heat_flux
      - surf_mom_flux
      - wind_speed_10m
      - horiz_winds_at_model_bot
      - SW_flux_dn_at_model_bot
      - SW_flux_up_at_model_bot
      - LW_flux_dn_at_model_bot
      - LW_flux_up_at_model_bot
      - SW_flux_up_at_model_top
      - SW_flux_dn_at_model_top
      - LW_flux_up_at_model_top
'''
# field_txt_3D = '''
#       - ps
#       - omega
#       - horiz_winds
#       - qv
#       - qc
#       - qr
#       - qi
#       - qm
#       - nc
#       - nr
#       - ni
#       - bm
#       - T_mid
#       - z_mid
#       - RelativeHumidity
#       - rad_heating_pdel
#       - P3_qr2qv_evap
# '''

default_field_txt_1D = '''
      - ps
      - omega
      - U
      - V
      - qv
      - qc
      - qr
      - qi
      - qm
      - nc
      - nr
      - ni
      - bm
      - T_mid
      - z_mid
      - RelativeHumidity
      - rad_heating_pdel
      - cldfrac_tot_for_analysis
      - cldfrac_liq
      - cldfrac_ice_for_analysis
'''

def get_field_txt_2D(opts):
   # enable_zm = False
   # if 'enable_zm' in opts: enable_zm = opts['enable_zm']
   field_txt_2D = default_field_txt_2D
   # if enable_zm: field_txt_2D+='      - zm_prec \n'
   return field_txt_2D

def get_field_txt_1D(opts):
   # enable_zm = False
   # if 'enable_zm' in opts: enable_zm = opts['enable_zm']
   field_txt_1D = default_field_txt_1D
   field_txt_1D+='      - p3_T_mid_tend \n'
   field_txt_1D+='      - shoc_T_mid_tend \n'
   field_txt_1D+='      - rrtmgp_T_mid_tend \n'
   field_txt_1D+='      - homme_T_mid_tend \n'
   field_txt_1D+='      - p3_qv_tend \n'
   field_txt_1D+='      - shoc_qv_tend \n'
   field_txt_1D+='      - homme_qv_tend \n'
   # field_txt_1D+='      - shoc_horiz_winds_tend \n'
   # field_txt_1D+='      - homme_horiz_winds_tend \n'
   # if enable_zm: 
   #    field_txt_1D+='      - zm_T_mid_tend \n'
   #    field_txt_1D+='      - zm_qv_tend \n'
   #    # field_txt_1D+='      - zm_u_tend \n'
   #    # field_txt_1D+='      - zm_v_tend \n'
   return field_txt_1D

def get_hist_opts_2D_1hr(opts):
   return f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
averaging_type: Average
max_snapshots_per_file: 24
fields:
   physics_pg2:
      field_names:{get_field_txt_2D(opts)}
output_control:
   frequency: 1
   frequency_units: nhours
Restart:
   force_new_file: false
'''

def get_hist_opts_1D_1hr(opts):
   horiz_remap_file = opts['horiz_remap_file_1D']
   return f'''
%YAML 1.1
---
filename_prefix: output.scream.1D.1hr
averaging_type: average
max_snapshots_per_file: 24
horiz_remap_file: {horiz_remap_file}
fields:
   physics_pg2:
      field_names:{get_field_txt_1D(opts)}
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: false
'''

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)): main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
