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
clean_clone = True
quick_test = False

Config = runsp.Config(newcase=False, config=True, clean=True, build=True,
                      runsim=True, update_namelist=True, debug=True,
                      copyinit=True, testrun=trial_run, hindcast=True,
                      sp=True)

compiler = 'intel'
gcm_res = "ne30"
res = gcm_res  # to make sure I didn't miss anything 
# (nx, ny, dx, EW)
# run_combos = [(64, 1, 2, False), (8, 8, 2, False), (64, 1, 2, True), (256, 1, 1, False), (16, 16, 1, False)]
# run_combos = [(8, 8, 2, False), (16, 16, 1, False)]
run_combos = [(64, 1, 4, False)]
# run_combos = [(128, 1, 1, False)]

def gen_case_name(gcm_res, compiler, nx, ny, dx, EW):
    base = 'SP1_' + compiler
    if EW:
        base = base + '_EW'
    if ny > 1:
        base = base + '_mom' # momentum transport
    if Config.debug is True:
        base = base + "_debug"
    sdx = str(dx).replace('.','') + 'km'  # 0.5 -> '05'
    return "_".join([gcm_res, base, str(nx)+"x"+str(ny), sdx])

ref_dir = ("/lustre/atlas/proj-shared/cli115/crjones/e3sm_hindcast_ics/"
           "nuv04p2.ne30/")
ref_case = "nuv04p2.ne30"

case_format = '%Y%m%d'
xml_format = '%Y-%m-%d'


def ncdata(date, ref_dir, ref_case, model="cam"):
    """Construct ncdata file name, assuming date = datetimeobject
    """
    ncfile = ".".join([ref_case, model, "i", date.strftime("%Y-%m-%d-00000.nc")])
    return "'" + ref_dir + ncfile + "'"


cam_namelist_hindcast = {
    "nhtfrq": "0,-1,-1,-1,-1",
    "mfilt": "1,24,24,24,1",
    "fincl2": "'T','Q','Z3','OMEGA','U','V','CLOUD'",
    "fincl3": "'TS','TMQ','PRECT','TREFHT','LHFLX','SHFLX',"
        "'FLNS','FLNT','FSNS','FSNT','FLUT',"
        "'CLDLOW','CLDMED','CLDHGH','CLDTOT',"
        "'U850','U200','V850','V200','OMEGA500',"
        "'LWCF','SWCF','PS','PSL','QAP:A','TAP:A','PRECC','PRECL'",
    "fincl4": "'DTCORE:A','SPDT:A','SPDQ:A','PTTEND:A','PTEQ:A',"
        "'DTV:A','VD01:A','QRL:A','QRS:A','QAP:I','TAP:I',"
        "'SPQC','SPQI','SPQS','SPQR','SPQG','SPQPEVP','PBLH'",
    "fincl5": "'CRM_U','CRM_V','CRM_W','CRM_T','CRM_QV','CRM_QC',"
        "'CRM_QI','CRM_PREC','CRM_QPI','CRM_QPC','CRM_QRS','CRM_QRL',"
        "'PRECT','T','Z3','PHIS'",
    "fincl5lonlat": "'115w:80w_25n:65n'",
    "srf_flux_avg": "1",
    "state_debug_checks": ".true."
    }

# ===================================================
# Step 3: Let the games begin!
# ===================================================
ndays_to_run = {'20110430': 5,
                '20110507': 5,
                '20110510': 10,
                '20110517': 11,
                '20110519': 9,
                '20110521': 7,
                '20110523': 5,
                '20110528': 6,
                '20110530': 5,
                '20110601': 6,
                '20110605': 6,
                '20110608': 5,
                '20110612': 5,
                '20110615': 5,
                '20110618': 6,
                '20110624': 6,
                '20110630': 5,
                '20110704': 5,
                '20110710': 6,
                '20110714': 6,
                '20110719': 5,
                '20110724': 6,
                '20110728': 6,
                '20110731': 5,
                '20110804': 5,
                '20110808': 5,
                '20110812': 5,
                '20110816': 6,
                '20110823': 5,
                '20110827': 5}
# quick hack to run subset of hindcasts
ndays_to_run = {'20110519': 9}

for (nx, ny, dx, EW) in run_combos:
    if res == "ne16":
        ntasks = 1536
        ndyn = 1536
    elif res == "ne30":
        ntasks = 5400
        ndyn = 5400
    else:
        ntasks = None
        ndyn = None
    if nx * ny > 150: # use more processes! 
        ntasks = 21600

    # ===================================================
    # Step 1: Build the executable:
    # ===================================================
    BuildCase = runsp.Case(case_name=gen_case_name(gcm_res, compiler, nx, ny, dx, EW),
                           res=gcm_res,
                           compiler=compiler,
                           compset="FC5AV1C-04P2",
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
        if ny > 1:  # 3D case
            new_cam_config_opts['-cppdefs'] = "'-DCRM3D -DSPMOMTRANS'" 
        elif not EW:
            new_cam_config_opts['-cppdefs'] = "'-DSP_DIR_NS -DCRJONESDEBUG'"

        BuildCase.set_cam_config_opts(test=trial_run, default_set="SP1", dict_pop=['-cppdefs'],
                                      **new_cam_config_opts)
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
    for case, ndays in ndays_to_run.iteritems():
        case_name = BuildCase.case_name + "_" + case
        case_date = dt.datetime.strptime(case, case_format)

        print "Case date: " + str(case_date)
        ref_date = case_date.strftime(xml_format)
        print "Ref date: " + str(ref_date)

        # ensure all details of RunCase and BuildCase are same except for name
        RunCase = runsp.Case(case_name=case_name, res=BuildCase.res,
                             sp=BuildCase.sp,
                             compset=BuildCase.compset)

        # extreme cleaning -- delete the cloned cases
        if Config.clean is True or clean_clone:
            RunCase.delete(test=trial_run)

        # clone the case:
        if do_clone:
            RunCase.create_clone(BuildCase, test=trial_run)

        # Update namelist for standard hindcast run:
        if Config.update_namelist is True:
            RunCase.update_namelist(**cam_namelist_hindcast)
            RunCase.update_namelist(ncdata=ncdata(case_date, ref_dir, ref_case))

            # clm:
            clm_nl = {'finidat': ncdata(case_date, ref_dir, ref_case, model='clm')}
            clm_nl_fname = RunCase.Directory.case_dir + "/user_nl_clm"

        print "Current namelist"
        print RunCase.namelist
        print RunCase.Directory.cam_namelist_file
        if trial_run is False:
            RunCase.write_namelist_to_file()
            RunCase.write_namelist_to_file(filename=clm_nl_fname, namelist=clm_nl)
            user_file_loc = "/lustre/atlas/proj-shared/cli115/crjones/e3sm_hindcast_ics/CAPT/"
            RunCase.copy_to_casedir(user_file_loc+"user_nl_cice", test=trial_run)
            RunCase.copy_to_casedir(user_file_loc+"user_nl_docn", test=trial_run)
            RunCase.copy_to_casedir(user_file_loc+"user_docn.streams.txt.prescribed", test=trial_run)

            # update run-time options in xmlfiles:
            RunCase.xmlchanges("env_run.xml", test=trial_run,
                               RUN_TYPE="startup",
                               RUN_REFDIR="'"+ref_dir+"'",
                               REST_OPTION="nsteps",
                               REST_N="90",
                               GET_REFCASE="FALSE",
                               RUN_REFCASE=ref_case,
                               RUN_REFDATE=ref_date,
                               RUN_STARTDATE=case_date.strftime(xml_format),
                               STOP_OPTION="ndays",
                               STOP_N=str(ndays),
                               RESUBMIT="0",
                               CONTINUE_RUN=str(Config.continue_run).upper(),
                               INFO_DBUG="1",
                               ATM_NCPL="96"
                               )

        if ndays < 7:
            wall_time = "04:00:00"
        else:
            wall_time = "06:00:00"
        if ntasks > 20000:
            wall_time = "12:00:00"
            if ndays < 10:
                wall_time = "10:00:00"
            if ndays < 6:
                wall_time = "07:00:00"
        if nx == 128:
            wall_time = "06:00:00"
            if ndays > 7:
                wall_time = "12:00:00"
        if nx * ny < 64:
            wall_time = "04:00:00"
        RunCase.xmlchanges("env_batch.xml", test=trial_run,
                           JOB_WALLCLOCK_TIME=wall_time)

        # Submit the case
        if Config.runsim is True:
            RunCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
