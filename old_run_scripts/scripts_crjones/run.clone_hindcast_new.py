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

trial_run = False
do_clone = True
quick_test = False

# ===================================================
# Step 1: Build the executable:
# ===================================================
Config = runsp.Config(newcase=True, config=True, clean=False, build=True,
                      runsim=True, update_namelist=True, debug=False,
                      copyinit=False, testrun=trial_run, hindcast=True,
                      sp=True, continue_run=False)

BuildCase = runsp.Case(case_name="ne30_new_SP1_64x1_1km", res="ne30", sp=Config.sp,
                       compiler="pgi", compset="FC5AV1C-04P2")

# (1) Create newcase
if Config.newcase is True:
    BuildCase.create_newcase(test=trial_run)

# (2a) Edit env_mach_pes.xml
if Config.config is True:
    if Config.clean is True:
        BuildCase.setup(clean=True, test=trial_run)
    # specify additional env_mach_pes.xml as kwargs to config_env_mach_pes
    BuildCase.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=5400, num_dyn=5400)

    # (2b) Case setup
    BuildCase.setup(test=trial_run)

# (3a) Edit env_build.xml
# (3b) Build case
if Config.build is True:
    if Config.clean is True:
        BuildCase.build(clean=True, test=trial_run)

    BuildCase.set_cam_config_opts(test=trial_run, default_set="SP1",
                                  **{"-crm_nx": "64", "-crm_dx": "1000",
                                     "-crm_dt": "5", "-microphys": "mg2"})
    BuildCase.xmlchanges('env_build.xml', test=trial_run,
                         DEBUG=str(Config.debug).upper(),
                         CALENDAR="'GREGORIAN'")
    BuildCase.build(test=trial_run)

# ===================================================
# Step 2: Prepare to create new cases that link to executable from Step 1.
# ===================================================
exeroot = BuildCase.Directory.bld_dir  # location of executable for runs
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
        "'SPQC','SPQI','SPQS','SPQR','SPQG','SPQPEVP'",
    "fincl5": "'CRM_U','CRM_V','CRM_W','CRM_T','CRM_QV','CRM_QC',"
        "'CRM_QI','CRM_PREC','CRM_QPI','CRM_QPC','CRM_QRS','CRM_QRL',"
        "'PRECT','T'",
    "fincl5lonlat": "'110w:80w_25n:45n'",
    "srf_flux_avg": "1"
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
if quick_test:
    ndays_to_run = {'20110401': 5}  # simple test run
for case, ndays in ndays_to_run.iteritems():
    case_name = BuildCase.case_name + "_" + case
    case_date = dt.datetime.strptime(case, case_format)

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
                       REST_OPTION="none",
                       GET_REFCASE="FALSE",
                       RUN_REFCASE=ref_case,
                       RUN_REFDATE=case_date.strftime(xml_format),
                       RUN_STARTDATE=case_date.strftime(xml_format),
                       STOP_OPTION="ndays",
                       STOP_N=str(ndays),
                       RESUBMIT="0",
                       CONTINUE_RUN=str(Config.continue_run).upper(),
                       INFO_DBUG="2"
                       )
    if Config.copyinit:
        restart_dir = ref_dir + "archive/restart/"
        rpointer_dir = ref_dir + "archive/"
        RunCase.copy_refcase_to_rundir(restart_dir, ref_date, test=trial_run,
                                       ref_case=ref_case, rm_cam_rest=True)
        RunCase.copy_rpointers_to_rundir(rpointer_dir, ref_date, test=trial_run)

    if ndays <= 6:
        wall_time = "04:00:00"
    else:
        wall_time = "06:00:00"
    RunCase.xmlchanges("env_batch.xml", test=trial_run,
                       JOB_WALLCLOCK_TIME=wall_time)

    # Submit the case
    if Config.runsim is True:
        RunCase.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
