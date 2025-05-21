#!/usr/bin/env python
import os, datetime, subprocess as sp, numpy as np
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/SCREAM_SRC'

#  clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug 

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:30:00'
# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'
   
ne = 20
dtime = 10
total_domain_size = 200e3 # domain length [m] 200km for GATE

case = '.'.join(['DPSCREAM','GATE',f'ne{ne}','00'])

# case = case+'.debug-on'
# case = case+'.checks-on'

#---------------------------------------------------------------------------------------------------
# Case specific information
#---------------------------------------------------------------------------------------------------
lat,lon,iop_file = 9.00,336.0,'GATEIII_iopfile_4scam.nc'
do_iop_srf_prop   = '.false.'    # Use surface fluxes in IOP file?
do_iop_nudge_tq   = '.false.'    # Relax T&Q to observations?
do_iop_nudge_uv   = '.true.'     # Relax U&V to observations?
do_iop_subsidence = '.false.'    # compute LS vertical transport?
do_turnoff_swrad  = False        # Turn off SW calculation
do_turnoff_lwrad  = False        # Turn off LW calculation
startdate         = '1974-08-30' # Start date in IOP file
start_in_sec      = 0            # start time in seconds in IOP file

init_aero_type  = 'prescribed'                           # Aerosol specification (for SCREAM always prescribed)
iop_path        = 'atm/cam/scam/iop'                     # Location of IOP file
presc_aero_path = 'atm/cam/chem/trop_mam/aero'           # Prescribed aerosol file path
presc_aero_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc' # Prescribed aerosol file name

# Set radiation frequency parameters
iradsw_in = 0 if do_turnoff_swrad else 5
iradlw_in = 0 if do_turnoff_lwrad else 5


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main():

   print('\n  case : '+case+'\n')

   num_dyn = ne*ne*6

   ntasks = 64 # default to single node
   if ne==20: ntasks = 64*2
   if ne==30: ntasks = 64*8

   #-------------------------------------------------------------------------------
   # Define run command
   #-------------------------------------------------------------------------------
   # Set up terminal colors
   class tcolor:
      ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
   def run_cmd(cmd,suppress_output=False,execute=True):
      if suppress_output : cmd = cmd + ' > /dev/null'
      msg = tcolor.GREEN + cmd + tcolor.ENDC
      print(f'\n{msg}')
      if execute: os.system(cmd)
      return
   #---------------------------------------------------------------------------------------------------
   # Create new case
   #---------------------------------------------------------------------------------------------------
   if newcase :
      cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
      cmd += f' -compset F2000-SCREAM-HR -res ne30_ne30 --pecount {ntasks}x1'
      run_cmd(cmd)

      # Copy this run script into the case directory
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #---------------------------------------------------------------------------------------------------
   # Configure
   #---------------------------------------------------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   if config : 
      #-------------------------------------------------------
      # Atmos configure stuff - write the namelist first
      write_atm_namelist()
      run_cmd('./xmlchange CAM_CONFIG_OPTS="-phys default -scam -dpcrm_mode -nlev 128 -shoc_sgs -microphys p3 -rad rrtmgp -chem none" ')
      run_cmd(f'./xmlchange RUN_STARTDATE="{startdate}",START_TOD="{start_in_sec}"')
      run_cmd(f'./xmlchange PTS_MULTCOLS_MODE="TRUE",PTS_MODE="TRUE",PTS_LAT="{lat}",PTS_LON="{lon}"')
      #-------------------------------------------------------
      # other misc options
      run_cmd('./xmlchange ELM_CONFIG_OPTS="-phys elm" ')

      # Compute number of columns needed for component model initialization
      num_col = ne*ne*(4-1)**2
      run_cmd(f'./xmlchange MASK_GRID="USGS",PTS_NX="{num_col}",PTS_NY=1')
      run_cmd(f'./xmlchange ICE_NX="{num_col}",ICE_NY=1')
      run_cmd(f'./xmlchange CALENDAR="GREGORIAN"')

      run_cmd(f'./xmlchange PIO_TYPENAME="netcdf"')
      #-------------------------------------------------------
      # Run case setup
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #---------------------------------------------------------------------------------------------------
   # Build
   #---------------------------------------------------------------------------------------------------
   if build : 
      if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #---------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   #---------------------------------------------------------------------------------------------------
   if submit : 
      
      write_atm_namelist()
      #-------------------------------------------------------
      # non-atm namelist
      #-------------------------------------------------------
      # avoid writing monthly cice file
      file = open('user_nl_cice','w') 
      file.write(f"histfreq='y','x','x','x','x' \n")
      file.close()


      # ELM output is temporarily broken for DP-SCREAM so turn it off
      file = open('user_nl_elm','w') 
      file.write(f"hist_empty_htapes = .true. \n")
      file.close()

      #-------------------------------------------------------
      # Set some run-time stuff
      #-------------------------------------------------------
      # Write restart files at the end of model simulation
      run_cmd(f'./xmlchange REST_OPTION="end"')

      if 'dtime' in locals(): run_cmd(f'./xmlchange ATM_NCPL={(86400/dtime)}')
      run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
      run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

      if continue_run :
         run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
      else:
         run_cmd('./xmlchange CONTINUE_RUN=FALSE')
      #-------------------------------------------------------
      # Submit the run
      #-------------------------------------------------------
      run_cmd('./case.submit')

   #---------------------------------------------------------------------------------------------------
   # Print the case name again
   #---------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def write_atm_namelist():
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   file = open('user_nl_eam','w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = -24, 1 \n')
   file.write(' mfilt     = 5000, 5000 \n')
   file.write(" avgflag_pertape=\'A\',\'I\','I' \n")
   
   file.write(" fincl2    = 'crm_grid_x','crm_grid_y'")
   file.write(             ",'PS','TS'")
   file.write(             ",'PRECL','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP','TGCLDCWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   file.write(             ",'QREFHT','SOLIN' ")
   file.write(             ",'WINDSPD_10M','' ")
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'T500','T850','Q850'")
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   # file.write(             ",'','' ")

   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRS','QRL'")
   file.write('\n')

   #------------------------------
   # Other namelist stuff
   #------------------------------
   file.write(f" use_gw_front     = .false. \n")
   file.write(f" use_gw_oro       = .false. \n")
   file.write(f" use_gw_convect   = .false. \n")
   file.write(f" deep_scheme      = 'off' \n")
   file.write(f" convproc_do_aer  = .false. \n")
   file.write(f" iop_dosubsidence = {do_iop_subsidence} \n")
   file.write(f" iop_nudge_tq     = {do_iop_nudge_tq} \n")
   file.write(f" iop_nudge_uv     = {do_iop_nudge_uv} \n")
   file.write(f" scmlat           = {lat} \n")
   file.write(f" scmlon           = {lon} \n")
   file.write(f" iradsw           = {iradsw_in} \n")
   file.write(f" iradlw           = {iradlw_in} \n")
   file.write(f" scm_iop_srf_prop = {do_iop_srf_prop} \n")
   file.write(f" iopfile          = '{din_loc_root}/{iop_path}/{iop_file}' \n")
   file.write(f" pertlim          = 0.001 \n")
   file.write(f" iop_perturb_high = 900.0D0 \n")

   # Timestepping stuff related to DP-SCREAM
   # NOTE, if you change resolution from default it may be required to change some of these settings.
   file.write(f"transport_alg          =  0 \n")
   file.write(f"semi_lagrange_cdr_alg  = 20 \n")
   file.write(f"hypervis_order         =  2 \n")
   file.write(f"hypervis_subcycle      =  1 \n")
   file.write(f"hypervis_subcycle_tom  =  1 \n")
   file.write(f"hypervis_subcycle_q    =  1 \n")
   file.write(f"nu                     =  0.216784 \n")
   file.write(f"nu_div                 = -1 \n")
   file.write(f"nu_p                   = -1 \n")
   file.write(f"nu_q                   = -1 \n")
   file.write(f"nu_top                 =  0 \n")
   file.write(f"qsplit                 = -1 \n")
   file.write(f"rsplit                 = -1 \n")
   file.write(f"se_ftype               =  4 \n")
   file.write(f"se_limiter_option      =  9 \n")
   file.write(f"se_nsplit              = 30 \n")
   file.write(f"se_partmethod          =  4 \n")
   file.write(f"semi_lagrange_nearest_point_lev = 100 \n")
   file.write(f"theta_hydrostatic_mode = .false. \n")
   file.write(f"tstep_type             = 9 \n")
   file.write(f"theta_advect_form      = 1 \n")
   file.write(f"vert_remap_q_alg       = 10 \n")
   file.write(f"vthreads               = 1 \n")
   file.write(f"se_tstep               = -1 \n")
   file.write(f"dt_remap_factor        = 1 \n")
   file.write(f"dt_tracer_factor       = 1 \n")
   file.write(f"cld_macmic_num_steps   = 1 \n")
   file.write(f"hypervis_scaling       = 3.0 \n")
   file.write(f"shoc_timestep          = -1 \n")
   file.write(f"shoc_thl2tune          = 1.0 \n")
   file.write(f"shoc_qw2tune           = 1.0 \n")
   file.write(f"shoc_qwthl2tune        = 1.0 \n")

   # Settings related to domain size and resolution
   file.write(f"mesh_file = 'none' \n")
   file.write(f"se_ne_x   = {ne} \n")
   file.write(f"se_ne_y   = {ne} \n")
   file.write(f"se_lx     = {total_domain_size} \n")
   file.write(f"se_ly     = {total_domain_size} \n")


   # Tuning parameters related to the prescribed aerosol model
   file.write(f"use_hetfrz_classnuc      = .false. \n")
   file.write(f"aerodep_flx_type         = 'CYCLICAL' \n")
   file.write(f"aerodep_flx_datapath     = '{din_loc_root}/{presc_aero_path}' \n")
   file.write(f"aerodep_flx_file         = '{presc_aero_file}' \n")
   file.write(f"aerodep_flx_cycle_yr     = 01 \n")
   file.write(f"prescribed_aero_type     = 'CYCLICAL' \n")
   file.write(f"prescribed_aero_datapath = '{din_loc_root}/{presc_aero_path}' \n")
   file.write(f"prescribed_aero_file     = '{presc_aero_file}' \n")
   file.write(f"prescribed_aero_cycle_yr = 01 \n")
   
   # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

   # if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   # close atm namelist file
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   main()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------