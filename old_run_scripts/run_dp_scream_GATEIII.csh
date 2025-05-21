#!/bin/csh -fe

#######################################################################
#######################################################################
#######  Script to run SCREAM in doubly periodic (DP) mode
#######  GATEIII
#######  Maritime deep convection
#######
#######  Script Author: P. Bogenschutz (bogenschutz1@llnl.gov)

#######################################################
#######  BEGIN USER DEFINED SETTINGS

  # Set the name of your case here
  setenv casename scream_dp_GATEIII

  # Set the case directory here
  setenv casedirectory /p/lustre2/bogensch/ACME_simulations

  # Directory where code lives
  setenv code_dir /g/g19/bogensch/code

  # Code tag name
  setenv code_tag SCREAM_DP

  # Name of machine you are running on (i.e. cori, anvil, etc)
  setenv machine quartz

  # Name of project to run on, if submitting to queue
  setenv projectname cbronze


  # Set to debug queue?
  # - Some cases are small enough to run on debug queues
  # - Setting to true only supported for NERSC and Livermore Computing,
  #   else user will need to modify script to submit to debug queue
  setenv debug_queue false

  # Set number of processors to use
  set num_procs = 256

  # set walltime
  set walltime = '04:00:00'

  ## SET DOMAIN SIZE AND RESOLUTION:
  # - Note that these scripts are set to run with dx=dy=3.33 km
  # which is the default SCREAM resolution.

  # To estimate dx (analogous for dy):
  # dx = domain_size_x / (num_ne_x * 3)
  # (there are 3x3 unique columns per element, hence the "3" factor)

  # Set number of elements in the x&y directions
  set num_ne_x = 20
  set num_ne_y = 20

  # Set domain length (in m) in x&y direction
  set domain_size_x = 200000
  set domain_size_y = 200000

  # SET MODEL TIME STEP (in s).  NOTE that if you change the model resolution,
  #  it is likely the timestep will need to be adjusted.  Adjusting this
  #  time step may not be comprehensive, as dynamics related settings may
  #  also need to be modified (see namelist)

  set model_dtime = 120

####### END (mandatory) USER DEFINED SETTINGS, but...
####### Likely POSSIBLE EXCEPTIONS (not limited to):
#######  - If the user wants to add additional output, for example, the EAM
#######	   namelist (user_nl_eam) should be modified below to accomodate for this.
#######  - User has changed the resolution which may require adjustment
#######    of the dynamics time step settings (bogenschutz1@llnl.gov has run
#######    several cases at a range of resolutions and may be able to
#######    advise you on the appropriate settings).
#######
#######  - NOTE ON DEFAULT OUTPUT
#######    - *eam.h0* tapes contain the the default output averaged daily
#######      (for multi-day cases) or hourly (for shorter boundary layer
#######      cloud cases)
#######    - *eam.h1* tapes contain instantaneous 2D fields output hourly
#######    - ALL/any of this can be modified by the user based on needs
###########################################################################
###########################################################################
###########################################################################

# Case specific information kept here
  set lat = 9.00 # latitude
  set lon = 336.0 # longitude
  set do_iop_srf_prop = .false. # Use surface fluxes in IOP file?
  set do_iop_nudge_tq = .false. # Relax T&Q to observations?
  set do_iop_nudge_uv = .true. # Relax U&V to observations?
  set do_iop_subsidence = .false. # compute LS vertical transport?
  set do_turnoff_swrad = .false. # Turn off SW calculation
  set do_turnoff_lwrad = .false. # Turn off LW calculation
  set startdate = 1974-08-30 # Start date in IOP file
  set start_in_sec = 0 # start time in seconds in IOP file
  set stop_option = ndays
  set stop_n = 20
  set iop_file = GATEIII_iopfile_4scam.nc #IOP file name
# End Case specific stuff here

  # Aerosol specification (for SCREAM always prescribed)
  set init_aero_type = prescribed

  # Location of IOP file
  set iop_path = atm/cam/scam/iop

  # Prescribed aerosol file path and name
  set presc_aero_path = atm/cam/chem/trop_mam/aero
  set presc_aero_file = mam4_0.9x1.2_L72_2000clim_c170323.nc

  set PROJECT=$projectname
  set E3SMROOT=${code_dir}/${code_tag}

  cd $E3SMROOT/cime/scripts

  set compset=F2000-SCREAM-HR

  # Note that in DP-SCREAM the grid is set ONLY to initialize
  #  the model from these files
  set grid=ne30_ne30

  set CASEID=$casename

  set CASEDIR=${casedirectory}/$CASEID

  set run_root_dir = $CASEDIR
  set temp_case_scripts_dir = $run_root_dir/case_scripts

  set case_scripts_dir = $run_root_dir/case_scripts
  set case_build_dir   = $run_root_dir/build
  set case_run_dir     = $run_root_dir/run

# Create new case
  ./create_newcase -case $casename --script-root $temp_case_scripts_dir -mach $machine -project $PROJECT -compset $compset -res $grid
  cd $temp_case_scripts_dir

  ./xmlchange JOB_WALLCLOCK_TIME=$walltime

# Define executable and run directories
  ./xmlchange --id EXEROOT --val "${case_build_dir}"
  ./xmlchange --id RUNDIR --val "${case_run_dir}"

# Set to debug, only on certain machines
  if ($debug_queue == 'true') then
    if ($machine =~ 'cori*') then
      ./xmlchange --id JOB_QUEUE --val 'debug'
    endif

    if ($machine == 'quartz' || $machine == 'syrah') then
      ./xmlchange --id JOB_QUEUE --val 'pdebug'
    endif
  endif

# Get local input data directory path
  set input_data_dir = `./xmlquery DIN_LOC_ROOT -value`

# need to use single thread
  set npes = $num_procs
  foreach component ( ATM LND ICE OCN CPL GLC ROF WAV )
    ./xmlchange  NTASKS_$component=$npes,NTHRDS_$component=1
  end

# CAM configure options.  Set to SCREAM default settings.
  set CAM_CONFIG_OPTS="-phys default -scam -dpcrm_mode -nlev 128 -shoc_sgs -microphys p3 -rad rrtmgp -chem none"

  ./xmlchange CAM_CONFIG_OPTS="$CAM_CONFIG_OPTS"

  # Always run with the theta-l version of HOMME, the default for SCREAM
  ./xmlchange CAM_TARGET=theta-l

# if we want to turn off SW radiation, then set appropriate namelist settings here
  if ($do_turnoff_swrad == true) then
    set iradsw_in = 0
  else
    set iradsw_in = 5
  endif

# if we want to turn off LW radiation, then set appropriate namelist settings here
  if ($do_turnoff_lwrad == true) then
    set iradlw_in = 0
  else
    set iradlw_in = 5
  endif

# Runtime specific namelist information
cat <<EOF >> user_nl_eam
 use_gw_front = .false.
 use_gw_oro = .false.
 use_gw_convect = .false.
 deep_scheme = 'off'
 convproc_do_aer = .false.
 iop_dosubsidence = $do_iop_subsidence
 iop_nudge_tq = $do_iop_nudge_tq
 iop_nudge_uv = $do_iop_nudge_uv
 history_aerosol = .false.
 fincl2='CLDLOW','CLDMED','CLDHGH','CLDTOT','CDNUMC','DTENDTH','DTENDTQ','FLDS','FLNS','FLNSC','FLNT','FLNTC','FLUT','FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTC','FSNTOA','FSNTOAC','FSUTOA','FSUTOAC','LHFLX','SHFLX','LWCF','SWCF','OMEGA500','PRECL','PS','QREFHT','SOLIN','TAUX','TAUY','TGCLDCWP','TGCLDIWP','TGCLDLWP','TH7001000','TMQ','TREFHT','TS','WINDSPD_10M','crm_grid_x','crm_grid_y'
 mfilt = 5000, 5000
 nhtfrq = -24, -1
 avgflag_pertape='A','I'
 scmlat = $lat
 scmlon = $lon
 iradsw = $iradsw_in
 iradlw = $iradlw_in
 scm_iop_srf_prop = $do_iop_srf_prop
 iopfile = '$input_data_dir/$iop_path/$iop_file'
 pertlim = 0.001
 iop_perturb_high = 900.0D0
EOF

# Timestepping stuff related to DP-SCREAM
# NOTE, if you change resolution from default it may be required to
#  change some of these settings.
cat <<EOF >> user_nl_eam
 transport_alg         = 0
 semi_lagrange_cdr_alg = 20
 hypervis_order         =      2
 hypervis_subcycle              =   1
 hypervis_subcycle_tom = 1
 hypervis_subcycle_q            =  1
 nu             =   0.216784
 nu_div         =   -1
 nu_p           =   -1
 nu_q           =   -1
 nu_top         =  0
 qsplit         =  -1
 rsplit         =   -1
 se_ftype               = 4
 se_limiter_option              =  9
 se_nsplit              =   30
 se_partmethod          =  4
 semi_lagrange_nearest_point_lev = 100
 theta_hydrostatic_mode=.false.
 tstep_type = 9
 theta_advect_form=1
 vert_remap_q_alg               =  10
 vthreads               =  1
 se_tstep = -1
 dt_remap_factor = 1
 dt_tracer_factor = 1
 cld_macmic_num_steps = 1
 hypervis_scaling =  3.0
 shoc_timestep = -1
 shoc_thl2tune = 1.0
 shoc_qw2tune = 1.0
 shoc_qwthl2tune = 1.0
EOF

# Settings related to domain size and resolution
cat <<EOF >> user_nl_eam
 mesh_file = 'none'
 se_ne_x = $num_ne_x
 se_ne_y = $num_ne_y
 se_lx = $domain_size_x
 se_ly = $domain_size_y
EOF

# Tuning parameters related to the prescribed aerosol model
cat <<EOF >> user_nl_eam
  use_hetfrz_classnuc = .false.
  aerodep_flx_type = 'CYCLICAL'
  aerodep_flx_datapath = '$input_data_dir/$presc_aero_path'
  aerodep_flx_file = '$presc_aero_file'
  aerodep_flx_cycle_yr = 01
  prescribed_aero_type = 'CYCLICAL'
  prescribed_aero_datapath='$input_data_dir/$presc_aero_path'
  prescribed_aero_file='$presc_aero_file'
  prescribed_aero_cycle_yr = 01
EOF

# avoid the monthly cice file from writing as this
#   appears to be currently broken for SCM
cat <<EOF >> user_nl_cice
  histfreq='y','x','x','x','x'
EOF

# ELM output is temporarily broken for DP-SCREAM.  For now turn it off.
#  NOTE: this is a to do item to figure out.
cat <<EOF>> user_nl_elm
  hist_empty_htapes = .true.
EOF

set ELM_CONFIG_OPTS="-phys elm"
./xmlchange ELM_CONFIG_OPTS="$ELM_CONFIG_OPTS"

# Modify the run start and duration parameters for the desired case
  ./xmlchange RUN_STARTDATE="$startdate",START_TOD="$start_in_sec",STOP_OPTION="$stop_option",STOP_N="$stop_n"

# Compute number of columns needed for component model initialization
  set comp_mods_nx = `expr $num_ne_x \* $num_ne_y \* 9`

# Modify the latitude and longitude for the particular case
  ./xmlchange PTS_MULTCOLS_MODE="TRUE",PTS_MODE="TRUE",PTS_LAT="$lat",PTS_LON="$lon"
  ./xmlchange MASK_GRID="USGS",PTS_NX="${comp_mods_nx}",PTS_NY=1
  ./xmlchange ICE_NX="${comp_mods_nx}",ICE_NY=1
  ./xmlchange CALENDAR="GREGORIAN"


# Set model timesteps

  @ ncpl = 86400 / $model_dtime
  ./xmlchange ATM_NCPL=$ncpl
  ./xmlchange CAM_NAMELIST_OPTS="dtime=$model_dtime"
  ./xmlchange ELM_NAMELIST_OPTS="dtime=$model_dtime"

  ./case.setup

# Write restart files at the end of model simulation
  ./xmlchange PIO_TYPENAME="netcdf"
  ./xmlchange REST_OPTION="end"

# Build the case
  ./case.build

# Submit the case
  ./case.submit

  exit
