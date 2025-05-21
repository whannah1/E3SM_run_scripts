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
do_clone = False
quick_test = False

ndays = 20
hannah_config = {'-rad': 'rrtmg',
                 '-nlev': '72',
                 '-crm_nz': '58',
                 '-crm_adv': 'MPDATA',
                 '-crm_nx': '32',
                 '-crm_ny': '1',
                 '-crm_dx': 1000,
                 '-crm_dt': 5,
                 '-SPCAM_microp_scheme': 'sam1mom',
                 '-microphys': 'mg2',
                 '-crm_nx_rad': 8,
                 '-crm_ny_rad': 1,
                 '-chem': 'linoz_mam4_resus_mom_soag',
                 '-rain_evap_to_coarse_aero': None,
                 '-bc_dep_to_snow_updates': None,
                 '-cppdefs': "'-DSP_DIR_NS  -DSP_TK_LIM'"
                 }

case_mods = {'ACME_SP1_CTL_ne30_32x1_0.5km_00': {"-crm_dx": 500}}
ref_dates = {'ACME_SP1_CTL_ne30_32x1_0.5km_00': "2000-02-20"}

default_config = {'-rad': 'rrtmg',
                  '-nlev': '72',
                  '-crm_nz': '58',
                  '-crm_adv': 'MPDATA',
                  '-crm_nx': '32',
                  '-crm_ny': '1',
                  '-crm_dx': 1000,
                  '-crm_dt': 10,
                  '-SPCAM_microp_scheme': 'sam1mom',
                  '-microphys': 'mg2',
                  '-chem': 'linoz_mam4_resus_mom_soag',
                  '-rain_evap_to_coarse_aero': None,
                  '-bc_dep_to_snow_updates': None,
                  '-cppdefs': "'-DSP_DIR_NS'"
                  }


# ===================================================
# Step 1: Build the executable:
# ===================================================
Config = runsp.Config(newcase=True, config=True, clean=False, build=True,
                      runsim=True, update_namelist=True, debug=False,
                      copyinit=True, testrun=trial_run, hindcast=False,
                      sp=True)

for casename, config_opts in case_mods.iteritems():
    Case = runsp.Case(case_name=casename,
                      res="ne30", compset="FC5AV1C-L", sp=Config.sp, compiler="pgi")

    # (1) Create newcase
    if Config.newcase is True:
        Case.create_newcase(test=trial_run)

    # (2a) Edit env_mach_pes.xml
    if Config.config is True:
        if Config.clean is True:
            Case.setup(clean=True, test=trial_run)
        # specify additional env_mach_pes.xml as kwargs to config_env_mach_pes
        Case.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=5400)

        # (2b) Case setup
        Case.setup(test=trial_run)

    # (3a) Edit env_build.xml
    # (3b) Build case
    if Config.build is True:
        if Config.clean is True:
            Case.build(clean=True, test=trial_run)

        cam_config = hannah_config.copy()
        cam_config.update(**config_opts)

        Case.set_cam_config_opts(test=trial_run, default_set="SP1",
                                 **cam_config)
        Case.xmlchanges('env_build.xml', test=trial_run,
                        DEBUG=str(Config.debug).upper())
        Case.build(test=trial_run)

    # ===================================================
    # Step 2: Prepare to create new cases that link to executable from Step 1.
    # ===================================================
    exeroot = Case.Directory.bld_dir  # location of executable for runs
    ref_dir = "/lustre/atlas/proj-shared/cli115/hannah6/ACME/"+casename+"/rest/"
    ref_case = casename
    ref_date = ref_dates[casename]

    cam_debug_namelist = {
        "nhtfrq": "0,1,1,1",
        "mfilt": "1,48,48,48",
        "fincl2": "'T','Q','Z3','OMEGA','U','V','CLOUD'",
        "fincl3": "'TS','TMQ','PRECT','TREFHT','LHFLX','SHFLX',"
            "'FLNS','FLNT','FSNS','FSNT','FLUT',"
            "'CLDLOW','CLDMED','CLDHGH','CLDTOT',"
            "'U850','U200','V850','V200','OMEGA500',"
            "'LWCF','SWCF','PS','PSL','QAP:I','TAP:I','PRECC','PRECL'",
        "fincl4": "'DTCORE:I','SPDT:I','SPDQ:I','PTTEND:I','PTEQ:I',"
            "'DTV:I','VD01:I','QRL:I','QRS:I','QAP:I','TAP:I',"
            "'SPQC','SPQI','SPQS','SPQR','SPQG','SPQPEVP'",
        "srf_flux_avg": "1"
        }

    if Config.update_namelist is True:
        Case.update_namelist(**cam_debug_namelist)

        print "Current namelist"
        print Case.namelist
        print Case.Directory.cam_namelist_file
        if trial_run is False:
            Case.write_namelist_to_file()

    # update run-time options in xmlfiles:
    Case.xmlchanges("env_run.xml", test=trial_run,
                    RUN_TYPE="branch",
                    RUN_REFDIR="'"+ref_dir+"'",
                    REST_OPTION="ndays",
                    REST_N="10",
                    GET_REFCASE="FALSE",
                    RUN_REFCASE=ref_case,
                    RUN_REFDATE=ref_date,
                    RUN_STARTDATE=ref_date,
                    STOP_OPTION="ndays",
                    STOP_N=str(ndays),
                    RESUBMIT="0",
                    CONTINUE_RUN="TRUE"
                   )
    if Config.copyinit:
        restart_dir = ref_dir
        rpointer_dir = ref_dir
        Case.copy_refcase_to_rundir(restart_dir, ref_date, test=trial_run,
                                    ref_case=ref_case, rm_cam_rest=False)
        # need to copy history files h1, h2 as well:
        Case.copy_refcase_to_rundir(restart_dir, ref_date, test=trial_run,
                                    ref_case=ref_case, rm_cam_rest=False,
                                    pat="*cam.h[12]*")
        Case.copy_rpointers_to_rundir(rpointer_dir, ref_date, test=trial_run)

    Case.xmlchanges("env_batch.xml", test=trial_run,
                    JOB_WALLCLOCK_TIME="06:00:00")

    # Submit the case
    if Config.runsim is True:
        Case.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'fail', '-M', 'end')
