#!/usr/bin/env python
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
''' Ben's decadal run script for reference
/ccs/home/brhillman/codes/scream/cases/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run.decadal-amip.sh
'''
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/2025-DYNAMO-hindcast (master @ 2025-7-7)

# clean        = True
#newcase      = True
#config       = True
#build        = True
submit       = True
continue_run = True


# queue = 'regular'

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,2,'6:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,4,'6:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'6:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',10,0,'6:00:00'

# /lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata/20231226.I2010CRUELM.ne1024pg2_ICOS10.elm.r.1994-10-01-00000.nc

#---------------------------------------------------------------------------------------------------
lnd_init_root = f'/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run'
lnd_init_file = f'{lnd_init_root}/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1.elm.r.1994-11-10-00000.nc'
lnd_data_file = f'/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne1024pg2_simyr2010_c211021.nc'
#---------------------------------------------------------------------------------------------------
# specify initialization date

init_date = datetime.datetime.strptime('2011-11-10 00', '%Y-%m-%d %H')
# init_date = datetime.datetime.strptime('2011-11-15 00', '%Y-%m-%d %H')
# init_date = datetime.datetime.strptime('2011-11-20 00', '%Y-%m-%d %H')
# init_date = datetime.datetime.strptime('2011-11-25 00', '%Y-%m-%d %H')

# init_scratch = '/global/cfs/projectdirs/m4842/whannah/HICCUP'
init_scratch = '/lustre/orion/cli115/proj-shared/hannah6/HICCUP'
init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne1024np4.L128.nc'
# init_file_sst = f'{init_scratch}/HICCUP.sst_noaa.{init_date.strftime("%Y-%m-%d")}.nc'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

# add_case(prefix='2025-DYNAMO-00', compset='F20TR-SCREAMv1', grid='ne1024pg2_ICOS10', num_nodes=1024, init=init_date.strftime('%Y-%m-%d'), rfrac_fix=False )
# add_case(prefix='2025-DYNAMO-00', compset='F20TR-SCREAMv1', grid='ne1024pg2_ICOS10', num_nodes=1024, init=init_date.strftime('%Y-%m-%d'), rfrac_fix=True )

# start over after COSP fix
add_case(prefix='2025-DYNAMO-01', compset='F20TR-SCREAMv1', grid='ne1024pg2_ICOS10', num_nodes=1024, init=init_date.strftime('%Y-%m-%d'), rfrac_fix=False )
# add_case(prefix='2025-DYNAMO-01', compset='F20TR-SCREAMv1', grid='ne1024pg2_ICOS10', num_nodes=1024, init=init_date.strftime('%Y-%m-%d'), rfrac_fix=True )

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'    in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'   in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_'  in opts['grid']: grid_name = 'ne120pg2'
   if 'ne256pg2_'  in opts['grid']: grid_name = 'ne256pg2'
   if 'ne1024pg2_' in opts['grid']: grid_name = 'ne1024pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','grid','init']:
         case_list.append(val)
      # elif key in ['grid']: 
      #    case_list.append(get_grid_name(opts))
      elif key in ['num_nodes','compset']:
         continue
         # case_list.append(f'NN_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #------------------------------------------------------------------------------------------------
   exit()
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']

   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']#+'_'+opts['grid']
   compset = opts['compset']
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
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' --machine=frontier'
      # cmd += f' --compiler=craygnu-hipcc ' # no longer available
      # cmd += f' --compiler=craycray-mphipcc '
      cmd += f' --compiler=craygnu-mphipcc '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
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
      run_cmd('./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      #-------------------------------------------------------------------------
      # thread settings taken from Ben's decadal run script
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_ATM="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_LND="6"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_ICE="6"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_OCN="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_ROF="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_CPL="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_GLC="1"')
      run_cmd('./xmlchange --file env_mach_pes.xml NTHRDS_WAV="1"')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      #-------------------------------------------------------------------------
      if 'rfrac_fix' in opts:
         if opts['rfrac_fix']:
            run_cmd('./atmchange set_cld_frac_r_to_one=true')
         else:
            run_cmd('./atmchange set_cld_frac_r_to_one=false')

      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      # add_hist_file(f'{case_root}/case_scripts/scream_output_2D_10min_inst.yaml',hist_opts_2D_10min_inst)
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_6hr_inst.yaml',        hist_opts_2D_6hr_inst)
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_1hr_avg_ne30pg2.yaml', hist_opts_2D_1hr_avg_ne30pg2)
      add_hist_file(f'{case_root}/case_scripts/scream_output_3D_6hr_avg_ne30pg2.yaml', hist_opts_3D_6hr_avg_ne30pg2)
      
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------------
      # Specify start date and SST file for hindcast
      
      run_cmd(f'./xmlchange CCSM_CO2_PPMV=390.9') # 2011
      run_cmd(f'./atmchange initial_conditions::filename=\"{init_file_atm}\"')
      run_cmd(f'./xmlchange --file env_run.xml  RUN_STARTDATE={init_date.strftime("%Y-%m-%d")}')
      run_cmd(f'./atmchange orbital_year={init_date.strftime("%Y")}')

      # sst_yr = int(init_date.strftime('%Y'))
      # run_cmd(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={init_file_sst}')
      # run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_yr}')
      # run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_yr}')
      # run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={sst_yr+1}')

      # taken from decadal run
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_DATA_FILENAME --val /lustre/orion/cli115/world-shared/e3sm/inputdata/atm/cam/sst/sst_ostia_3600x7200_19940930_20151231_c20240125.nc')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_GRID_FILENAME --val /lustre/orion/cli115/world-shared/e3sm/inputdata/ocn/docn7/domain.ocn.3600x7200.230522.nc')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_ALIGN --val 1994')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_START --val 1994')
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_END --val 2015')
      #-------------------------------------------------------------------------
      file=open('user_nl_elm','w')
      if 'lnd_init_file' in locals():file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      if 'lnd_data_file' in locals():file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      file.close()
      #-------------------------------------------------------------------------
      # Set some run-time stuff
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
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

horiz_remap_file = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne1024pg2_to_ne30pg2_traave.20240206-cdf5.nc'

'''
         - surf_evap
         - surf_mom_flux
         - horiz_winds_at_model_bot
         - SW_flux_dn_at_model_bot
         - SW_flux_up_at_model_bot
         - LW_flux_dn_at_model_bot
         - LW_flux_up_at_model_bot
'''

'''
         - nc
         - nr
         - ni
         - bm
'''

var_list_2D = '''
         - ps
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - U_at_850hPa
         - U_at_200hPa
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
'''
var_list_3D = '''
         - ps
         - omega
         - horiz_winds
         - qv
         - qc
         - qi
         - qr
         - qm
         - RelativeHumidity
         - T_mid
         - z_mid
         - rad_heating_pdel
         - cldfrac_tot_for_analysis
         - cldfrac_liq
         - cldfrac_ice_for_analysis
'''

hist_opts_2D_1hr_avg_ne30pg2 = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr.ne30pg2
averaging_type: average
max_snapshots_per_file: 24
horiz_remap_file: {horiz_remap_file}
fields:
   physics_pg2:
      field_names:{var_list_2D}
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: false
'''

hist_opts_3D_6hr_avg_ne30pg2 = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.6hr.ne30pg2
averaging_type: average
max_snapshots_per_file: 4
horiz_remap_file: {horiz_remap_file}
fields:
   physics_pg2:
      field_names:{var_list_3D}
output_control:
   frequency: 6
   frequency_units: nhours
restart:
   force_new_file: false
'''

# 6-hourly 2D for eye-candy snapshots
hist_opts_2D_6hr_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.6hr
averaging_type: instant
max_snapshots_per_file: 4
fields:
   physics_pg2:
      field_names:
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - U_at_850hPa
         - U_at_200hPa
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
output_control:
   frequency: 6
   frequency_units: nhours
restart:
   force_new_file: false
'''

# 10-min ne1024 output for eye-candy animation
hist_opts_2D_10min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.10min
averaging_type: instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - U_at_850hPa
         - U_at_200hPa
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
output_control:
   frequency: 10
   frequency_units: nmins
restart:
   force_new_file: false
'''




#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
