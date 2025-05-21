#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:42:10 2018

@author: Chris Jones (christopher.jones@pnnl.gov)
"""

import runsp

trial_run = False   # if true, just print commands to screen
continue_run = False

# Case = runsp.Case(case_name="ne120_nudge_intel",
#                  compset='F20TRC5AV1C-H01A', # 'FC5AV1C-H01A", # 'FC5AV1C-L',
#                  res="ne120",
#                  compiler="intel",
#                  sp=False,
#                  top_dir="/ccs/home/crjones/dev/ACME/")

Case = runsp.Case(case_name="ACME_ne30_nudge_above_pbl",
                  compset='F20TRC5AV1C-04P2', # 'FC5AV1C-H01A", # 'FC5AV1C-L',
                  res="ne30",
                  compiler="pgi",
                  sp=False,
                  top_dir="/ccs/home/crjones/dev/ACME/")

# (1) Create newcase
# Case.create_newcase(test=trial_run)

# (2a) Edit env_mach_pes.xml (use defaults)
# Case.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=5400, num_dyn=5400)

# (2b) Case setup [env_mach_pes locked after this]
# Case.setup(clean=False, test=trial_run)

# (3) Edit env_build.xml and build
# Case.set_cam_config_opts(test=trial_run, default_set="SP1",
#                         **{"-nlev": "30", "-crm_nz": "28", "-microphys": "mg2"})
#
# Case.xmlchanges('env_build.xml', test=trial_run,
#                 CALENDAR="'GREGORIAN'")
#Case.build(clean=False, test=trial_run)

# (4a) Edit run options
Case.xmlchanges('env_run.xml', test=trial_run,
                RUN_STARTDATE="2011-03-01",
                REST_OPTION="ndays",
                REST_N="15",
                STOP_OPTION="ndays",
                STOP_N="185",
                RESUBMIT="0",
                CONTINUE_RUN=str(continue_run).upper())

# (4b) Edit batch options
Case.xmlchanges('env_batch.xml', test=trial_run,
                JOB_WALLCLOCK_TIME="6:00:00")

# (4c) Update namelist
cam_namelist_nudging = runsp.cam_namelist_for_nudging
cam_namelist_nudging.update({"Nudge_Path": "'/lustre/atlas/proj-shared/csc249/crjones/era-interim/ne30/'",
                             "Nudge_File_Template": "'regrid_IE_ne30.cam2.i.%y-%m-%d-%s.nc'",
                             "finidat": "'/lustre/atlas/world-shared/cli900/cesm/inputdata/lnd/clm2/initdata_map/I1850CLM45.ne30_oECv3.edison.intel.36b43c9.clm2.r.0001-01-06-00000_c20171023.nc'",
                             "flanduse_timeseries": "'/lustre/atlas/world-shared/cli900/cesm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4_hist_simyr1850_c20171102.nc'",
                             "fsurdat": "'/lustre/atlas/world-shared/cli900/cesm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr1850_2015_c171018.nc'"
                             })
                             #"se_nsplit": "6",
                             #"rsplit": "2", "qsplit": "1",
                             #"cld_macmic_num_steps": "3"})
Case.update_namelist(**cam_namelist_nudging)
# Case.write_namelist_to_file()

# (5) Submit the case
Case.submit(trial_run, '--mail-user', 'christopher.jones@pnnl.gov', '-M', 'end', '-M', 'fail')
