#!/usr/bin/env python
#============================================================================================================================
#   Jan, 2017   Walter Hannah    Lawrence Livermore National Lab
#   Automated ECP testing procesdure
#============================================================================================================================
import sys
import os
import datetime
home = os.getenv("HOME")
host = os.getenv("HOST")
if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"
#============================================================================================================================
#============================================================================================================================
if host == "titan"  : project = "cli115"
# if host == "titan"  : project = "csc249"
if host == "edison" : project = "acme"

src_dir = home+"/E3SM/E3SM_SRC_master"
# src_dir = home+"/E3SM/E3SM_SRC1"
# src_dir = home+"/E3SM/E3SM_SRC2"

generate = True         # generate baselines
verbose  = False         # print commands

debug_script = False     # do not submit test - for debugging this script
debug_test   = False     # submit test with debug options

# tests = ["e3sm_ecp"]

tests = ["ERP_Ln9.ne4_ne4.F-EAMv1-AQP1"  \
        ,"SMS_Ld1.ne4_ne4.F-EAMv1-AQP1"]

### list of tests to run as a batch
# tests = ["ERP_Ld11.ne4_oQU240.A_WCYCL2000"    \
#         ,"ERP_Ld5.ne4_ne4.FC5AV1C-L"          \
#         ,"ERP_Ld5.ne30_ne30.FC5AV1C-L"        \
#         ,"ERS_Ld5.ne30_ne30.FC5AV1C-L"        \
#         ,"ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST"    \
#         ,"ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST"    \
#         ,"ERP_Ld3_P96.ne4_ne4.FSP2V1-TEST"    \
#         ]

### non-SP tests only
# tests = ["ERP_Ld5.ne30_ne30.FC5AV1C-L"      \
#         ,"ERP_Ld5.ne4_ne4.FC5AV1C-L"        \
#         ,"ERP_Ld11.ne4_oQU240.A_WCYCL2000"  \
#         ,"ERS_Ld5.ne30_ne30.FC5AV1C-L"      \
#         ]


### SP tests only
# tests = ["ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST"  \
#         ,"ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST"  \
#         ,"ERP_Ld3_P96.ne4_ne4.FSP2V1-TEST"  \
#         ]

# tests = [ "ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST", "ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERP_Ln5_P96.ne4_ne4.FSP1V1-TEST", "ERS_Ln5_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERS_Ln5_P96.ne4_ne4.FSP1V1-TEST" ]


### Individual tests
# tests = [ "ERP_Ld5.ne30_ne30.FC5AV1C-L" ]
# tests = [ "ERS_Ld5.ne30_ne30.FC5AV1C-L" ]

# tests = [ "ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERS_Ld3_P96.ne4_ne4.FSP2V1-ECPP-TEST" ]

# tests = [ "ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERP_Ld3_P96.ne4_ne4.FSP2V1-TEST" ]
# tests = [ "ERP_Ld3_P96.ne4_ne4.SP2V1-ECPP-TEST" ]


# tests = [ "ERP_Ld5.ne4_ne4.FC5AV1C-L" ]
# tests = [ "ERP_Ld5.ne30_ne30.FC5AV1C-L" ]
# tests = [ "ERS_Ld5.ne30_ne30.FC5AV1C-L" ]
# tests = [ "ERP_Ld11.ne4_oQU240.A_WCYCL2000" ]
# tests = [ "ERP_Ld31.ne4_oQU240.A_WCYCL2000","ERP_Ld11.ne4_oQU240.A_WCYCL2000" ]
# tests = [ "ERP_Ld11.ne4_oQU240.A_WCYCL2000" ]
# tests = [ "ERS_Ln9.ne4_ne4.FC5AV1C-L.titan_pgi" ]

# tests = [ "ERS_Ld3_P96.ne4_ne4.FSP1V1-TEST" ]
# tests = [ "ERP_Ld3_P96.ne4_ne4.FSP2V1-TEST" ]

#============================================================================================================================
#============================================================================================================================
if debug_script : verbose = True

now = datetime.datetime.utcnow()
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)

print("\n"+timestamp+"")

case_dir = home+"/E3SM/test_cases/"+timestamp

if generate : case_dir = case_dir+"_baseline"

for test in tests :

    if debug_test : 
        test = test.replace("ERP_","ERP_D_")
        test = test.replace("ERS_","ERS_D_")
        test = test.replace("SMS_","SMS_D_")

    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+"/"+timestamp+"."+test+".log"

    if generate :
        mode = " --generate "
        # Check for previous baseline direcory
        # if os.path.isdir(dst_dir) :
    else :
        mode = " -c "
    
    cmd = "nohup "+src_dir+"/cime/scripts/create_test "+mode+"  "+test+" --test-root "+case_dir+"   --project "+project+" --wait "
    
    #--------------------------------------------
    # Machine-specific configurations
    #--------------------------------------------
    # if host=="titan" : cmd = cmd+" --compiler pgi "
    if host=="titan" : cmd = cmd+" --compiler intel "
    if host=="titan" and project=="cli115" : cmd = cmd + " --baseline-root /lustre/atlas/proj-shared/cli115/hannah6/E3SM/baselines "

    ### use regular queue for debug run since they need a longer wall clock limit
    if host=="edison" : 
        if debug_test :
            cmd = cmd+" --queue regular "
        else :
            cmd = cmd+" --queue debug "

    #--------------------------------------------
    #--------------------------------------------
    
    if generate : 
        cmd = cmd + " --allow-baseline-overwrite "
    else :
        cmd = cmd + " -b master "

    # if debug_test : cmd = cmd+" --walltime 04:00:00 "    # Cannot use a wall clock time more than 2 hours on Titan

    cmd = cmd+" --walltime 02:00:00 "
    # if host=="titan"  : cmd = cmd+" --walltime 02:00:00 "
    # if host=="edison" : cmd = cmd+" --time 02:00:00 "

    # cmd = cmd+" --force-procs 96 "

    cmd = cmd+"  >& "+log_file+" &"

    ### print the command for starting the test
    if verbose : print("\n"+cmd+"")

    ## submit the test
    if not debug_script : os.system(cmd)

print
#============================================================================================================================
#============================================================================================================================

# --baseline-root $REG_HOME/baselines ERP_Ld31.ne4_ne4.FC5AV1C
# cmd = src_dir+"/cime/scripts/create_test -r "+home+"E3SM/test_cases --force-procs 32  -g -p "+project+"  >& "+log_file+" &"

# if host == "titan"  : cmd = cmd+" --force-procs 32 "
# if host == "edison" : cmd = cmd+" --force-procs 24 "
