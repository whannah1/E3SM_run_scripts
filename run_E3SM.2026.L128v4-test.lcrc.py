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
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC1' # branch => whannah/eamxx/support-new-L128

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# stop_opt,stop_n,resub,walltime = 'nsteps',18,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,4,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'3:00:00'

#---------------------------------------------------------------------------------------------------

kwargs = {'prefix':'2026-L128-TEST-00'}

# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=1,   grid='ne4pg2_ne4pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=2,   grid='ne30pg2_ne30pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=2,   grid='ne32pg2_ne32pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=4,   grid='ne64pg2_ne64pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=16,  grid='ne120pg2_ne120pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=16,  grid='ne128pg2_ne128pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=64,  grid='ne256pg2_ne256pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=256, grid='ne512pg2_ne512pg2')
# add_case(**kwargs, compset='F2010-SCREAMv1', num_nodes=512, grid='ne1024pg2_ne1024pg2')

# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=1,   grid='ne4pg2_ne4pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne30pg2_ne30pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=4,   grid='ne64pg2_ne64pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=16,  grid='ne120pg2_ne120pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=16,  grid='ne128pg2_ne128pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=64,  grid='ne256pg2_ne256pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=256, grid='ne512pg2_ne512pg2')
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=512, grid='ne1024pg2_ne1024pg2')

# add_case(**kwargs, compset='F2010-SCREAMv1',  num_nodes=4,   grid='ne64pg2_ne64pg2', old_L128=True)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=4,   grid='ne64pg2_ne64pg2', old_L128=True)

# add_case(**kwargs, compset='F2010-SCREAMv1',  num_nodes=8,   grid='ne64pg2_ne64pg2', old_L128=True)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=8,   grid='ne64pg2_ne64pg2', old_L128=True)


# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', imp_flux=True)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', cape_thr=100)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', mcsp_on=False)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', zmtau=7200)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', remap_fac=1)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', alt_init=True)

# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', dt_rcp=1) # lower dt_dyn
add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', dt_rcp=2) # lower dt_dyn
add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', dt_rcp=3) # lower dt_dyn

# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', length_fac=2.0)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', length_fac=1.0)
# add_case(**kwargs, compset='F2010xx-ZM-CICE', num_nodes=2,   grid='ne32pg2_ne32pg2', length_fac=0.25)

# retest long-term stability with new IC files from ERA5
# add_case(prefix='2026-L128-TEST-01', compset='F2010xx-ZM-CICE', num_nodes=4, grid='ne32pg2_ne32pg2', ic='old')
# add_case(prefix='2026-L128-TEST-01', compset='F2010xx-ZM-CICE', num_nodes=4, grid='ne32pg2_ne32pg2', ic='new')
# add_case(prefix='2026-L128-TEST-01', compset='F2010xx-ZM-CICE', num_nodes=4, grid='ne32pg2_ne32pg2', ic='new', remap_fac=1)

# add_case(prefix='2026-L128-TEST-01', compset='F2010xx-ZM', num_nodes=16, grid='ne32pg2_r025_RRSwISC6to18E3r5', ic='new', remap_fac=2)

# add_case(prefix='2026-L128-TEST-01', compset='F2010xx-ZM-CICE', num_nodes=64, grid='ne128pg2_ne128pg2', ic='new')

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','grid']: case_list.append(val)
      elif key in ['debug']:        continue
      elif key in ['num_nodes']:    case_list.append(f'NN_{val}')
      elif key in ['num_tasks']:    case_list.append(f'NT_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if opts.get('debug',False): case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
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
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   debug_mode = opts.get('debug', False)
   #------------------------------------------------------------------------------------------------
   case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'
   DIN_LOC_ROOT = '/lcrc/group/e3sm/data/inputdata'
   machine,compiler = 'chrysalis','intel'
   if 'num_nodes' in opts:
      num_nodes = opts['num_nodes']
      max_mpi_per_node,atm_nthrds = 64,1 ; max_task_per_node = 64
      atm_ntasks = max_mpi_per_node*num_nodes
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
      cmd += f' --pecount {atm_ntasks}x1 --machine={machine} --compiler={compiler} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      if opts.get('imp_flux'):
         run_cmd('./xmlchange ATM_FLUX_INTEGRATION_METHOD=implicit_stress')
         run_cmd('./xmlchange ATM_SUPPLIES_GUSTINESS=TRUE')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      # run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      # use updated SPA data file
      run_cmd(f'./atmchange -b spa_data_file="{DIN_LOC_ROOT}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      # splitform
      run_cmd(f'./atmchange -b theta_advect_form=2 ')
      run_cmd(f'./atmchange -b pgrad_correction=0 ')

      if opts.get('cape_thr'): run_cmd(f'./atmchange -b cape_threshold={opts.get("cape_thr")} ')
      if 'mcsp_on' in opts:
         if opts.get('mcsp_on'):
            run_cmd(f'./atmchange -b mcsp_enabled=true')
         else:
            run_cmd(f'./atmchange -b mcsp_enabled=false')
      if opts.get('zmtau'): run_cmd(f'./atmchange -b zm::tau={opts.get("zmtau")} ')

      if opts.get('length_fac'): run_cmd(f'./atmchange -b shoc::length_fac={opts.get("length_fac")} ')

      if opts.get('remap_fac'): run_cmd(f'./atmchange -b dt_remap_factor={opts.get("remap_fac")} ')

      #-------------------------------------------------------------------------
      # /lcrc/group/e3sm/data/inputdata/atm/scream/init/vertical_coordinates_L128v4_c20260820.nc
      # /lcrc/group/e3sm/data/inputdata/atm/scream/init/eamxxi_ne64np4L128v4_v3.LR.amip_0101.eam.i.2000-01-01-00000.20260911.nc
      if opts.get('old_L128'):
         init_root = '/lcrc/group/e3sm/data/inputdata/atm/scream/init'
         if opts.get('grid')=='ne64pg2_ne64pg2':
            run_cmd(f'./atmchange -b initial_conditions::filename=\"{init_root}/eamxxi_ne64np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20260813.nc\"')
            run_cmd(f'./atmchange -b vertical_coordinate_filename=\"{init_root}/vertical_coordinates_L128_20220927.nc\"')
      #-------------------------------------------------------------------------
      if opts.get('grid')=='ne32pg2_ne32pg2':
         if opts.get('ic')=='new':
            run_cmd(f'./atmchange -b initial_conditions::filename="/lcrc/group/e3sm/ac.whannah/HICCUP/files_init/eamxxi_ne32np4L128v4_ERA5-20121001_c20260922.nc" ')
         if opts.get('ic')=='old':
            run_cmd(f'./atmchange -b initial_conditions::filename="/lcrc/group/e3sm/public_html/inputdata/atm/scream/init/eamxxi_ne32np4L128v4_v3.LR.amip_0101.eam.i.2000-01-01-00000.20260911.nc" ')

      if opts.get('grid')=='ne128pg2_ne128pg2':
         if opts.get('ic')=='new':
            run_cmd(f'./atmchange -b initial_conditions::filename="/lcrc/group/e3sm/ac.whannah/HICCUP/files_init/eamxxi_ne128np4L128v4_ERA5-20190101_c20260922.nc" ')
         if opts.get('ic')=='old':
            raise ValueError('ERROR - you forgot to set the IC file!')
            # run_cmd(f'./atmchange -b initial_conditions::filename="/lcrc/group/e3sm/public_html/inputdata/atm/scream/init/eamxxi_ne32np4L128v4_v3.LR.amip_0101.eam.i.2000-01-01-00000.20260911.nc" ')
      #-------------------------------------------------------------------------
      # try alt IC
      if opts.get('alt_init'):
         if opts.get('grid')=='ne32pg2_ne32pg2':
            # init_file = '/lcrc/group/e3sm/data/inputdata/atm/scream/init/eamxxi_ne32np4L128v4_v3.LR.amip_0101.eam.i.2000-01-01-00000.20260911.nc' # default
            # init_file = '/global/cfs/projectdirs/e3sm/whannah/HICCUP/HICCUP.atm_era5.2019-08-01.ne32np4.L128v4.nc'
            init_file = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/HICCUP/HICCUP.atm_era5.2019-08-01.ne32np4.L128v4.20260918.nc'
            run_cmd(f'./atmchange -b initial_conditions::filename=\"{init_file}\"')
            sst_data_file = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/HICCUP/HICCUP.sst_noaa.2020-08-10.nc'
            # sst_grid_file = '/lcrc/group/e3sm/data/inputdata/ocn/docn7/domain.ocn.1x1.111007.nc' # default
            sst_grid_file = '/lcrc/group/e3sm/data/inputdata/ocn/docn7/domain.ocn.0.25x0.25.c20190221.nc'
            run_cmd(f'./xmlchange --file env_run.xml SSTICE_DATA_FILENAME={sst_data_file}')
            run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_GRID_FILENAME --val "{sst_grid_file}"')
            sst_yr = '2020'
            run_cmd(f'./xmlchange --file env_run.xml SSTICE_YEAR_ALIGN={sst_yr},')
            run_cmd(f'./xmlchange --file env_run.xml SSTICE_YEAR_START={sst_yr}')
            run_cmd(f'./xmlchange --file env_run.xml SSTICE_YEAR_END={sst_yr}')
      #-------------------------------------------------------------------------
      # # default time step recipe
      # run_cmd(f'./xmlchange ATM_NCPL=48 ') # 30 min
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=12 ') # 2.5 min
      # run_cmd(f'./atmchange -b se_tstep=300 ')
      # run_cmd(f'./atmchange -b dt_remap_factor=2 ')
      # run_cmd(f'./atmchange -b dt_tracer_factor=6 ')
      # run_cmd(f'./atmchange -b hypervis_subcycle_q=6 ')
      # run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=0 ')
      # run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')
      
      # # alt time step recipe - 20 min
      # run_cmd(f'./xmlchange ATM_NCPL=72 ')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=8 ')
      # run_cmd(f'./atmchange -b se_tstep=300 ')
      # run_cmd(f'./atmchange -b dt_remap_factor=2 ')
      # run_cmd(f'./atmchange -b dt_tracer_factor=4 ')
      # run_cmd(f'./atmchange -b hypervis_subcycle_q=4 ')
      # # run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=0 ')
      # # run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')

      # # alt time step recipe - 5 min
      # run_cmd(f'./xmlchange ATM_NCPL=288 ')
      # run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=2 ')
      # run_cmd(f'./atmchange -b se_tstep=60 ')
      # run_cmd(f'./atmchange -b dt_remap_factor=1 ')
      # run_cmd(f'./atmchange -b dt_tracer_factor=5 ')
      # run_cmd(f'./atmchange -b hypervis_subcycle_q=5 ')
      # # run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=0 ')
      # # run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')

      # alt time step recipe - shorten dyn dt for ne32
      if opts.get('grid')=='ne32pg2_ne32pg2':
         if opts.get('dt_rcp')==1:
            run_cmd(f'./xmlchange ATM_NCPL=60 ') # 24 min
            run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=12 ') # 2 min
            run_cmd(f'./atmchange -b se_tstep=240 ') # 4 min
            run_cmd(f'./atmchange -b dt_remap_factor=2 ')
            run_cmd(f'./atmchange -b dt_tracer_factor=6 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_q=6 ')
            run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=0 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')
         if opts.get('dt_rcp')==2:
            run_cmd(f'./xmlchange ATM_NCPL=48 ') # 30 min
            run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=12 ') # 2.5 min
            run_cmd(f'./atmchange -b se_tstep=225 ') # 3+ min
            run_cmd(f'./atmchange -b dt_remap_factor=2 ')
            run_cmd(f'./atmchange -b dt_tracer_factor=8 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_q=8 ')
            run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=2 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')
         if opts.get('dt_rcp')==3:
            run_cmd(f'./xmlchange ATM_NCPL=48 ') # 30 min
            run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=12 ') # 2.5 min
            run_cmd(f'./atmchange -b se_tstep=257.1428571428570 ') # 4+ min
            run_cmd(f'./atmchange -b dt_remap_factor=1 ')
            run_cmd(f'./atmchange -b dt_tracer_factor=7 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_q=7 ')
            run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=2 ')
            run_cmd(f'./atmchange -b hypervis_subcycle_tom=1 ')

      #-------------------------------------------------------------------------
      # file = open('user_nl_elm','w')
      # # file.write(f' fsurdat = \'\'\n')
      # file.write(f' finidat = \'\'\n')
      # # file.write(f' finidat = \'/lcrc/group/e3sm/data/inputdata/lnd/clm2/initdata_map/ne32pg2.elm.r.2013-08-01-00000.64bit.nc\'\n')      
      # file.close()
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      # # Enable tendency calculation for output
      # run_cmd(f'./atmchange -b shoc::compute_tendencies=T_mid')
      # if 'F2010xx-ZM' in opts['compset']:
      #    run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid')
      #-------------------------------------------------------------------------
      # add_hist_file('output_1si.yaml',get_hist_opts_1si(opts))
      # # add_hist_file('output_1da.yaml',get_hist_opts_1da(opts))
      # hist_file_list_str = ','.join(hist_file_list)
      # run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # disable history output
      run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
      #-------------------------------------------------------------------------
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
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
# gw_flds = f'''
#          - gw_horiz_winds_tend
#          - gw_oro_tend_u
#          - gw_conv_tend_u
#          - gw_T_mid_tend
#          - gw_conv_heating_depth
#          - gw_conv_heating_max
# '''
# {gw_flds if opts.get('use_gw',False) else ''}
def get_hist_opts_1si(opts):
   return f'''
%YAML 1.1
---
filename_prefix: output.1si
averaging_type: Instant
max_snapshots_per_file: 32
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         #------------------------------
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         #------------------------------
         - T_2m
         - U_at_model_bot
         - surf_sens_flux
         - surf_evap
         #------------------------------
         # - T_mid
         # - z_mid
         # - shoc_T_mid_tend
         # - zm_T_mid_tend
         # - zm_prec
         # - zm_activity
output_control:
   frequency: 1
   frequency_units: nsteps
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
