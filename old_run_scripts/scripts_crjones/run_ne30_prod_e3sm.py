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
quick_run = True

Config = runsp.Config(newcase=True, config=True, clean=False, build=True,
                      runsim=True, update_namelist=True, debug=False,
                      copyinit=True, testrun=trial_run, hindcast=True,
                      continue_run=False, sp=False)

compiler = 'intel'
gcm_res = "ne30"
basename = 'E3SM_rrtmgp'
top_dir = os.getenv('HOME') + '/repos/current/E3SM/'
res = gcm_res  # to make sure I didn't miss anything 
nlev = 72
ncpl = 48

def gen_case_name(gcm_res, compiler, nlev=72, ncpl=48, EW=False, basename='ZM'):
    # base = '_'.join([basename, compiler])
    base = basename
    if Config.debug is True:
        base = base + "_debug"
    snlev = str(nlev) + "L"
    scpl = 'nc' + str(ncpl)
    return "_".join([gcm_res, base, snlev, scpl])


def calc_stopn(res, nlev, ncpl):
    if "30" in str(res):  # ne30
        if nlev == 30:
            stopn = 180
            restn = 30
            wallclock = "06:00:00"
        else:
            stopn = 180
            restn = 30
            wallclock = "06:00:00"
    elif "4" in str(res):  # ne4
        pass
    elif "16" in str(res):  # ne16
        pass
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
    # "srf_flux_avg": "1",
    # "state_debug_checks": ".true."
    }

ntasks = 5401
ndyn = 5400

# ===================================================
# Step 1: Build the executable:
# ===================================================
BuildCase = runsp.Case(case_name=gen_case_name(gcm_res, compiler, nlev, ncpl, basename=basename),
                       res=gcm_res,
                       compiler=compiler,
                       compset="FC5AV1C-04P2",
                       top_dir=top_dir,
                       sp=False)

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
    BuildCase.set_cam_config_opts(test=trial_run, default_set='E3SM_RRTMGP')
    BuildCase.xmlchanges('env_build.xml', test=trial_run,
                         DEBUG=str(Config.debug).upper())
    BuildCase.build(test=trial_run)
if not trial_run:
    if not BuildCase.is_build_complete():
        raise Exception('Build failed for ' + BuildCase.case_name)

if Config.update_namelist is True:
    BuildCase.update_namelist(**cam_namelist_hindcast)
print "Current namelist"
print BuildCase.namelist
print BuildCase.Directory.cam_namelist_file

stopn, restn, wall_time = calc_stopn(gcm_res, nlev, ncpl)
resub = 2
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
wall_time = "06:00:00"
if quick_run:
    BuildCase.xmlchanges("env_run.xml", test=trial_run,
                         STOP_N="10",
                         REST_OPTION="none",
                         RESUBMIT="0")
    wall_time = "02:00:00"

BuildCase.xmlchanges("env_batch.xml", test=trial_run,
                     JOB_WALLCLOCK_TIME=wall_time)

# Submit the case
if Config.runsim is True:
    BuildCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
