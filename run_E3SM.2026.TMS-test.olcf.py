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
'''NOTES
branch whannah/scidac-2026-v4-tuning was made on Sep 29 using:
=> master @ Sep 29
=> merge whannah/eamxx/conv-gw-fix
=> merge whannah/eamxx/fix-zm-non-bfb
=> merge whannah/eamxx/mcsp-momentum-update

nohup python -u run_E3SM.2026.rayfric-test.nersc.py > run_E3SM.2026.rayfric-test.nersc.py.out &
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
newcase,config,build,clean,set_run_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'cli115'
top_dir = os.getenv('HOME')+'/E3SM'
src_dir = f'{top_dir}/E3SM_SRC0' # branch => ???

# clean        = True
newcase      = True
config       = True
build        = True
set_run_opts = True
submit       = True
# continue_run = True


# stop_opt,stop_n,resub,walltime,queue = 'ndays',10,0,'1:00:00','regular'
# stop_opt,stop_n,resub,walltime,queue = 'ndays',365,4-1,'32:00:00','regular'

#---------------------------------------------------------------------------------------------------
'''
ohf - obstacle_height_factor   => default: 1.0   => Factor to convert SGH to COH
ohn - obstacle_height_min      => default: 1.0   => Min COH
rlf - roughness_length_factor  => default: 0.075 => Factor to convert COH to ERL
rlx - roughness_length_max     => default: 100.0 => Max ERL
wsn - wspd_squared_min         => default: 0.01  => Min lowest level wind speed squared [m2/s2]
dsf - drag_scaling_factor      => default: 1.0   => Scaling factor for TMS drag coefficient
'''
#---------------------------------------------------------------------------------------------------

kwargs_ne256  = ({'num_nodes':128,'grid':'ne256pg2_ne256pg2'})
kwargs_ne30   = ({'num_nodes':4,'grid':'ne30pg2_ne30pg2'})

# kwargs_common = {'prefix':'2026-TMS-TEST-00','compset':'F2010xx-ZM-CICE'}
kwargs_common = {'prefix':'2026-TMS-TEST-01','compset':'F2010xx-ZM-CICE'} # start over after exploring stability issue

# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00' # initial ne30 test
stop_opt,stop_n,resub,walltime = 'ndays',183,2*5-1,'2:00:00' # longer ne30

# add_case(**kwargs_common,**kwargs_ne30,tms=False)
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.0,ohn=1.0,rlf=0.075,rlx=100.0,wsn=0.01,dsf=1.0) # defaults
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=0.5,ohn=1.0,rlf=0.075,rlx=100.0,wsn=0.01,dsf=1.0) # reduce ohf
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.0,ohn=1.0,rlf=0.035,rlx=100.0,wsn=0.01,dsf=1.0) # reduce rlf
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.0,ohn=0.5,rlf=0.075,rlx=100.0,wsn=0.01,dsf=1.0) # reduce ohn
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.0,ohn=1.0,rlf=0.075,rlx=100.0,wsn=0.01,dsf=0.5) # reduce dsf
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.0,ohn=2.0,rlf=0.075,rlx=100.0,wsn=0.01,dsf=1.0) # increase ohn
# add_case(**kwargs_common,**kwargs_ne30,tms=True,ohf=1.5,ohn=1.0,rlf=0.075,rlx=100.0,wsn=0.01,dsf=0.5) # increase ohf and decrease dsf

# # try marks suggestion of vert_remap_u_alg=11
# add_case(**kwargs_common,**kwargs_ne30,vra=11,tms=False)
# add_case(**kwargs_common,**kwargs_ne30,vra=11,tms=True)

### retry control cases with more frequent vertical remap
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=False)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.5) # reduce ohf
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,rlf=0.035) # reduce rlf
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohn=0.5) # reduce ohn
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.5) # reduce dsf
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohn=2.0) # increase ohn
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=1.5,dsf=0.5) # increase ohf and decrease dsf

# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25) # reduce ohf
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,rlf=0.01) # reduce rlf
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.25) # reduce dsf

# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.50, rlf=0.04, dsf=0.50) # reduce all 3 scaling factors
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.75, rlf=0.04, dsf=0.25) # reduce all 3 scaling factors
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25, rlf=0.04, dsf=0.75) # reduce all 3 scaling factors
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.40, rlf=0.07, dsf=0.40) # reduce all 3 scaling factors



# # A) Same z0 over mountains as default TMS (rlf*ohf = 0.075), but TMS off over more flat terrain.
# #    Tests whether the JJA gain from ohf=0.25 comes from where TMS is off or from weaker drag.
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.5, rlf=0.15)  # off where SGH < 2 m
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,rlf=0.3)   # off where SGH < 4 m

# # B) More drag mainly in stable (winter/night) conditions via the wind-shear floor in Ri
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,wsn=1.0)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,wsn=4.0)

# # C) Start from the best JJA runs and try to recover DJF with wsn
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,wsn=1.0)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,rlf=0.04,dsf=0.75,wsn=1.0)

# # D) Split the gold run's settings to see which one helps
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,dsf=0.75)



# # weaker drag overall, more drag in stable (winter) conditions
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.5,wsn=4.0)

# # upper end of the wsn sweep
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,wsn=10.0)

# # TMS off over flat terrain (mountain z0 at default) + more stable-condition drag
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.5, rlf=0.15,wsn=1.0)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,rlf=0.3, wsn=1.0)

# # TMS off over flat terrain + slightly weaker drag (between set A and the gold run)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,ohf=0.25,rlf=0.3,dsf=0.75)

# stronger drag reduction with dsf - try to match earlier case with => ohf=0.75, rlf=0.04, dsf=0.25
add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.4,wsn=1.0)
add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.2,wsn=1.0)
# add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.1,wsn=1.0)
add_case(**kwargs_common,**kwargs_ne30,rmf=1,tms=True,dsf=0.05,wsn=1.0)


#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix']:      case_list.append(val)
      elif key in ['grid']:      case_list.append(val.split('_')[0])
      elif key in ['compset']:   continue
      # elif key in ['arch']:      continue
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: continue # case_list.append(f'NN_{val}')
      elif key in ['num_tasks']: continue # case_list.append(f'NT_{val}')
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

   print(f'{case}')
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
   # arch       = opts.get('arch','CPU')
   #------------------------------------------------------------------------------------------------
   machine,compiler = 'frontier','craygnu-mphipcc'
   if 'num_nodes' in opts:
      max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
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
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      if opts.get('vgrid') is not None:
         run_cmd(f'./xmlchange EAMXX_VGRID={opts.get('vgrid')}')
      else:
         run_cmd(f'./xmlchange EAMXX_VGRID=L128v4')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if set_run_opts:
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      #-------------------------------------------------------------------------
      # enable split-form
      run_cmd(f'./atmchange -b theta_advect_form=2')
      run_cmd(f'./atmchange -b pgrad_correction=0')
      # increase vertical remap frequency
      if opts.get('rmf') is not None: run_cmd(f'./atmchange -b dt_remap_factor={opts.get('rmf')}')
      # try marks suggestion of vert_remap_u_alg=11
      if opts.get('vra') is not None: run_cmd(f'./atmchange -b vert_remap_u_alg={opts.get('vra')}')
      #-------------------------------------------------------------------------
      if opts.get('tms') is not None:
         if opts.get('tms'):
            run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list=tms,shoc,cld_fraction,spa,p3')
         else:
            run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list=shoc,cld_fraction,spa,p3')
      #-------------------------------------------------------------------------
      tms_nl_prfx = 'physics::mac_aero_mic::tms'
      if opts.get('ohf') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::obstacle_height_factor={opts.get('ohf')}')
      if opts.get('ohn') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::obstacle_height_min={opts.get('ohn')}')
      if opts.get('rlf') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::roughness_length_factor={opts.get('rlf')}')
      if opts.get('rlx') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::roughness_length_max={opts.get('rlx')}')
      if opts.get('wsn') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::wspd_squared_min={opts.get('wsn')}')
      if opts.get('dsf') is not None: run_cmd(f'./atmchange -b {tms_nl_prfx}::drag_scaling_factor={opts.get('dsf')}')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('output_1ma.yaml', get_hist_opts_1ma(opts) )
      # add_hist_file('output_1da.yaml', get_hist_opts_1da(opts) )
      # add_hist_file('output_1si.yaml', get_hist_opts_1si(opts) )
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange -b scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # # disable history output
      # run_cmd(f'./atmchange scorpio::output_yaml_files=""')
      # print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
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
# time step instantaneous output
def get_hist_opts_1si(opts):
   return f'''
filename_prefix: output.1si
averaging_type: instant
max_snapshots_per_file: 144
fields:
   physics_pg2:
      field_names:
         - U
         - V
         - T_mid
         - ps
         - gw_oro_tend_u
         - gw_oro_tend_v
         - gw_oro_tend_t
output_control:
   frequency: 1
   frequency_units: nsteps
'''
# daily mean output - native grid
def get_hist_opts_1da(opts):
   return f'''
filename_prefix: output.1da
averaging_type: average
max_snapshots_per_file: 5
fields:
   physics_pg2:
      field_names:
         # precipitation
         - precip_total_surf_mass_flux
         - precip_liq_surf_mass_flux
         - precip_ice_surf_mass_flux
         - zm_prec
         # water paths
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         - LW_flux_up_at_model_top
         - T_2m
         - U_at_850hPa
         - U_at_200hPa
         - U_at_50hPa
         - U_at_20hPa
         - U_at_10hPa
         - U_at_model_top
         - T_mid_at_10hPa
output_control:
   frequency: 1
   frequency_units: ndays
'''
# monthly mean output - native grid
def get_hist_opts_1ma(opts):
   return f'''
filename_prefix: output.1ma
averaging_type: average
max_snapshots_per_file: 1
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
         # - RelativeHumidity
         # - qv
         # - qc
         # - qr
         # - qi
         # - qm
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
         # - gw_horiz_winds_tend
         # - gw_oro_tend_u
         # - gw_conv_tend_u
         # - zm_detr_qc
         # - zm_detr_qi
         # ---------------------------------------------------------------------
         # ZM diagnostic fields
         - zm_prec
         # - zm_activity
         # - zm_cape
         # - zm_dcape
         # - zm_depth
         # - mcsp_ds_out
         # - mcsp_dq_out
         # - mcsp_du_out
         # - mcsp_freq
         # - mcsp_shear
         # - evap_ds_out
         # - evap_dq_out
output_control:
   frequency: 1
   frequency_units: nmonths
'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
