#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:42:10 2018

@author: Chris Jones (christopher.jones@pnnl.glv)
"""

import runsp

trial_run = False   # if true, print commands to screen without executing them

Case = runsp.Case(case_name="ne30_nlev72_merge_SP1_pgi_dbg_test",
                  compset="FC5AV1C-L",
                  res="ne30",
                  compiler="pgi",
                  top_dir="/ccs/home/crjones/merge/ACME-ECP/",
                  sp=True)

# (1) Create newcase
Case.create_newcase(test=trial_run)


# (2a) Edit env_mach_pes.xml
Case.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=5400, num_dyn=5400)

# (2b) Case setup [env_mach_pes locked after this]
Case.setup(clean=False, test=trial_run)

# (3) Edit env_build.xml and build
Case.set_cam_config_opts(test=trial_run, default_set="SP1",
                         **{"-microphys": "mg2", '-crm_nx': "32", '-crm_ny': "1"})
#                         **{"-nlev": "30", "-crm_nz": "28", "-microphys": "mg2"})
Case.xmlchanges('env_build.xml', test=trial_run,
                DEBUG="TRUE")
Case.build(clean=False, test=trial_run)


# (4a) Edit run options
Case.xmlchanges('env_run.xml', test=trial_run,
                STOP_N="5",
                STOP_OPTION="ndays",
                INFO_DBUG="1")

# (4b) Edit batch options
Case.xmlchanges('env_batch.xml', test=trial_run,
                JOB_WALLCLOCK_TIME="02:00:00")

# (4c) Update user_nl_cam namelist
# Case.update_namelist(nhtfrq="-1",
#                      mfilt="1")
Case.write_namelist_to_file()

# (5) Submit the case
Case.submit(test=trial_run)
