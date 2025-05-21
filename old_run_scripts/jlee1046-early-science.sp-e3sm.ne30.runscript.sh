#!/bin/bash
 # Run script for SP-E3SM early science runs on summit
 # 
 # Branch for this simulation campaign:
 # E3SM-Project/ACME-ECP.git/crjones/crm/summit_early_science (commit fdee19e)
 # 
 # See https://confluence.exascaleproject.org/x/SIOWAw for further details 
 #
 # This should serve as a template. For these summit early science 
 # runs, the preferred approach is to create a new run script titled
 #              early_science.$datestamp.sh 
 # that corresponds to the appropriately datestamp in the case name.
 #
 # Contact: christopher.jones@pnnl.gov
 #
 #caseid="TEST_crm_nx_rad64"
 caseid="TEST_crm_nx_rad4_nthread1_print2"
 create_newcase=true
 dosetup=true
 dobuild=true
 donamelist=true
 dosubmit=true

 datestamp=20191030

 ### BASIC INFO FOR create_newcase
 compset=FC5AV1C-L
 resolution=ne30_ne30
 project=m3312
 machine=cori-knl
 # pecount=L
 ### CRM details specified in CAM_CONFIG_OPTS
 # additional options specified directly in CAM_CONFIG_OPTS include:
 #    -phys cam5 -use_SPCAM -crm_adv MPDATA -nlev 72 -crm_nz 58
 #    -microphys mg2 -rad rrtmg -chem none -pcols 256
 crm_nx=64
 crm_ny=1
 crm_nx_rad=4
 crm_ny_rad=1
 crm_dx=1000
 crm_dt=5
 sp_micro=sam1mom
 cppdefs="' -DSP_DIR_NS -DSP_MCICA_RAD'"
 
 ### Create case_name:
 case_name=earlyscience.${compset}.${resolution%_*}.E3SM.$datestamp.${caseid}

 echo
 echo $case_name
 echo

 ### local directory info
 # repo_dir=$HOME/git_repos/Cori-Early-Science
 repo_dir=$HOME/ECP/ECP_MASTER
 case_dir_root=$HOME/ECP/Cases
 case_dir=$case_dir_root/$case_name
 cime_dir=$repo_dir/cime/scripts

 ### create case:
 if [ "$create_newcase" = true ] ; then
     cd $case_dir_root
     $cime_dir/create_newcase -compset $compset -res $resolution -project $project -mach $machine -case $case_name 
     #-pecount $pecount
 fi

 cd $case_dir
 ### case setup:
 if [ "$dosetup" = true ] ; then
      # need to use single thread for CRM
     ./xmlchange  NTHRDS_ATM=1
     ./xmlchange  NTHRDS_LND=1
     ./xmlchange  NTHRDS_ICE=1
     ./xmlchange  NTHRDS_OCN=1
     ./xmlchange  NTHRDS_CPL=1
     ./xmlchange  NTHRDS_GLC=1
     ./xmlchange  NTHRDS_ROF=1
     ./xmlchange  NTHRDS_WAV=1
     
     ./case.setup --clean
     ./case.setup --reset
     ./case.setup
 fi
 
 ### build options:
 if [ "$dobuild" = true ] ; then
     # ./xmlchange CAM_CONFIG_OPTS="-phys cam5 -clubb_sgs -nlev 72  -microphys mg2 -chem linoz_mam4_resus_mom -rain_evap_to_coarse_aero -bc_dep_to_snow_updates"
     ./xmlchange CAM_CONFIG_OPTS="-phys cam5 -use_SPCAM -crm_adv MPDATA -nlev 72 -microphys mg2 -crm_nz 58 -rad rrtmg -chem none -crm_nx ${crm_nx} -crm_ny ${crm_ny} -crm_dx ${crm_dx} -crm_dt ${crm_dt} -crm_nx_rad $crm_nx_rad -crm_ny_rad $crm_ny_rad -SPCAM_microp_scheme $sp_micro -bc_dep_to_snow_updates -cppdefs $cppdefs "
     ./xmlchange ATM_PIO_NETCDF_FORMAT="64bit_data"   # note: this may not actually do anything ...
     ./case.build --clean-all
     ./case.build
 fi

 ### Run options
 ./xmlchange ATM_NCPL=72
 ./xmlchange RUN_STARTDATE=0001-01-01
 ./xmlchange STOP_OPTION=ndays
 ./xmlchange STOP_N=1
 # ./xmlchange REST_OPTION=nmonths
 # ./xmlchange REST_N=2
 ./xmlchange RESUBMIT=0

 ### namelist options
 if [ "$donamelist" = true ] ; then
 rm user_nl_cam
 cat <<EOF >> user_nl_cam
   !! prescribed aerosols 
   !! (disabled because model failed to initialize; need to update CAM_CONFIG_OPTS with proper 
   !!  chemistry options in future runs if prescribed aerosols important)
   prescribed_aero_cycle_yr = 01
   prescribed_aero_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
   prescribed_aero_datapath = '/project/projectdirs/acme/inputdata/atm/cam/chem/presc_aero'
   prescribed_aero_type = 'CYCLICAL'
   aerodep_flx_type = 'CYCLICAL'
   aerodep_flx_datapath = '/project/projectdirs/acme/inputdata/atm/cam/chem/presc_aero'
   aerodep_flx_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
   aerodep_flx_cycle_yr = 01

   use_hetfrz_classnuc = .false.
   
   ! enable surface flux smoothing (stability requirement ?)
   srf_flux_avg = 1
   
   ! dycore options (5-min effective dynamics step)
   se_nsplit = 2
   rsplit = 2
   
   ! radiation every 20 minutes
   iradlw = 1
   iradsw = 1
   
   ! crm mean-state acceleration
   use_crm_accel = .true.
   crm_accel_factor = 2.
   crm_accel_uv = .true.
   srf_flux_avg = 1

   ! file i/o
   nhtfrq = 0,-1,-3
   mfilt = 1,120,40
   avgflag_pertape = 'A','A','A'

   ! hourly 2D fields
   fincl2 = 'PRECT','TMQ','LHFLX','SHFLX','TS','PS','FLNT','FSNT','FSNS','FLNS','SWCF','LWCF','TGCLDLWP','TGCLDIWP'

   ! daily 3D fields + budget terms (3-hourly even better for tropical/mcs dynamics)
   fincl3 = 'T','Q','Z3','U','V','OMEGA','CLDLIQ','CLDICE','QRL','QRS'

   inithist = 'ENDOFRUN'
 
EOF
 fi


 ### batch options
 ./xmlchange JOB_QUEUE=debug 
 ./xmlchange JOB_WALLCLOCK_TIME=0:30:00
 ./xmlchange CHARGE_ACCOUNT=$project
 ./xmlchange 
 ### submit
 if [ "$dosubmit" = true ] ; then
     ./case.submit --mail-user lee1046@llnl.gov -M begin -M end -M fail 
 fi    

