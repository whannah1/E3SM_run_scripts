#!/usr/bin/env python3
import os, datetime, subprocess as sp
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
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli200'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # master @ Mar 19 2025

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',40,0,'2:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',10,0,'1:00:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'0:30:00'

arch = 'GPU'

native_res = 'ne256pg2'
remap_res  = 'ne30pg2'
hist_map   = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.cdf5.nc'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

compset = 'F2010-SCREAMv1-DYAMOND1'

# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true') # default
# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false')

# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  icmrmax='0.005' ) # default
# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', icmrmax='0.005' )

# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  icmrmax='0.0' )
# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', icmrmax='0.0' )

# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  icmrmax='0.05' )
# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', icmrmax='0.05' )

# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  clfrmin='0.1' )
# add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', clfrmin='0.1' )

add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  icmrmax='0.0005' )
add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', icmrmax='0.0005' )

add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='true',  icmrmax='0.0001' )
add_case(prefix='2025-RAD-MODS-00', compset=compset, grid='ne256pg2', num_nodes=192, subcol='false', icmrmax='0.0001' )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):

   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','grid','compset']:
         case_list.append(val)
      elif key in ['num_nodes']:
         continue
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')

   print(f'\n  case : {case}\n')

   # exit()
   # return

   #------------------------------------------------------------------------------------------------
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   # if arch=='CPU': max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   # if arch=='GPU': max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   if arch=='CPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
   if arch=='GPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']+'_'+opts['grid']
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
      if arch=='CPU': cmd+=f' -mach frontier -compiler crayclang'
      # if arch=='GPU': cmd+=f' -mach frontier-scream-gpu -compiler crayclang-scream'
      if arch=='GPU': cmd+=f' -mach frontier -compiler craycray-mphipcc'
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
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
      # if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
      #-------------------------------------------------------------------------
      if 'subcol' in opts.keys(): run_cmd(f'./atmchange rrtmgp::do_subcol_sampling={opts["subcol"]}')
      #-------------------------------------------------------------------------
      cmake_opts = ''
      # if 'icmrmax' in opts.keys(): cmake_opts += f' -DICMR_MAX={opts["icmrmax"]} '
      # if 'clfrmin' in opts.keys(): cmake_opts += f' -DCLFR_MIN={opts["clfrmin"]} '
      if 'icmrmax' in opts.keys(): cmake_opts += f' ICMR_MAX {opts["icmrmax"]} '
      if 'clfrmin' in opts.keys(): cmake_opts += f' CLFR_MIN {opts["clfrmin"]} '
      if cmake_opts!='':
         run_cmd(f'./xmlchange --append SCREAM_CMAKE_OPTIONS=\" {cmake_opts} \"')
      #-------------------------------------------------------------------------
      # # parameters for addressing popcorn
      # if 'acp' in opts.keys():run_cmd(f'./atmchange autoconversion_prefactor'        +f'={opts["acp"]}')
      # if 'acr' in opts.keys():run_cmd(f'./atmchange autoconversion_radius'           +f'={opts["acr"]}')
      # if 'acq' in opts.keys():run_cmd(f'./atmchange autoconversion_qc_exponent'      +f'={opts["acq"]}')
      # if 'acn' in opts.keys():run_cmd(f'./atmchange autoconversion_nc_exponent'      +f'={opts["acn"]}')
      # if 'acc' in opts.keys():run_cmd(f'./atmchange accretion_prefactor'             +f'={opts["acc"]}')
      # if 'rsc' in opts.keys():run_cmd(f'./atmchange rain_selfcollection_prefactor'   +f'={opts["rsc"]}')
      # if 'eci' in opts.keys():run_cmd(f'./atmchange cldliq_to_ice_collection_factor' +f'={opts["eci"]}')
      # if 'eri' in opts.keys():run_cmd(f'./atmchange rain_to_ice_collection_factor'   +f'={opts["eri"]}')
      # if 'mti' in opts.keys():run_cmd(f'./atmchange max_total_ni'                    +f'={opts["mti"]}')
      # if 'cfl' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_l_to_one'       +f'=true ')
      # if 'cfr' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_r_to_one'       +f'=true ')
      # if 'cfi' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_i_to_one'       +f'=true ')
      # if 'isf' in opts.keys():run_cmd(f'./atmchange p3::ice_sedimentation_factor'    +f'={opts["isf"]}')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
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
      # add_hist_file('scream_output_2D_1hr_inst_native.yaml',hist_opts_2D_1hr_inst)
      # add_hist_file('scream_output_3D_1dy_mean_native.yaml',hist_opts_3D_1dy_mean)
      add_hist_file('scream_output_2D_1dy_mean_remap.yaml',hist_opts_2D_1dy_mean_remap)
      # add_hist_file('scream_output_2D_1hr_inst_remap.yaml', hist_opts_2D_1hr_inst_remap)
      # add_hist_file('scream_output_3D_1dy_mean_remap.yaml', hist_opts_3D_1dy_mean_remap)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      #-----------------------------------------------------------------------------
      if compset == 'F2010-SCREAMv1-DYAMOND1':
         start_date = '2016-08-01'
         start_year = int(start_date.split('-')[0])
         run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={start_date}')
         run_cmd(f'./atmchange orbital_year={start_year}')
      #-------------------------------------------------------------------------
      # if init_file is not None: 
      #    run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
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
      run_cmd(f'./case.submit -a=" -x frontier08656 " ')
      # run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
field_txt_2D = '''
      - ps
      - precip_total_surf_mass_flux
      - VapWaterPath
      - LiqWaterPath
      - IceWaterPath
      - surf_sens_flux
      - surf_evap
      - surface_upward_latent_heat_flux
      - surf_mom_flux
      - wind_speed_10m
      - horiz_winds_at_model_bot
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
'''



field_txt_3D = '''
      - ps
      - omega
      - horiz_winds
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
'''

# the P3 process tendency fields were not available in this branch
# P3_qr2qv_evap

hist_opts_2D_1hr_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr.{native_res}
Averaging Type: Instant
Max Snapshots Per File: 24
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: nhours
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

hist_opts_2D_1hr_inst_remap = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr.{remap_res}
Averaging Type: Instant
Max Snapshots Per File: 24
horiz_remap_file: {hist_map}
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: nhours
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

hist_opts_2D_1dy_mean_remap = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1dy.{remap_res}
Averaging Type: Average
Max Snapshots Per File: 1
horiz_remap_file: {hist_map}
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

hist_opts_3D_1dy_mean = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.1dy.{native_res}
Averaging Type: Average
Max Snapshots Per File: 1
Fields:
   Physics PG2:
      Field Names:{field_txt_3D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''



hist_opts_3D_1dy_mean_remap = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.1dy.{remap_res}
Averaging Type: Average
Max Snapshots Per File: 1
horiz_remap_file: {hist_map}
Fields:
   Physics PG2:
      Field Names:{field_txt_3D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
