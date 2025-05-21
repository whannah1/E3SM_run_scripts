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
do_clone = True
quick_test = False

compiler = "intel"

Config = runsp.Config(newcase=False, config=True, clean=True, build=True,
                      runsim=True, update_namelist=True, debug=True,
                      copyinit=True, testrun=trial_run, hindcast=True,
                      sp=True)

# EW orientation
gcm_res = ("ne30",)
crm_dx = (1,)  # in km
crm_nx = ("32",)


def gen_case_name(gcm_res, crm_dx, crm_nx):
    dx = str(crm_dx).replace('.', '') + 'km'
    return "_".join([gcm_res, "SP1_dbg2", compiler, crm_nx+"x1", dx])


# Set-up the clone cases
ref_case = {"ne16": "ACME_ZM_nlev72_ne16_nudge_above_pbl",
            "ne30": "ACME_ZM_CTL_ne30_nudge_above_pbl"}
ref_dates = [dt.datetime(2011, 3, 1) + dt.timedelta(days=x)
             for x in range(0, 185, 7)]
case_format = '%Y%m%d'
xml_format = '%Y-%m-%d'


def ncdata(date, ref_dir, ref_case):
    """Construct ncdata file name, assuming date = datetimeobject
    """
    ncfile = ref_case + ".cam.i." + date.strftime("%Y-%m-%d-00000.nc")
    return "'" + ref_dir + ncfile + "'"


def get_ref_date(date):
    """ Find reference date closest to input date
    """
    ref_date = min(ref_dates, key=lambda x: abs(x - date))
    return ref_date.strftime(xml_format)


cam_namelist_hindcast = {
    "nhtfrq": "-6,-6,-1,-6",
    # "nhtfrq": "1,1,1,1",
    "mfilt": "4,4,24,4",
    "fincl2": "'T','Q','Z3','OMEGA','U','V','CLOUD'",
    "fincl3": "'TS','TMQ','PRECT','TREFHT','LHFLX','SHFLX',"
        "'FLNS','FLNT','FSNS','FSNT','FLUT',"
        "'CLDLOW','CLDMED','CLDHGH','CLDTOT',"
        "'U850','U200','V850','V200','OMEGA500',"
        "'LWCF','SWCF','PS','PSL','QAP:A','TAP:A','PRECC','PRECL'",
    "fincl4": "'DTCORE:A','SPDT:A','SPDQ:A','PTTEND:A','PTEQ:A',"
        "'DTV:A','VD01:A','QRL:A','QRS:A','QAP:I','TAP:I',"
        "'SPQC','SPQI','SPQS','SPQR','SPQG','SPQPEVP'",
    "srf_flux_avg": "1",
    "state_debug_checks": ".true."
    }

# ===================================================
# Step 3: Let the games begin!
# ===================================================
# full list (deal with the rest of these later ...)
#ndays_to_run = {'20110430': 5,
#                '20110507': 5,
#                '20110510': 10,
#                '20110517': 11,
#                '20110519': 9,
#                '20110521': 7,
#                '20110523': 5,
#                '20110528': 6,
#                '20110530': 5,
#                '20110601': 6,
#                '20110605': 6,
#                '20110608': 5,
#                '20110612': 5,
#                '20110615': 5,
#                '20110618': 6,
#                '20110624': 6,
#                '20110630': 5,
#                '20110704': 5,
#                '20110710': 6,
#                '20110714': 6,
#                '20110719': 5,
#                '20110724': 6,
#                '20110728': 6,
#                '20110731': 5,
#                '20110804': 5,
#                '20110808': 5,
#                '20110812': 5,
#                '20110816': 6,
#                '20110823': 5,
#                '20110827': 5}

ndays_to_run = {'20110519': 9}
#tests_to_run = {'a3_mic0': (3, '.false.', 0),
#                'a3_mic1': (3, '.false.', 1),
#                'a3_uv_mic0': (3, '.true.', 0),
#                'a3_uv_mic1': (3, '.true.', 1),
#                'a0_mic0': (0, '.false.', 0)}
tests_to_run = {'ctl': (0, '.false.', 0),
                'a1_mic0': (1, '.false.', 0),
                'a1_mic1': (1, '.false.', 1),
                'a3_mic0': (3, '.false.', 0),
                'a3_mic1': (3, '.false.', 1),
                'a3_uv_mic0': (3, '.true.', 0),
                'a3_uv_mic1': (3, '.true.', 1)}
tests_to_run = {'a1_uv_mic1': (1, '.true.', 1)} # in orig, uv and mic1 shouldn't matter

for (res, dx, nx) in itertools.product(gcm_res, crm_dx, crm_nx):
    # set ntasks:
    if res == "ne16":
        ntasks = 1536
    elif res == "ne30":
        ntasks = 5400
    else:
        ntasks = None

    # ===================================================
    # Step 1: Build the executable:
    # ===================================================
    BuildCase = runsp.Case(case_name=gen_case_name(res, dx, nx),
                           res=res, compset="FC5AV1C-L", compiler=compiler, sp=True)
    
    if Config.newcase or Config.build or not BuildCase.is_build_complete():
        # (1) Create newcase
        if Config.newcase is True:
            BuildCase.create_newcase(test=trial_run)

        # (2a) Edit env_mach_pes.xml
        if Config.config is True:
            if Config.clean is True:
                BuildCase.setup(clean=True, test=trial_run)
            # specify additional env_mach_pes.xml as kwargs to config_env_mach_pes
            BuildCase.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=ntasks)

            # (2b) Case setup
            BuildCase.setup(test=trial_run)

        # (3a) Edit env_build.xml
        # (3b) Build case
        if Config.build is True:
            if Config.clean is True:
                BuildCase.build(clean=True, test=trial_run)

            BuildCase.set_cam_config_opts(test=trial_run, default_set="SP1",
                                          dict_pop=None,
                                          **{"-crm_nx": nx,
                                             "-crm_dx": str(dx * 1000),
                                             "-crm_dt": 5,
                                             "-microphys": "mg2",
                                             "-cppdefs": "'-DCRMACCEL -DSP_DIR_NS'"})
            BuildCase.xmlchanges('env_build.xml', test=trial_run,
                                 DEBUG=str(Config.debug).upper())
            BuildCase.build(test=trial_run)
    if not trial_run:
        if not BuildCase.is_build_complete():
            print 'Build failed for', BuildCase
            continue

    # ===================================================
    # Step 2: Prepare to create new cases that link to executable from Step 1.
    # ===================================================
    exeroot = BuildCase.Directory.bld_dir  # location of executable for runs
    ref_dir = ("/lustre/atlas/proj-shared/csc249/crjones/acme_hindcast_ics/"
               "nudge_erai_uv_above_pbl_"+res+"/")

    
    for testcase, tup in tests_to_run.iteritems():
        # case = '20110519'
        ndays = 5

        case_name = BuildCase.case_name + "_" + testcase
        # case_date = dt.datetime.strptime(case, case_format)

        #print "Case date: " + str(case_date)
        #ref_date = get_ref_date(case_date)
        #print "Ref date: " + str(ref_date)

        # ensure all details of RunCase and BuildCase are same except for name
        RunCase = runsp.Case(case_name=case_name, res=BuildCase.res,
                             sp=BuildCase.sp,
                             compset=BuildCase.compset)

        # extreme cleaning -- delete the cloned cases
        if Config.clean is True:
            RunCase.delete(test=trial_run)

        # clone the case:
        if do_clone:
            RunCase.create_clone(BuildCase, test=trial_run)

        # Update namelist for standard hindcast run:
        if Config.update_namelist is True:
            RunCase.update_namelist(**cam_namelist_hindcast)
            # since chem matters now ...
            # RunCase.update_namelist(**runsp.cam_namelist_for_acme)
            # initial condition
            RunCase.update_namelist(srf_flux_avg='1',
                                    use_crm_accel='.true.',
                                    crm_accel_factor=str(tup[0]),
                                    crm_accel_uv=str(tup[1]),
                                    crm_accel_micro_opt=str(tup[2]),
                                    state_debug_checks='.true.')
            if testcase == 'ctl':
                RunCase.update_namelist(use_crm_accel='.false.')
        print "Current namelist"
        print RunCase.namelist
        print RunCase.Directory.cam_namelist_file
        if trial_run is False:
            RunCase.write_namelist_to_file()

        # user_nl_clm needs updating too ...
        #lnd_namelist = {"fsurdat": "'/lustre/atlas/world-shared/cli900/cesm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr1850_c130927.nc'"}
        #lnd_filename = RunCase.Directory.case_dir + "/user_nl_clm"
        #if trial_run is False:
        #    RunCase.write_namelist_to_file(filename=lnd_filename, namelist=lnd_namelist, write_option="a")

        # update run-time options in xmlfiles:
        RunCase.xmlchanges("env_run.xml", test=trial_run,
                           STOP_OPTION="ndays",
                           STOP_N=str(ndays),
                           RESUBMIT="0",
                           CONTINUE_RUN=str(Config.continue_run).upper(),
                           INFO_DBUG="1"
                           )

        if res == "ne16":
            wall_time = "02:00:00"
        else:
            wall_time = "04:00:00"
        RunCase.xmlchanges("env_batch.xml", test=trial_run,
                           JOB_WALLCLOCK_TIME=wall_time)

        # Submit the case
        if Config.runsim is True:
            RunCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
