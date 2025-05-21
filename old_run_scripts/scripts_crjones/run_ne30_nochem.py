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
# (nx, ny, dx, nlev, ncpl)
# run_combos = [(64, 1, 4, 30, 288), (64, 1, 4, 72, 288), (64, 1, 4, 30, 48), (64, 1, 4, 72, 48)]
# run_combos = [(64, 1, 4, 72, 96), (32, 1, 4, 72, 96), (64, 1, 2, 72, 96)]
run_combos = [(64, 1, 1, 72, 144)]
basename = 'SP1_dyntest'
top_dir = os.getenv('HOME') + '/repos/current/ACME-ECP/'

def gen_case_name(gcm_res, compiler, nx, ny, dx, nlev, ncpl=48, EW=False, basename='SP1'):
    base = basename  # '_'.join([basename, compiler])
    if EW:
        base = base + '_EW'
    if ny > 1:
        base = base + '_mom' # momentum transport
    if Config.debug is True:
        base = base + "_debug"
    snlev = str(nlev) + "L"
    sdx = str(dx).replace('.','') + 'km'  # 0.5 -> '05'
    scpl = 'nc' + str(ncpl)
    return "_".join([gcm_res, base, snlev, str(nx)+"x"+str(ny), sdx, scpl])


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
    elif "4" in str(res):  # ne4
        stopn = 20
        restn = 20
        wallclock = "04:00:00"
    elif "16" in str(res):  # ne16
        pass
    if ncpl > 100:
        wallclock = "08:00:00"
    if ncpl == 288:
        wallclock = "12:00:00"
        restn = 5
    return stopn, restn, wallclock


cam_namelist_hindcast = {
    "nhtfrq": "0,-24,-24",
    "mfilt": "1,30,30",
    "fincl2": "'T','Q','Z3','OMEGA','U','V','CLOUD'",
    "fincl3": "'TS','TMQ','PRECT','TREFHT','LHFLX','SHFLX',"
        "'FLNS','FLNT','FSNS','FSNT','FLUT',"
        "'CLDLOW','CLDMED','CLDHGH','CLDTOT',"
        "'U850','U200','V850','V200','OMEGA500',"
        "'LWCF','SWCF','PS','PSL','QAP:A','TAP:A','PRECC','PRECL'",
    "srf_flux_avg": "1",
    "se_ftype": "0",
    "se_nsplit": "5",
    "rsplit": "2",
    # "state_debug_checks": ".true."
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

for (nx, ny, dx, nlev, ncpl) in run_combos:
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
    BuildCase = runsp.Case(case_name=gen_case_name(gcm_res, compiler, nx, ny, dx, nlev, ncpl, basename=basename),
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
            new_cam_config_opts['-cppdefs'] = "'-DSP_DIR_NS -DAPPLY_POST_DECK_BUGFIXES'"
        else:
            new_cam_config_opts['-cppdefs'] = "'-DSP_ORIENT_RAND -DAPPLY_POST_DECK_BUGFIXES'"

        if nlev == 30:
            default_set="SP1_nlev30"
        else:
            default_set="SP1"
        BuildCase.set_cam_config_opts(test=trial_run, default_set=default_set,
                                      dict_pop=dict_pop,
                                      **new_cam_config_opts)
        BuildCase.xmlchanges('env_build.xml', test=trial_run,
                             DEBUG=str(Config.debug).upper())
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
    resub = 365 // stopn  # just for now ...
    resub = 90 // stopn
    resub = 0
    if trial_run is False:
        BuildCase.write_namelist_to_file()
        # update run-time options in xmlfiles:
        BuildCase.xmlchanges("env_run.xml", test=trial_run,
                           RUN_TYPE="startup",
                           RUN_STARTDATE="1999-12-01",
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
