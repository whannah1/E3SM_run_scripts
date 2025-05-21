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

Config = runsp.Config(newcase=True, config=True, clean=False, build=True,
                      runsim=True, update_namelist=True, debug=True,
                      copyinit=True, testrun=trial_run, hindcast=True,
                      sp=True)

compiler = 'intel'
gcm_res = "ne30"
res = gcm_res  # to make sure I didn't miss anything 
# (nx, ny, dx, nlev, ncpl)
# run_combos = [(32, 1, 4, 30, 12), (32, 1, 4, 72, 12), (32, 1, 4, 30, 48), (32, 1, 4, 72, 48)]
# run_combos = [(32, 1, 4, 30, 48), (32, 1, 4, 72, 48)]
run_combos = [(64, 1, 4, 72, 48)]

def gen_case_name(gcm_res, compiler, nx, ny, dx, nlev, EW=False, base_prefix='SP1'):
    base = "_".join([base_prefix, compiler])
    if EW:
        base = base + '_EW'
    if ny > 1:
        base = base + '_mom' # momentum transport
    if Config.debug is True:
        base = base + "_debug"
    snlev = str(nlev) + "L"
    sdx = str(dx).replace('.','') + 'km'  # 0.5 -> '05'
    return "_".join([gcm_res, base, snlev, str(nx)+"x"+str(ny), sdx])

# configure this to get timestep by timestep output:
cam_namelist_hindcast = {
    "nhtfrq": "0,1,1",
    "mfilt": "1,1,1",
    "fincl2": "'T','TpreCRM','TpostCRM','Q','Z3','OMEGA','U','V','CLOUD',"
        "'TS','TMQ','PRECT','TREFHT','LHFLX','SHFLX',"
        "'FLNS','FLNT','FSNS','FSNT','FLUT',"
        "'CLDLOW','CLDMED','CLDHGH','CLDTOT','CLDLIQ',"
        "'U850','U200','V850','V200','OMEGA500',"
        "'LWCF','SWCF','PS','PSL','QAP:A','TAP:A','PRECC','PRECL','TAUX','TAUY'",
    "fincl3": "'DTCORE:I','SPDT:I','SPDQ:I','PTTEND:I','PTEQ:I',"
        "'DTV:I','QRL:I','QRS:I','QAP:I','TAP:I',"
        "'SPQC','SPQI','SPQS','SPQR','SPQG','SPQPEVP',"
        "'SPDT','SPDQ','SPDQC','SPDQI','SPTLS','SPQTLS','SPPFLX','SPQTFLX','SPQPFLX','SPQPFALL',"
        "'CRM_U','CRM_V','CRM_W','CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_QPI','CRM_PREC'",
    "srf_flux_avg": "1",
    "state_debug_checks": ".true."
    }

for (nx, ny, dx, nlev, ncpl) in run_combos:
    if ncpl == 12:
        do_clone = False
        case_prefix = 'dt7200'
    elif ncpl == 48:
        # this is a cloned case
        do_clone = False
        case_prefix = 'dt1800'
    if gcm_res == "ne16":
        ntasks = 1536
        ndyn = 1536
    elif gcm_res == "ne30":
        ntasks = 5401
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
    BuildCase = runsp.Case(case_name=gen_case_name(gcm_res, compiler, nx, ny, dx, nlev, base_prefix=case_prefix),
                           res=gcm_res,
                           compiler=compiler,
                           compset="FC5AV1C-04P2",
                           sp=True)

    if do_clone:
        PreBuildCase = runsp.Case(case_name=gen_case_name(gcm_res, compiler, nx, ny, dx, nlev, base_prefix='dt7200'),
                                  res=gcm_res, compiler=compiler, compset="FC5AV1C-04P2", sp=True)
        BuildCase.delete(test=trial_run)
        BuildCase.create_clone(PreBuildCase, test=trial_run)

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
        new_cam_config_opts['-cppdefs'] = "'-DSP_DIR_NS -DCRJONESDEBUG -DAPPLY_POST_DECK_BUGFIXES'"

        if nlev == 30:
            default_set="SP1_nlev30"
        else:
            default_set="SP1"
        BuildCase.set_cam_config_opts(test=trial_run, default_set=default_set,
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

    stopn = 5 # 5 day simulation, expect most to crash
    resub = 1

    if trial_run is False:
        BuildCase.write_namelist_to_file()
        # update run-time options in xmlfiles:
        BuildCase.xmlchanges("env_run.xml", test=trial_run,
                           RUN_TYPE="branch",
                           RUN_STARTDATE="0001-12-01",
                           RUN_REFCASE="ne30_SP1_intel_72L_64x1_4km_nc48",
                           RUN_REFDATE="0002-06-01",
                           REST_OPTION="nsteps",
                           REST_N=str(4),
                           STOP_OPTION="ndays",
                           STOP_N=str(stopn),
                           RESUBMIT=str(resub),
                           ATM_NCPL=str(ncpl),
                           CONTINUE_RUN=str(Config.continue_run).upper(),
                           INFO_DBUG="1")
    wall_time = "06:00:00"
    BuildCase.xmlchanges("env_batch.xml", test=trial_run,
                       JOB_WALLCLOCK_TIME=wall_time)

    # Submit the case
    if Config.runsim is True:
        BuildCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
