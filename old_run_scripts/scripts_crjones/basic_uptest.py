#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:42:10 2018

@author: Chris Jones (christopher.jones@pnnl.glv)
"""

import runsp

trial_run = False   # if true, print commands to screen without executing them

Case = runsp.Case(case_name="ne120_upcam_intel_test",
                  compset="FC5AV1C-L",
                  res="ne120",
                  compiler="intel",
                  top_dir="/ccs/home/crjones/dev/ACME-ECP/",
                  sp=True)

# (1) Create newcase
# Case.create_newcase(test=trial_run)

# (2a) Edit env_mach_pes.xml
# Case.set_ntasks_in_env_mach_pes(test=trial_run, num_phys=5400, num_dyn=5400)

# (2b) Case setup [env_mach_pes locked after this]
# Case.setup(clean=False, test=trial_run)
#new_cam_config_opts = {"-crm_nx": '32', "-crm_ny": '1',
#                       "-crm_dx": str(250), "-crm_dt": str(1), 
#                       '-nlev': '125', '-crm_nz': '125', "-microphys": "mg2"}
# Case.set_cam_config_opts(test=trial_run, default_set="SP1", **new_cam_config_opts)
# Case.xmlchanges('env_build.xml', test=trial_run, DEBUG=str(Config.debug).upper())
# Case.build(test=trial_run, clean=False)

# (4a) Edit run options
Case.xmlchanges('env_run.xml', test=trial_run,
                RUN_STARTDATE="2008-10-07",
                START_TOD="43200",
                STOP_N="1",
                STOP_OPTION="ndays",
                INFO_DBUG="1",
                REST_N="1",
                REST_OPTION="ndays",
                RESUBMIT='1',
                CONTINUE_RUN='FALSE',
                ATM_NCPL='576')

# (4c) Update user_nl_cam namelist
Case.update_namelist(nhtfrq="0,-6,-1",
                     mfilt="1,4,24",
                     fincl2="'T','Q','PS','Z3','OMEGA','CLOUD'",
                     fincl3="'PS','SPQC','TS','TMQ','PRECL','PRECC','LHFLX','SHFLX','FLNS','FLNT','FSNS','FSNT','FLUT','OMEGA500','CLDLOW','CLDMED','CLDTOT','TGCLDLWP','TGCLDIWP', 'PBLH'",
                     srf_flux_avg="1",
                     dtime="150",
                     ncdata="'/lustre/atlas/proj-shared/cli115/crjones/upcam/regrid_EI_ne120.cam2.i.2008-10-07-43200.nc'")
Case.write_namelist_to_file()

# (4b) Edit batch options
Case.xmlchanges('env_batch.xml', test=trial_run,
                JOB_WALLCLOCK_TIME="12:00:00")

# (5) Submit the case
Case.submit(test=trial_run)
