#!/usr/bin/env python
# ============================================================================
#   This script runs atmosphere only simulations of ACME
#   It is configured to handle hindcasts and/or nudging
#
#    Jan, 2017  Walter Hannah       Lawrence Livermore National Lab
#    Updates:
#    ------------
#    Sep, 2017  Chris Jones         Pacific Northwest National Lab
#                                   (update to pep8 style compliance;
#                                    minor changes)
#
# ============================================================================

import os
import runsp
import datetime as dt   # pandas not available on titan
import itertools

trial_run = False
do_chem = False
quick_test = False

Config = runsp.Config(newcase=True, config=True, clean=False, build=True,
                      runsim=True, update_namelist=True, debug=False,
                      copyinit=True, testrun=trial_run, hindcast=True,
                      continue_run=False, sp=True)

compiler = 'intel'
gcm_res = "ne30"
res = gcm_res  # to make sure I didn't miss anything 
ny = 1
nlev = 72

# choose run combinations
default_run_setup = [(64, 96, 4)]
nx_perts = (32,  128)
dx_perts = (0.5, 1, 2)
ncpl_perts = (144, 72, 48)  # 10 min, 15 min, 20 min

# run_combos = [nx, ncpl, dx]
run_combos = [(64, 96, 4), (64, 96, 2), (64, 96, 1), (64, 96, 0.5),
              (32, 96, 4), (128, 96, 4),
              (64, 144, 4), (64, 48, 4)]


basename = 'SP1_nochem'
top_dir = os.getenv('HOME') + '/repos/current/ACME-ECP/'

def gen_case_name(gcm_res, nx, ny, dx, nlev=72, ncpl=48, basename='SP1'):
    base = basename
    if ny > 1:
        base = base + '_3D' # momentum transport
    if Config.debug is True:
        base = base + "_debug"
    snlev = str(nlev) + "L"
    sdx = str(dx).replace('.','') + 'km'  # 0.5 -> '05'
    scpl = 'nc' + str(ncpl)
    return "_".join([gcm_res, base, snlev, str(nx)+"x"+str(ny), sdx, scpl])

def calc_se_splits(ncpl):
    """choose se_nsplit and se_rsplit based on coupling frequenc

    want ncpl / (se_nsplit*se_rsplit) = effective 5-min dynamic step
    """
    if ncpl == 96:  # 15 minutes
        se_nsplit = 1
        se_rsplit = 3
    elif ncpl == 48:   # 30 minutes
        se_nsplit = 2
        se_rsplit = 3
    elif ncpl == 72:   # 20 minutes
        se_nsplit = 2
        se_rsplit = 2
    elif ncpl == 144:  # 10 minutes
        se_nsplit = 1
        se_rsplit = 2
    return se_nsplit, se_rsplit

def calc_stopn(res, nlev, ncpl):
    if "30" in str(res):  # ne30
        if nlev == 30:
            stopn = 30
            restn = 10
            wallclock = "06:00:00"
        else:
            stopn = 10
            restn = 5
            wallclock = "06:00:00"
    if ncpl > 100:
        wallclock = "08:00:00"
    return stopn, restn, wallclock

cam_namelist_hindcast = {
    "nhtfrq": "0,-1",
    "mfilt": "1,24",
    "fincl2": "'T','Q','PS','TS','OMEGA','U','V','QRL','QRS',"
              "'FSNT','FLNT','FLNS','FSNS','FSNTC','FLNTC','LWCF','SWCF',"
              "'LHFLX','SHFLX','TAUX','TAUY','PRECT','TMQ',"
              "'CLOUD','CLDLIQ','CLDICE','SPDT','SPDQ','SPTLS','SPQTLS'",
    "srf_flux_avg": "1",
    }
if not do_chem:
    prescribed_aero_path = "'/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/chem/trop_mam/aero'"
    prescribed_aero_file = "'mam4_0.9x1.2_L72_2000clim_c170323.nc'"
    cam_namelist_hindcast.update(prescribed_aero_type="'CYCLICAL'",
                                 prescribed_aero_datapath=prescribed_aero_path,
                                 prescribed_aero_file=prescribed_aero_file,
                                 prescribed_aero_cycle_yr="01",
                                 use_hetfrz_classnuc=".false.")
                                 #prescribed_ozone_cycle_yr="2000",
                                 #prescribed_ozone_datapath="'/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/ozone'",
                                 #prescribed_ozone_file="'ozone_1.9x2.5_L26_2000clim_c091112.nc'",
                                 #prescribed_ozone_name="'O3'",
                                 #prescribed_ozone_type="'CYCLICAL'")

for (nx, ncpl, dx) in run_combos:
    se_nsplit, se_rsplit = calc_se_splits(ncpl)
    cam_namelist_hindcast.update(se_nsplit=str(se_nsplit),
                                 rsplit=str(se_rsplit))
    if gcm_res == "ne16":
        ntasks = 1536
        ndyn = 1536
    elif gcm_res == "ne30":
        ntasks = 6076
        ndyn = 5400
    elif gcm_res == "ne4":
        ntasks = 866 # easiest way to do this - could go up to 866
        ndyn = 96
    else:
        ntasks = None
        ndyn = None
    if nx * ny > 150: # use more processes! 
        ntasks = 21600

    # ===================================================
    # Step 1: Build the executable:
    # ===================================================
    BuildCase = runsp.Case(case_name=gen_case_name(gcm_res, nx, ny, dx, nlev=72, ncpl=ncpl, basename=basename),
                           res=gcm_res,
                           compiler=compiler,
                           compset="FC5AV1C-04P2",
                           top_dir=top_dir,
                           sp=True)

    # (1) Create newcase
    if Config.newcase is True:
        BuildCase.create_newcase(test=trial_run)

    # (2a) Edit env_mach_pes.xml
    if Config.config is True:
        if Config.clean is True:
            BuildCase.setup(clean=True, test=trial_run)
        # specify additional env_mach_pes.xml as kwargs to config_env_mach_pes
        BuildCase.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=ntasks, num_dyn=ndyn)

        # (2b) Case setup
        BuildCase.setup(test=trial_run)

    # (3a) Edit env_build.xml
    # (3b) Build case
    if Config.build is True:
        if Config.clean is True:
            BuildCase.build(clean=True, test=trial_run)

        new_cam_config_opts = {"-crm_nx": str(nx), "-crm_ny": str(ny),
                               "-crm_dx": str(dx * 1000),
                               "-crm_dt": str(5),
                               "-microphys": "mg2"}
        if not do_chem:
            new_cam_config_opts["-chem"] = "none"
            dict_pop = ('-rain_evap_to_coarse_aero', '-bc_dep_to_snow_updates')
        else:
            dict_pop = None

        if ny > 1:  # 3D case
            new_cam_config_opts['-cppdefs'] = "'-DCRM3D -DSPMOMTRANS'" 
        if Config.debug:
            new_cam_config_opts['-cppdefs'] = "'-DSP_ORIENT_RAND -DSP_TK_LIM -DAPPLY_POST_DECK_BUGFIXES'"

        if nlev == 30:
            default_set="SP1_nlev30"
        else:
            default_set="SP1"
        BuildCase.set_cam_config_opts(test=trial_run, default_set=default_set,
                                      dict_pop=dict_pop,
                                      **new_cam_config_opts)
        BuildCase.xmlchanges('env_build.xml', test=trial_run,
                             DEBUG=str(Config.debug).upper())
        if not BuildCase.is_build_complete():
            BuildCase.build(test=trial_run)
    if not trial_run:
        if not BuildCase.is_build_complete():
            print 'Build failed for', BuildCase
            continue

    if Config.update_namelist is True:
        BuildCase.update_namelist(**cam_namelist_hindcast)
    print "Current namelist"
    print BuildCase.namelist
    print BuildCase.Directory.cam_namelist_file

    stopn, restn, wall_time = calc_stopn(gcm_res, nlev, ncpl)
    resub = 30 // stopn  # just for now ...
    # resub = 3
    if trial_run is False:
        BuildCase.write_namelist_to_file()
        # update run-time options in xmlfiles:
        BuildCase.xmlchanges("env_run.xml", test=trial_run,
                           RUN_TYPE="startup",
                           RUN_STARTDATE="2000-01-01",
                           REST_OPTION="ndays",
                           REST_N=str(restn),
                           STOP_OPTION="ndays",
                           STOP_N=str(stopn),
                           RESUBMIT=str(resub),
                           ATM_NCPL=str(ncpl),
                           CONTINUE_RUN=str(Config.continue_run).upper(),
                           INFO_DBUG="1")
        if Config.debug:
            BuildCase.xmlchanges("env_run.xml", test=trial_run,
                                 REST_OPTION="nsteps",
                                 REST_N="5")
    
    if quick_test:
        BuildCase.xmlchanges("env_run.xml", test=trial_run,
                             REST_OPTION="none",
                             STOP_OPTION="nsteps",
                             RESUBMIT="0",
                             STOP_N="5")
        wall_time = "01:00:00"
    BuildCase.xmlchanges("env_batch.xml", test=trial_run,
                         JOB_WALLCLOCK_TIME=wall_time)

    # Submit the case
    if Config.runsim is True:
        BuildCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
